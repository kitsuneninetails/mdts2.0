__author__ = 'micucci'

import unittest


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


from VTM.Host import Host
from VTM.VirtualTopologyConfig import VirtualTopologyConfig
from VTM.tests.VirtualTopologyConfigTest import MockClient
from PTM.VMHost import VMHost
from PTM.ComputeHost import ComputeHost
from PTM.RootServer import RootServer
from VTM.Network import Network
import logging
import datetime

class MockNetwork(Network):



class MyTestCase(unittest.TestCase):
    def __init__(self):
        super(MyTestCase, self).__init__()
        self.hosts = [Host()]
        self.vtc = VirtualTopologyConfig(client_api_impl=MockClient)

    def test_host_plugin_vm(self):
        api_passthrough = self.vtc.get_client()
        test_system = RootServer()
        test_system.config_compute('cmp1', {'iface': 'eth0', 'ips': ['2.2.2.2', '32']})
        test_system.config_vm('cmp1', 'vm1', [{'iface': 'eth0', 'ips': ['3.3.3.3', '32']}])
        hv = test_system.get_host('cmp1')
        """ :type: ComputeHost"""
        vm = hv.get_vm('vm1')


        virtual_host = Host(self.vtc, vm)
        virtual_network = MockNetwork()

        virtual_host.plugin_vm()


        h._bind_port = lambda bp: True
        h._unbind_port = lambda ubp: True

        mac = 'fa:16:3e:68:a7:df'
        ip_addr = '1.1.1.2'
        port = {'port': {
            'status': 'ACTIVE',
            'binding:host_id': None,
            'name': '',
            'admin_state_up': True,
            'network_id': '0c05d77e-96ce-4e04-841b-5a07b7815c8a',
            'tenant_id': 'devilman-2015-03-08 12:19:59',
            'binding:vif_details': {'port_filter': True},
            'binding:vnic_type': 'normal',
            'binding:vif_type': 'midonet',
            'device_owner': '',
            'mac_address': mac,
            'fixed_ips': [
                {'subnet_id': '74ad2fcd-7a95-4b59-93d3-a20de1c5480b',
                 'ip_address': ip_addr}],
            'id': 'fe6707e3-9c99-4529-b059-aa669d1463bb',
            'security_groups': ['9be76a64-4bed-4b6e-833b-17273b62908b'],
            'device_id': ''}}

        vm = h.create_vm('ika', port)
        try:
            vm.execute('ip link show dev eth0 | grep  %s' % mac)
            vm.execute('ip addr show dev eth0 | grep  %s' % ip_addr)
        except Exception as e:
            print str(e)
            raise AssertionError('veth inside netns does not have correct mac')
        vm.delete()

    def test_ping_between_two_vms(self):
        #
        # Title: basic L2 connectivity in Neutron network
        #
        # When: there is a neutron network on which there are 2 neutron ports
        # Then: spwan VMs for each port
        # Then: VMs can ping to each other
        #
        # Virtual Topology:
        #
        # TODO: visualize the topology
        #

        test_id = 'mdts2_test_ping_between_two_vms' + \
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info('Starting a test %s', test_id)


        tenant_id = test_id
        name = 'test_ping_between_two_vms'

        #
        # Topology setup
        #

        # create network and subnet
        net_data = {'name': name, 'tenant_id': tenant_id}
        net = self.neutron_client.create_network({'network':net_data})

        network_id = net['network']['id']

        subnet = self.neutron_client.create_subnet(
            {'subnet': {'name': name,
                        'tenant_id': tenant_id,
                        'cidr':'1.1.1.0/24',
                        'network_id': network_id,
                        'ip_version': 4}  })

        # create two ports
        port1 = self.neutron_client.create_port(
            {'port': {'tenant_id': tenant_id,
                      'network_id': network_id}})

        port2 = self.neutron_client.create_port(
            {'port': {'tenant_id': tenant_id,
                      'network_id': network_id}})

        # create two VMs on host[0] for each port
        vm1 = self.hosts[0].create_vm('vm1', port1)
        vm2 = self.hosts[0].create_vm('vm2', port2)

        # Test:
        # make sure that vm1 cna vm2 can ping each other
        #
        vm1.assert_pings_to(vm2)
        vm2.assert_pings_to(vm1)

        #
        # teardown VMs and neutron
        #
        vm1.delete()
        vm2.delete()

        # tearing down neutron ports and network
        self.neutron_client.delete_port(port1['port']['id'])
        self.neutron_client.delete_port(port2['port']['id'])
        self.neutron_client.delete_network(network_id)

        self.assertEqual(True, False)

try:
    if __name__ == '__main__':
        unittest.main()
except Exception as e:
    print 'Exception: ' + e.message + ', ' + str(e.args)