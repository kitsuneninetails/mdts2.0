__author__ = 'tomoe'
# Copyright 2015 Midokura SARL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import subprocess
from VTM.VirtualTopologyConfig import VirtualTopologyConfig
from PTM.VMHost import VMHost
from common.CLI import LinuxCLI

class Host:
    """
    A class to wrap a VM from the Physical Topology Manager
    """

    def __init__(self, vtc, vm_host):
        self.vm_host = vm_host
        """ :type: VMHost"""
        self.vtc = vtc
        """ :type: VirtualTopologyConfig"""


    def plugin_vm(self, iface, port):
        """ Creates a pseudo VM based on netns for neutron port.
            This involves the following steps:
                1. create a netns with the same name as name
                2. create a veth pair
                3. stick vethB to the netns and configure (e.g. mac/ip adder)
                4. (if Host is running inside netns)
                      stick vethA to host's netns
                5. bind interface to MidoNet with mm-ctl

        :param name: name of VM: used for netns and net_device interface name
        :param port: Neutron Port data
        :param subnet: Neutron Subnet data
        :param setup_ip: configure ip addr and gw if True
        :returns VM instance
        """

        if self._vms.get(name):
            raise AssertionError('VM with the same name already exists')

        try:
            # configure mac address
            mac = port.get('port').get('mac_address')
            vm.execute('ip link set eth0 address %(mac)s' % {'mac': mac})

            # Now bind it to MidoNet
            port_id = port['port']['id']
            self._bind_port(port_id, name)

        except subprocess.CalledProcessError as e:
            print 'command output: ',   e.output
            raise
        else:
            return vm

    def delete_vm(self, name, port):
        """Deletes psedo VM

        :param name: name of the VM to delete
        """

        try:

            # delete veth pair
            cmdline = 'ip link del %s' % name
            subprocess.check_output(cmdline.split(), stderr=subprocess.STDOUT)

            # delete netns
            cmdline = 'ip netns del %s' % name
            subprocess.check_output(cmdline.split(), stderr=subprocess.STDOUT)

            # unbind MidoNet port
            port_id = port['port']['id']
            self._unbind_port(port_id)
        except subprocess.CalledProcessError as e:
            print 'command output: ',   e.output
            raise


    def _bind_port(self, port_id, ifname):

        cmdline = ''
        if self._netns:
            cmdline += 'ip netns exec %s" % self._netns '
        cmdline += 'mm-ctl --bind-port %(port_id)s %(ifname)s' % {
            'port_id': port_id, 'ifname': ifname}
        subprocess.check_output(cmdline.split(), stderr=subprocess.STDOUT)


    def _unbind_port(self, port_id):
        cmdline = ''
        if self._netns:
            cmdline += 'ip netns exec %s" % self._netns '
        cmdline += 'mm-ctl --unbind-port %s' % port_id
        subprocess.check_output(cmdline.split(), stderr=subprocess.STDOUT)


    def execute(self, cmdline, timeout=None):
        """Executes cmdline inside VM

        Args:
            cmdline: command line string that gets executed in this VM
            timeout: timeout in second

        Returns:
            output as a bytestring


        Raises:
            subprocess.CalledProcessError: when the command exists with non-zero
                                           value, including timeout.
            OSError: when the executable is not found or some other error
                     invoking
        """

        LOG.debug('VM: executing command: %s', cmdline)


        cmdline = "ip netns exec %s %s" % (
            self._name, ('timeout %d ' % timeout if timeout else "")  + cmdline)

        try:
            result = subprocess.check_output(cmdline, shell=True)
            LOG.debug('Result=%r', result)
        except subprocess.CalledProcessError as e:
            print 'command output: ',   e.output
            raise

        return result


    def expect(self, pcap_filter_string, timeout):
        """
        Expects packet with pcap_filter_string with tcpdump.
        See man pcap-filter for more details as to what you can match.


        Args:
            pcap_filter_string: capture filter to pass to tcpdump
                                See man pcap-filter
            timeout: in second

        Returns:
            True: when packet arrives
            False: when packet doesn't arrive within timeout
        """

        count = 1
        cmdline = 'timeout %s tcpdump -n -l -i eth0 -c %s %s 2>&1' % (
            timeout,
            count, pcap_filter_string)

        try:
            output = self.execute(cmdline)
            retval = True
            for l in output.split('\n'):
                LOG.debug('output=%r', l)
        except subprocess.CalledProcessError as e:
            print 'OUTPUT: ', e.output
            LOG.debug('expect failed=%s', e)
            retval = False
        LOG.debug('Returning %r', retval)
        return retval

    def send_arp_request(self, target_ipv4):
        cmdline = 'mz eth0 -t arp "request, targetip=%s"' % target_ipv4
        LOG.debug("cmdline: %s" % cmdline)
        return self.execute(cmdline)

    def send_arp_reply(self, src_mac, target_mac, src_ipv4, target_ipv4):
        arp_msg = '"' + "reply, smac=%s, tmac=%s, sip=%s, tip=%s" % \
                        (src_mac, target_mac, src_ipv4, target_ipv4) + '"'
        mz_cmd = ['mz', 'eth0', '-t', 'arp', arp_msg]
        return self.execute(mz_cmd)

    def clear_arp(self):
        cmdline = 'ip neigh flush all'
        LOG.debug('VM: flushing arp cache: ' + cmdline)
        self.execute(cmdline)

    def set_ifup(self):
        return self.execute('ip link set eth0 up')

    def set_ifdown(self):
        return self.execute('ip link set eth0  down')

    def set_ipv4_addr(self, ipv4_addr):
        return self.execute('ip addr add %s dev eth0' % ipv4_addr)

    def set_ipv4_gw(self, gw):
        return self.execute('ip route add default via %s' % gw)

    def assert_pings_to(self, other, count=3):
        """
        Asserts that the sender VM can ping to the other VM

        :param other: ping target VM instance
        """


        sender = self._port['port'].get('fixed_ips')
        receiver = other._port['port'].get('fixed_ips')
        if sender and receiver:
            receiver_ip = receiver[0]['ip_address']
            try:
                self.execute('ping -c %s %s' % (count, receiver_ip))
            except:
                raise AssertionError(
                    'ping from %s to %s failed'% (self, other))

    def  __repr__(self):
        return 'VM(%s)(port_id=%s)' % (self._name, self._port['port']['id'])



