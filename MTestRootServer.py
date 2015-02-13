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

from MTestHost import Host
from MTestZookeeperHost import ZookeeperHost
from MTestNetworkHost import NetworkHost
from MTestCassandraHost import CassandraHost
from MTestComputeHost import ComputeHost
from MTestRouterHost import RouterHost
from MTestCLI import LinuxCLI, NetNSCLI, CREATENSCMD, REMOVENSCMD

class RootServer(Host):
    def __init__(self):
        super(RootServer, self).__init__('root', LinuxCLI(), lambda name: None, lambda name: None)
        self.zookeeper_hosts = []
        self.cassandra_hosts = []
        self.compute_hosts = []
        self.network_hosts = []
        self.hosted_vms = []
        self.vlans = []
        self.routers = []
        self.hosts = {}

    def print_config(self, indent=0):
        print '[bridges]'
        for b in self.bridges.values():
            b.print_config(indent + 1)

        print '[zookeeper]'
        for h in self.zookeeper_hosts:
            h.print_config(indent + 1)
            print ('    ' * (indent + 2)) + 'Interfaces:'
            for i in self.get_interfaces_for_host(h.get_name()):
                 i.print_config(indent + 3)

        print '[cassandra]'
        for h in self.cassandra_hosts:
            h.print_config(indent + 1)
            print ('    ' * (indent + 2)) + 'Interfaces:'
            for i in self.get_interfaces_for_host(h.get_name()):
                 i.print_config(indent + 3)

        print '[compute]'
        for h in self.compute_hosts:
            h.print_config(indent + 1)
            print ('    ' * (indent + 2)) + 'Interfaces:'
            for i in self.get_interfaces_for_host(h.get_name()):
                 i.print_config(indent + 3)

        print '[routers]'
        for r in self.routers:
            r.print_config(indent + 1)

        print '[vlans]'
        for i in self.vlans:
            pass

    def init(self, cfg_obj):

        for i in cfg_obj['bridges']:
            br_cfg = BridgeConfig(i)
            b = self.add_bridge(br_cfg.get_name())
            b.add_ips(br_cfg.get_ip_list())

        for i in cfg_obj['zookeeper']:
            host_cfg = HostConfig(i)
            hname = host_cfg.get_name()

            h = ZookeeperHost(hname, NetNSCLI(hname), CREATENSCMD, REMOVENSCMD) 
            self.add_host(hname, h)
          
            h.linked_bridge = host_cfg.linked_bridge
            iface = self.add_virt_interface('veth' + hname, 'eth0', h)
            iface.add_ips(host_cfg.get_ip_list())
            self.zookeeper_hosts.append(h)

        for i in cfg_obj['cassandra']:
            host_cfg = HostConfig(i)
            hname = host_cfg.get_name()

            h = CassandraHost(hname, NetNSCLI(hname), CREATENSCMD, REMOVENSCMD) 
            self.add_host(hname, h)
          
            h.linked_bridge = host_cfg.linked_bridge
            iface = self.add_virt_interface('veth' + hname, 'eth0', h)
            iface.add_ips(host_cfg.get_ip_list())
            self.cassandra_hosts.append(h)

        for i in cfg_obj['compute']:
            host_cfg = HostConfig(i)
            hname = host_cfg.get_name()

            h = ComputeHost(hname, NetNSCLI(hname), CREATENSCMD, REMOVENSCMD) 
            self.add_host(hname, h)
           
            h.linked_bridge = host_cfg.linked_bridge
            iface = self.add_virt_interface('veth' + hname, 'eth0', h)
            iface.add_ips(host_cfg.get_ip_list())
            self.compute_hosts.append(h)

        for i in cfg_obj['routers']:
            host_cfg = RouterConfig(i)
            hname = host_cfg.get_name()
            
            h = RouterHost(hname, NetNSCLI(hname), CREATENSCMD, REMOVENSCMD)
            self.add_host(hname, h)

            for iface in host_cfg.get_interfaces():
                newiface = h.add_hwinterface(iface.get_name(),  
                                            iface.get_far_host_interface_name(),
                                            self.get_host(iface.get_far_host_name()))
                newiface.add_ips(iface.get_ip_list())
            self.routers.append(h)

        for i in cfg_obj['hosted_vms']:
            vm_cfg = VMConfig(i)
            hvname = vm_cfg.get_name()
            hv_host = self.get_host(hvname)
            v = hv_host.create_vm(vm_cfg.get_vm().get_name())
            v.linked_bridge = vm_cfg.get_vm().linked_bridge
            iface = hv_host.add_virt_interface('veth' + v.get_name(), 'eth0', v)
            iface.add_ips(vm_cfg.get_vm().get_ip_list())

        for i in cfg_obj['vlans']:
            pass

        n = NetworkHost('net-node', LinuxCLI(), lambda name: None, lambda name: None)
        self.network_hosts.append(n)

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
        for vlan in self.vlans:
            pass
        for iface in self.hwinterfaces:
            iface.setup()
            iface.up()

    def cleanup(self):
        for iface in self.hwinterfaces:
            iface.down()
            iface.cleanup()
        for vlan in self.vlans:
            pass
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

    def prepareFiles(self):
        for h in self.network_hosts:
            h.prepareFiles()
        for h in self.cassandra_hosts:
            h.prepareFiles()
        for h in self.zookeeper_hosts:
            h.prepareFiles()

        if self.cli.cmd('lsmod | grep openvswitch >/dev/null') == 1:
            self.cli.cmd('sudo modprobe -r openvswitch')

        self.cli.cmd('sudo modprobe openvswitch')

        for h in self.compute_hosts:
            h.prepareFiles()
        for r in self.routers: 
            r.prepareFiles()

    def add_host(self, name, host):
        self.hosts[name] = host
        self.interfaces_for_host[name] = []
        
    def get_host(self, name):
        if name not in self.hosts:
            raise HostNotFoundException(name)
        return self.hosts[name]

