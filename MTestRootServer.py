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
        self.zookeeper_ips = []
        self.cassandra_ips = []

    def add_host(self, name, host):
        self.hosts[name] = host
        self.interfaces_for_host[name] = []
        
    def get_host(self, name):
        if name not in self.hosts:
            raise HostNotFoundException(name)
        return self.hosts[name]

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
            if len(host_cfg.get_ip_list()) is not 0:
                self.zookeeper_ips.append(host_cfg.get_ip_list()[0])
                h.ip = host_cfg.get_ip_list()[0]

        for i in self.zookeeper_hosts:
            i.zookeeper_ips = self.zookeeper_ips

        for i in cfg_obj['cassandra']:
            host_cfg = HostConfig(i)
            hname = host_cfg.get_name()

            h = CassandraHost(hname, NetNSCLI(hname), CREATENSCMD, REMOVENSCMD) 
            self.add_host(hname, h)
          
            h.linked_bridge = host_cfg.linked_bridge
            h.init_token = host_cfg.get_extra_data()[0]

            iface = self.add_virt_interface('veth' + hname, 'eth0', h)
            iface.add_ips(host_cfg.get_ip_list())
            self.cassandra_hosts.append(h)
            if len(host_cfg.get_ip_list()) is not 0:
                self.cassandra_ips.append(host_cfg.get_ip_list()[0])
                h.ip = host_cfg.get_ip_list()[0]

        for i in self.cassandra_hosts:
            i.cassandra_ips = self.cassandra_ips

        for i in cfg_obj['compute']:
            host_cfg = HostConfig(i)
            hname = host_cfg.get_name()

            h = ComputeHost(hname, NetNSCLI(hname), CREATENSCMD, REMOVENSCMD) 
            self.add_host(hname, h)
           
            h.linked_bridge = host_cfg.linked_bridge
            h.zookeeper_ips = self.zookeeper_ips
            h.cassandra_ips = self.cassandra_ips

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

        net_host = NetworkHost('net-node', LinuxCLI(), lambda name: None, lambda name: None)
        net_host.zookeeper_ips = self.zookeeper_ips
        self.network_hosts.append(net_host)

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

        LinuxCLI().rm('/etc/zookeeper.test')
        LinuxCLI().copy_dir('/etc/zookeeper', '/etc/zookeeper.test')
            
        for j in range(0,len(self.zookeeper_ips)):
            LinuxCLI().cmd('echo \"server.' + str(j + 1) + '=' + str(self.zookeeper_ips[j][0]) + \
                           ':2888:3888\" >>/etc/zookeeper.test/conf/zoo.cfg')

        for h in self.zookeeper_hosts:
            h.prepareFiles()

        for h in self.compute_hosts:
            h.prepareFiles()
        for r in self.routers: 
            r.prepareFiles()

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
        for vlan in self.vlans:
            pass

    def control(self, *args):

        if len(args) < 3:
            print 'Need at least 3 arguments to control command: <target> <id> <command> <optional_args>...'
            print 'Only got ' + str(len(args))
            exit(1)

        control_target= args[0]
        host_id = int(args[1])
        control_command = args[2]
        control_command_args = args[3:]
        
        if control_target == 'zookeeper':
            print 'Control: ' + control_target + 'host: ' + str(host_id)
            print len(self.zookeeper_hosts)
            if len(self.zookeeper_hosts) >= host_id:
                host = self.zookeeper_hosts[host_id-1]

        if control_target == 'cassandra':
            print 'Control: ' + control_target + 'host: ' + str(host_id)
            print len(self.cassandra_hosts)
            if len(self.cassandra_hosts) >= host_id:
                host = self.cassandra_hosts[host_id-1]

        if control_target == 'compute':
            print 'Control: ' + control_target + 'host: ' + str(host_id)
            print len(self.compute_hosts)
            if len(self.compute_hosts) >= host_id:
                host = self.compute_hosts[host_id-1]

        if control_target == 'router':
            print 'Control: ' + control_target + 'host: ' + str(host_id)
            print len(self.routers)
            if len(self.routers) >= host_id:
                host = self.routers[host_id-1]

        if control_command == 'start':
            host.control_start(control_command_args)

        if control_command == 'stop':
            host.control_stop(control_command_args)

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
        for vlan in self.vlans:
            pass

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
        self.extra_data = name_ip_tuple[3:]

    def get_linked_bridge(self):
        return self.linked_bridge

    def get_extra_data(self):
        return self.extra_data

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
