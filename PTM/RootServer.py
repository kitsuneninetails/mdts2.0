__author__ = 'micucci'
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

from Exceptions import *
from Host import Host
from Bridge import Bridge
from ZookeeperHost import ZookeeperHost
from NetworkHost import NetworkHost
from CassandraHost import CassandraHost
from ComputeHost import ComputeHost
from RouterHost import RouterHost
from VLAN import VLAN
from common.CLI import LinuxCLI, NetNSCLI, CREATENSCMD, REMOVENSCMD


class RootServer(Host):
    def __init__(self):
        super(RootServer, self).__init__('root', LinuxCLI(), lambda name: None, lambda name: None, self)
        self.zookeeper_hosts = []
        self.cassandra_hosts = []
        self.compute_hosts = []
        self.network_hosts = []
        self.hosted_vms = []
        self.vlans = []
        self.routers = []
        self.hosts = {}
        self.zookeeper_ips = []
        self.cassandra_ips = []
        self.generic_hosts = []

    def print_config(self, indent=0):
        print '[bridges]'
        for b in self.bridges.values():
            b.print_config(indent + 1)

        print '[zookeeper]'
        for h in self.zookeeper_hosts:
            h.print_config(indent + 1)
            print ('    ' * (indent + 2)) + 'Interfaces:'
            for name, i in self.get_interfaces_for_host(h.get_name()).items():
                print ('    ' * (indent + 3)) + name
                i.print_config(indent + 4)

        print '[cassandra]'
        for h in self.cassandra_hosts:
            h.print_config(indent + 1)
            print ('    ' * (indent + 2)) + 'Interfaces:'
            for name, i in self.get_interfaces_for_host(h.get_name()).items():
                print ('    ' * (indent + 3)) + name
                i.print_config(indent + 4)

        print '[compute]'
        for h in self.compute_hosts:
            h.print_config(indent + 1)
            print ('    ' * (indent + 2)) + 'Interfaces:'
            for name, i in self.get_interfaces_for_host(h.get_name()).items():
                print ('    ' * (indent + 3)) + name
                i.print_config(indent + 4)

        print '[routers]'
        for r in self.routers:
            r.print_config(indent + 1)

        print '[generic hosts]'
        for h in self.generic_hosts:
            h.print_config(indent + 1)
            print ('    ' * (indent + 2)) + 'Interfaces:'
            for name, i in self.get_interfaces_for_host(h.get_name()).items():
                print ('    ' * (indent + 3)) + name
                i.print_config(indent + 4)

        print '[vlans]'
        for v in self.vlans:
            v.print_config(indent + 1)

    def add_host(self, name, host):
        self.hosts[name] = host
        self.interfaces_for_host[name] = []

    def get_host(self, name):
        if name not in self.hosts:
            raise HostNotFoundException(name)
        return self.hosts[name]

    def add_bridge(self, name, ip_list):
        new_bridge = Bridge(name, self, ip_list)
        self.bridges[name] = new_bridge
        return new_bridge

    def get_bridge(self, name):
        if name not in self.bridges:
            raise ObjectNotFoundException(name)
        return self.bridges[name]

    @staticmethod
    def create_from_physical_topology_config(ptc):
        rt = RootServer()

        for i in ptc.bridge_config:
            rt.config_bridge(i.name,
                             [(ip.ip_address, ip.subnet_mask) for ip in i.ip_list],
                             i.options)

        for i in ptc.zookeeper_config:
            if len(i.interface_list) > 0:
                iface = {'iface': i.interface_list[0].name,
                         'bridge': i.interface_list[0].bridge_link.name
                             if i.interface_list[0].bridge_link is not None else '',
                         'ips': [(ip.ip_address, ip.subnet_mask) for ip in i.interface_list[0].ip_list],
                         'mac': i.interface_list[0].mac_address}
                rt.config_zookeeper(i.name, iface)

        for i in ptc.cassandra_config:
            if len(i.interface_list) > 0:
                iface = {'iface': i.interface_list[0].name,
                         'bridge': i.interface_list[0].bridge_link.name
                             if i.interface_list[0].bridge_link is not None else '',
                         'ips': [(ip.ip_address, ip.subnet_mask) for ip in i.interface_list[0].ip_list],
                         'mac': i.interface_list[0].mac_address}
                rt.config_cassandra(i.name, iface, i.options)

        for i in ptc.compute_config:
            if len(i.interface_list) > 0:
                iface = {'iface': i.interface_list[0].name,
                         'bridge': i.interface_list[0].bridge_link.name
                             if i.interface_list[0].bridge_link is not None else '',
                         'ips': [(ip.ip_address, ip.subnet_mask) for ip in i.interface_list[0].ip_list],
                         'mac': i.interface_list[0].mac_address}
                rt.config_compute(i.name, iface)

        for i in ptc.router_config:
            if_list = [{'iface': j.near_interface.name,
                        'bridge': j.near_interface.bridge_link.name
                            if j.near_interface.bridge_link is not None else '',
                        'ips': [(ip.ip_address, ip.subnet_mask) for ip in j.near_interface.ip_list],
                        'mac': j.near_interface.mac_address,
                        'target_host': j.target_interface.host,
                        'target_iface': j.target_interface.interface_name} for j in i.peer_interface_list]

            rt.config_router(i.name, if_list)

        for i in ptc.host_config:
            iface_list = [{'iface': j.name,
                           'bridge': j.bridge_link.name if j.bridge_link is not None else '',
                           'ips': [(ip.ip_address, ip.subnet_mask) for ip in j.ip_list],
                           'mac': j.mac_address} for j in i.interface_list if len(i.interface_list) > 0]
            rt.config_generic_host(i.name, iface_list)

        for i in ptc.vm_config:
            hv_name = i.hypervisor_host_name
            vm_host = i.vm_host

            if_list = [{'iface': j.name,
                        'bridge': j.bridge_link.name if j.bridge_link is not None else '',
                        'ips': [(ip.ip_address, ip.subnet_mask) for ip in j.ip_list],
                        'mac': j.mac_address} for j in vm_host.interface_list]

            rt.config_vm(hv_name, vm_host.name, if_list)

        for i in ptc.vlan_config:
            vlan_if_list = [{'host': tif.name,
                             'iface': tif.interface_list[0].name,
                             'ips': [(ip.ip_address, ip.subnet_mask) for ip in tif.interface_list[0].ip_list]
                            } for tif in i.host_list if len(tif.interface_list) > 0]
            rt.config_vlan(i.vlan_id, vlan_if_list)

        return rt

    def init(self):
        for i in self.zookeeper_hosts:
            i.zookeeper_ips = self.zookeeper_ips

        for i in self.cassandra_hosts:
            i.cassandra_ips = self.cassandra_ips

        net_host = NetworkHost('net-node', LinuxCLI(), lambda name: None, lambda name: None, self)
        net_host.zookeeper_ips = self.zookeeper_ips
        self.network_hosts.append(net_host)

    def config_bridge(self, name, ip_list, options):
        b = self.add_bridge(name, ip_list)
        b.set_options(options)

    def config_zookeeper(self, name, interface):
        # interface is a map: {iface, bridge, ips, mac}
        h = ZookeeperHost(name, NetNSCLI(name), CREATENSCMD, REMOVENSCMD, self)
        self.add_host(name, h)

        self.add_virt_interface('veth' + name,
                                interface['iface'],
                                h,
                                interface['bridge'],
                                interface['ips'],
                                interface['mac'])

        self.zookeeper_hosts.append(h)
        self.zookeeper_ips.append(interface['ips'][0])
        h.ip = interface['ips'][0]

    def config_cassandra(self, name, interface, extra_data):
        # interface is a map: {iface, bridge, ips, mac}
        h = CassandraHost(name, NetNSCLI(name), CREATENSCMD, REMOVENSCMD, self)
        self.add_host(name, h)

        h.init_token = extra_data[0]

        self.add_virt_interface('veth' + name,
                                interface['iface'],
                                h,
                                interface['bridge'],
                                interface['ips'],
                                interface['mac'])

        self.cassandra_hosts.append(h)
        self.cassandra_ips.append(interface['ips'][0])
        h.ip = interface['ips'][0]

    def config_compute(self, name, interface):
        # interface is a map: {iface, bridge, ips, mac}
        h = ComputeHost(name, NetNSCLI(name), CREATENSCMD, REMOVENSCMD, self)
        self.add_host(name, h)

        h.zookeeper_ips = self.zookeeper_ips
        h.cassandra_ips = self.cassandra_ips

        self.add_virt_interface('veth' + name,
                                interface['iface'],
                                h,
                                interface['bridge'],
                                interface['ips'],
                                interface['mac'])

        self.compute_hosts.append(h)

    def config_router(self, name, interfaces):
        # interfaces is a list of maps: {iface, target_iface, target_host, bridge, ips, mac}
        h = RouterHost(name, NetNSCLI(name), CREATENSCMD, REMOVENSCMD, self)
        self.add_host(name, h)

        for iface in interfaces:
            h.add_hwinterface(iface['iface'],
                              iface['target_iface'],
                              self.get_host(iface['target_host']),
                              iface['bridge'],
                              iface['ips'],
                              iface['mac'])

        self.routers.append(h)

    def config_vm(self, hv_host_name, vm_name, interfaces):
        # interface is a map: {iface, bridge, ips, mac}
        hv_host = self.get_host(hv_host_name) if hv_host_name != '' else self
        v = hv_host.create_vm(vm_name)

        for iface in interfaces:
            hv_host.add_virt_interface('veth' + vm_name,
                                       iface['iface'],
                                       v,
                                       iface['bridge'],
                                       iface['ips'],
                                       iface['mac'])

    def config_vlan(self, vlan_id, vlan_if_list):
        vlan = VLAN(vlan_id, self)

        for iface in vlan_if_list:
            vlan.add_interface(self.get_interfaces_for_host(iface['host'])[iface['iface']],
                               iface['ips'])

        self.vlans.append(vlan)

    def config_generic_host(self, name, interface_list):
        # interface is a list of maps: {iface, bridge, ips, mac}
        h = Host(name, NetNSCLI(name), CREATENSCMD, REMOVENSCMD, self)
        self.add_host(name, h)
        for iface in interface_list:
            self.add_virt_interface('veth' + name,
                                    iface['iface'],
                                    h,
                                    iface['bridge'],
                                    iface['ips'],
                                    iface['mac'])

        self.generic_hosts.append(h)

    def setup(self):
        for b in self.bridges.values():
            b.setup()
            b.up()
        for h in self.cassandra_hosts:
            h.setup()
            self.setup_host_interfaces(h)
        for h in self.zookeeper_hosts:
            h.setup()
            self.setup_host_interfaces(h)
        for h in self.compute_hosts:
            h.setup()
            self.setup_host_interfaces(h)
        for router in self.routers:
            router.setup()
        for h in self.compute_hosts:
            h.setup_vms()
        for h in self.generic_hosts:
            h.setup()
            self.setup_host_interfaces(h)
        for vlan in self.vlans:
            vlan.setup()
        for iface in self.hwinterfaces:
            iface.setup()
            iface.up()

    def cleanup(self):
        for iface in self.hwinterfaces:
            iface.down()
            iface.cleanup()
        for vlan in self.vlans:
            vlan.cleanup()
        for h in self.generic_hosts:
            self.cleanup_interfaces(h)
            h.cleanup()
        for h in self.compute_hosts:
            h.cleanup_vms()
        for router in self.routers:
            router.cleanup()
        for h in self.compute_hosts:
            self.cleanup_interfaces(h)
            h.cleanup()
        for h in self.zookeeper_hosts:
            self.cleanup_interfaces(h)
            h.cleanup()
        for h in self.cassandra_hosts:
            self.cleanup_interfaces(h)
            h.cleanup()
        for b in self.bridges.values():
            b.down()
            b.cleanup()

    def prepare_files(self):
        for h in self.network_hosts:
            h.prepare_files()
        for h in self.cassandra_hosts:
            h.prepare_files()
        for h in self.zookeeper_hosts:
            h.prepare_files()
        for h in self.compute_hosts:
            h.prepare_files()
        for r in self.routers:
            r.prepare_files()

    def start(self):
        for h in self.cassandra_hosts:
            h.start()
        for h in self.zookeeper_hosts:
            h.start()
        for h in self.network_hosts:
            h.start()
        for h in self.compute_hosts:
            h.start()
        for h in self.routers:
            h.start()
        for h in self.compute_hosts:
            h.start_vms()

    def stop(self):
        for h in self.network_hosts:
            h.stop()
        for h in self.compute_hosts:
            h.stop_vms()
        for h in self.routers:
            h.stop()
        for h in self.compute_hosts:
            h.stop()
        for h in self.cassandra_hosts:
            h.stop()
        for h in self.zookeeper_hosts:
            h.stop()

    @staticmethod
    def get_control_host(host_list, host_id):
        if host_id != 0 and len(host_list) >= host_id:
            return host_list[host_id-1]
        else:
            raise ObjectNotFoundException(str(host_id))

    def control(self, *args):
        if len(args) < 3:
            print 'EnvConfigure.py control requires <target> <id> <command> <optional_args>'
            raise ArgMismatchException(''.join(args))

        control_target = args[0]
        host_id = int(args[1])
        control_command = args[2]
        control_command_args = args[3:]

        try:
            if control_target == 'zookeeper':
                host = self.get_control_host(self.zookeeper_hosts, host_id)
            elif control_target == 'cassandra':
                host = self.get_control_host(self.cassandra_hosts, host_id)
            elif control_target == 'compute':
                host = self.get_control_host(self.compute_hosts, host_id)
            elif control_target == 'router':
                host = self.get_control_host(self.routers, host_id)
            else:
                raise ArgMismatchException(control_target)

            host.mount_shares()

            if control_command == 'start':
                host.control_start(control_command_args)

            if control_command == 'stop':
                host.control_stop(control_command_args)

            host.unmount_shares()

        except ObjectNotFoundException:
            print 'Host not found for target ' + control_target + ' and ID ' + str(host_id)
            raise
        except ArgMismatchException as e:
            print 'Valid targets are: zookeeper, cassandra, compute, or router (got: ' + str(e) + ')'
            raise