class ConfigObjectBase(object):
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

class IPListConfig(ConfigObjectBase):
    def __init__(self, name, ip_tuple):
        super(IPListConfig, self).__init__(name)
        self.ip_list = ip_tuple

    def get_ip_list(self):
        return self.ip_list

class BridgeConfig(IPListConfig):
    def __init__(self, name_ip_tuple):
        super(BridgeConfig, self).__init__(name_ip_tuple[0], name_ip_tuple[2])
        self.base_host = name_ip_tuple[1]

    def get_base_host(self):
        return self.base_host
        
class HostConfig(IPListConfig):
    def __init__(self, name_ip_tuple):
        super(HostConfig, self).__init__(name_ip_tuple[0], name_ip_tuple[2])
        self.linked_bridge = name_ip_tuple[1]

    def get_linked_bridge(self):
        return self.linked_bridge

class InterfaceConfig(IPListConfig):
    def __init__(self, iface_tuple):
        super(InterfaceConfig, self).__init__(iface_tuple[0], iface_tuple[2])
        self.far_host_name = iface_tuple[1][0]
        self.far_host_iface_name = iface_tuple[1][1]

    def get_far_host_name(self):
        return self.far_host_name

    def get_far_host_interface_name(self):
        return self.far_host_iface_name
            
class RouterConfig(ConfigObjectBase):
    def __init__(self, host_iface_tuple):
        super(RouterConfig, self).__init__(host_iface_tuple[0])
        self.interfaces = []
        for iface_def in host_iface_tuple[1]:
            self.interfaces.append(InterfaceConfig(iface_def))
        
    def get_interfaces(self):
        return self.interfaces

class VMConfig(ConfigObjectBase):
    def __init__(self, host_tuple):
        super(VMConfig, self).__init__(host_tuple[0])
        self.vm = HostConfig(host_tuple[1:])
        
    def get_vm(self):
        return self.vm
