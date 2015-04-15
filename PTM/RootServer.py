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

from common.Exceptions import *
from Host import Host
from Bridge import Bridge
from ZookeeperHost import ZookeeperHost
from NetworkHost import NetworkHost
from CassandraHost import CassandraHost
from ComputeHost import ComputeHost
from RouterHost import RouterHost
from VLAN import VLAN
from common.CLI import LinuxCLI, NetNSCLI, CREATENSCMD, REMOVENSCMD
from PhysicalTopologyConfig import *


class RootServer(Host):
    def __init__(self):
        super(RootServer, self).__init__('root', LinuxCLI(), lambda name: None, lambda name: None, self)
        self.zookeeper_hosts = []
        """ :type: list[ZookeeperHost]"""
        self.cassandra_hosts = []
        """ :type: list[CassandraHost]"""
        self.compute_hosts = []
        """ :type: list[ComputeHost]"""
        self.network_hosts = []
        """ :type: list[NetworkHost]"""
        self.hosted_vms = []
        """ :type: list[VM]"""
        self.vlans = []
        """ :type: list[VLAN]"""
        self.routers = []
        """ :type: list[Router]"""
        self.hosts = {}
        """ :type: dict[str, Host]"""
        self.zookeeper_ips = []
        """ :type: list[Host]"""
        self.cassandra_ips = []
        """ :type: list[Host]"""
        self.generic_hosts = []
        """ :type: list[Host]"""

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

    def get_host(self, name):
        if name not in self.hosts:
            raise HostNotFoundException(name)
        return self.hosts[name]

    def get_bridge(self, name):
        if name not in self.bridges:
            raise ObjectNotFoundException(name)
        return self.bridges[name]

    @staticmethod
    def create_from_physical_topology_config(ptc):
        """
        :param ptc: PhysicalTopologyConfig
        :return: RootServer
        """
        rt = RootServer()

        for i in ptc.bridge_config:
            rt.config_bridge(i)

        for i in ptc.zookeeper_config:
            rt.config_zookeeper(i)

        for i in ptc.cassandra_config:
           rt.config_cassandra(i)

        for i in ptc.compute_config:
            rt.config_compute(i)

        for i in ptc.router_config:
            rt.config_router(i)

        for i in ptc.host_config:
            rt.config_generic_host(i)

        for i in ptc.vm_config:
            rt.config_vm(i)

        for i in ptc.vlan_config:
            rt.config_vlan(i)

        return rt

    def config_bridge(self, cfg):
        """
        :type cfg: BridgeDef
        :return: Bridge
        """
        b = Bridge(cfg.name, cfg.host, cfg.options.split(' '), cfg.ip_list)
        self.bridges[cfg.name] = b
        return b

    def config_zookeeper(self, cfg):
        """
        :type cfg: HostDef
        :return: ZookeeperHost
        """

        if len(cfg.interface_list) == 0:
            raise ArgMismatchException('zookeeper needs at least one interface')

        if len(cfg.interface_list[0].ip_list) == 0:
            raise ArgMismatchException('zookeeper interface list needs at least one IP')

        h = ZookeeperHost(cfg.name, NetNSCLI(cfg.name), CREATENSCMD, REMOVENSCMD, self)
        self.hosts[cfg.name] = h
        self.interfaces_for_host[cfg.name] = {}

        i = cfg.interface_list[0]
        self.add_virt_interface('veth' + cfg.name,
                                i.name,
                                h,
                                i.bridge_link,
                                i.ip_list,
                                i.mac_address)

        self.zookeeper_hosts.append(h)
        self.zookeeper_ips.append(i.ip_list[0])
        h.ip = i.ip_list[0]
        return h

    def config_cassandra(self, cfg):
        """
        :type cfg: HostDef
        :return: CassandraHost
        """

        if len(cfg.interface_list) == 0:
            raise ArgMismatchException('cassandra needs at least one interface')

        if len(cfg.interface_list[0].ip_list) == 0:
            raise ArgMismatchException('cassandra interface list needs at least one IP')

        if cfg.options == '':
            raise ArgMismatchException('cassandra interface list needs init token')

        h = CassandraHost(cfg.name, NetNSCLI(cfg.name), CREATENSCMD, REMOVENSCMD, self)
        self.hosts[cfg.name] = h
        self.interfaces_for_host[cfg.name] = {}

        h.init_token = cfg.options

        i = cfg.interface_list[0]
        self.add_virt_interface('veth' + cfg.name,
                                i.name,
                                h,
                                i.bridge_link,
                                i.ip_list,
                                i.mac_address)

        self.cassandra_hosts.append(h)
        self.cassandra_ips.append(i.ip_list[0])
        h.ip = i.ip_list[0]
        return h

    def config_compute(self, cfg):
        """
        :type cfg: HostDef
        :return: ComputeHost
        """

        if len(cfg.interface_list) == 0:
            raise ArgMismatchException('compute needs at least one interface')

        if len(cfg.interface_list[0].ip_list) == 0:
            raise ArgMismatchException('compute interface list needs at least one IP')

        h = ComputeHost(cfg.name, NetNSCLI(cfg.name), CREATENSCMD, REMOVENSCMD, self)
        self.hosts[cfg.name] = h
        self.interfaces_for_host[cfg.name] = {}

        h.zookeeper_ips = self.zookeeper_ips
        h.cassandra_ips = self.cassandra_ips

        i = cfg.interface_list[0]
        self.add_virt_interface('veth' + cfg.name,
                                i.name,
                                h,
                                i.bridge_link,
                                i.ip_list,
                                i.mac_address)

        self.compute_hosts.append(h)
        return h

    def config_router(self, cfg):
        """
        :type cfg: RouterDef
        :return: RouterHost
        """

        if len(cfg.peer_interface_list) == 0:
            raise ArgMismatchException('router needs at least one interface')

        if len(cfg.peer_interface_list[0].ip_list) == 0:
            raise ArgMismatchException('router interface list needs at least one IP')

        h = RouterHost(cfg.name, NetNSCLI(cfg.name), CREATENSCMD, REMOVENSCMD, self)
        self.hosts[cfg.name] = h
        self.interfaces_for_host[cfg.name] = {}

        i = cfg.peer_interface_list[0]
        for iface in cfg.peer_interface_list:
            h.add_hwinterface(iface.name,
                              h,
                              iface.bridge_link,
                              iface.ip_list,
                              iface.mac_address)

        self.routers.append(h)
        return h

    def config_vm(self, cfg):
        #hv_host_name, vm_name, interfaces):
        """
        :type cfg: VMDef
        :return: VMHost
        """

        hv_host = self.get_host(cfg.hypervisor_host_name) if cfg.hypervisor_host_name != '' else self
        """ :type: ComputeHost"""

        if not isinstance(hv_host, ComputeHost):
            raise HostNotFoundException(cfg.hypervisor_host_name)

        v = hv_host.create_vm(cfg.vm_host.name)

        for iface in cfg.vm_host.interface_list:
            self.add_virt_interface('veth' + cfg.vm_host.name,
                                    iface.name,
                                    v,
                                    iface.bridge_link,
                                    iface.ip_list,
                                    iface.mac_address)
        return v

    def config_vlan(self, cfg):
        """
        :type cfg: VLANDef
        :return: VLAN
        """
        vlan = VLAN(cfg.vlan_id, self)

        for host in cfg.host_list:
            for i in host.interface_list:
                vlan.add_interface(self.get_interfaces_for_host(host.name)[i.name],
                                   i.ip_list)

        self.vlans.append(vlan)
        return vlan

    def config_generic_host(self, cfg):
        """
        :type cfg: HostDef
        :return: Host
        """

        # interface is a list of maps: {iface, bridge, ips, mac}
        h = Host(cfg.name, NetNSCLI(cfg.name), CREATENSCMD, REMOVENSCMD, self)
        self.hosts[cfg.name] = h
        self.interfaces_for_host[cfg.name] = {}
        for iface in cfg.interface_list:
            self.add_virt_interface('veth' + cfg.name,
                                    iface.name,
                                    h,
                                    iface.bridge_link,
                                    iface.ip_list,
                                    iface.mac_address)

        self.generic_hosts.append(h)
        return h

    def init(self):
        for i in self.zookeeper_hosts:
            i.zookeeper_ips = self.zookeeper_ips

        for i in self.cassandra_hosts:
            i.cassandra_ips = self.cassandra_ips

        net_host = NetworkHost('net-node', LinuxCLI(), lambda name: None, lambda name: None, self)
        net_host.zookeeper_ips = self.zookeeper_ips
        self.network_hosts.append(net_host)

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
        for iface in self.hwinterfaces.itervalues():
            iface.setup()
            iface.up()

    def cleanup(self):
        for iface in self.hwinterfaces.itervalues():
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
            print 'mdts-ctl.py control requires <target> <id> <command> <optional_args>'
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