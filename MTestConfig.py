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

from MTestHost import Host, createNSHost
from MTestCLI import LinuxCLI

class RootServer(Host):
    def __init__(self):
        super(RootServer, self).__init__('root', LinuxCLI(), lambda name: None, lambda name: None)
        self._zookeeperHosts = []
        self._cassandraHosts = []
        self._computeHosts = []
        self._hostedVMs = []
        self._vlans = []
        self._routers = []

    def printConfig(self):
        print '[bridges]'
        for b in self.getBridges():
            print b.getName() + ' with IPs: ' + str(b.getIPs())

        print '[zookeeper]'
        for h in self.getZookeeperHosts():
            print h.getName() + ' linked on bridge: ' + h.getLinkedBridge() + ' on interfaces: ' 
            for i in self.getInterfacesForHost(h.getName()):
                print '    ' + str(i.getName()) + ' on IPs ' + str(i.getIPs())

        print '[cassandra]'
        for h in self.getCassandraHosts():
            print h.getName() + ' linked on bridge: ' + h.getLinkedBridge() + ' on interfaces: ' 
            for i in self.getInterfacesForHost(h.getName()):
                print '    ' + str(i.getName()) + ' on IPs ' + str(i.getIPs())

        print '[compute]'
        for h in self.getComputeHosts():
            print h.getName() + ' linked on bridge: ' + h.getLinkedBridge() + ' on interfaces: ' 
            for i in self.getInterfacesForHost(h.getName()):
                print '    ' + str(i.getName()) + ' on IPs ' + str(i.getIPs())

        print '[routers]'
        for r in self.getRouters():
            print r.getName() + ' hosting interfaces:' 
            for j in r.getHWInterfaces():
                print '    ' + j.getName() + ' linked as ' + j.getFarHost().getName() + '/' \
                             + j.getFarHostInterfaceName() + ' with IPs: ' + str(j.getIPs())

        print '[hostedVMs]'
        for hv in self.getComputeHosts():
            print hv.getName() + ' hosting VMs: '
            for vm in hv.getHosts():
                print '    ' + vm.getName() + ' linked on bridge: ' + vm.getLinkedBridge() + ' on interfaces: ' 
                for i in hv.getInterfacesForHost(vm.getName()):
                    print '        ' + str(i.getName()) + ' on IPs ' + str(i.getIPs())

        print '[vlans]'
        for i in self.getVLANs():
            Pass

    def init(self, cfgObj):

        for i in cfgObj['bridges']:
            brCfg = BridgeConfig(i)
            b = self.addBridge(brCfg.getName())
            b.addIPs(brCfg.getIPList())

        for i in cfgObj['zookeeper']:
            hostCfg = HostConfig(i)
            hname = hostCfg.getName()
            h = self.addHost(hname)
            h.setLinkedBridge(hostCfg.getLinkedBridge())
            iface = self.addVirtInterface('veth' + hname, 'eth0', h)
            iface.addIPs(hostCfg.getIPList())
            self._zookeeperHosts.append(h)

        for i in cfgObj['cassandra']:
            hostCfg = HostConfig(i)
            hname = hostCfg.getName()
            h = self.addHost(hname)
            h.setLinkedBridge(hostCfg.getLinkedBridge())
            iface = self.addVirtInterface('veth' + hname, 'eth0', h)
            iface.addIPs(hostCfg.getIPList())
            self._cassandraHosts.append(h)

        for i in cfgObj['compute']:
            hostCfg = HostConfig(i)
            hname = hostCfg.getName()
            h = self.addHost(hname)
            h.setLinkedBridge(hostCfg.getLinkedBridge())
            iface = self.addVirtInterface('veth' + hname, 'eth0', h)
            iface.addIPs(hostCfg.getIPList())
            self._computeHosts.append(h)

        for i in cfgObj['routers']:
            hostCfg = RouterConfig(i)
            hname = hostCfg.getName()
            h = self.addRouter(hname)
            for iface in hostCfg.getInterfaces():
                newiface = h.addHWInterface(iface.getName(),  
                                            iface.getFarHostInterfaceName(),
                                            self.getHost(iface.getFarHostName()))
                newiface.addIPs(iface.getIPList())

        for i in cfgObj['hosted_vms']:
            vmCfg = VMConfig(i)
            hvname = vmCfg.getName()
            hvHost = self.getHost(hvname)
            v = hvHost.addHost(vmCfg.getVM().getName())
            v.setLinkedBridge(vmCfg.getVM().getLinkedBridge())
            iface = hvHost.addVirtInterface('veth' + v.getName(), 'eth0', v)
            iface.addIPs(vmCfg.getVM().getIPList())

        for i in cfgObj['vlans']:
            Pass

    def getZookeeperHosts(self):
        return self._zookeeperHosts

    def getCassandraHosts(self):
        return self._cassandraHosts

    def getComputeHosts(self):
        return self._computeHosts

    def getHostedVMs(self):
        return self._hostedVMs

    def getVLANs(self):
        return self._vlans

    def addRouter(self, name):
        newRouter = createNSHost(name)
        self._routers.append(newRouter)
        return newRouter
        
    def getRouters(self):
        return self._routers

    def setup(self):
        for b in self.getBridges():
            b.setup()
            b.up()
        for h in self.getCassandraHosts():
            h.setup()
            self.setupHostInterfaces(h)
        for h in self.getZookeeperHosts():
            h.setup()
            self.setupHostInterfaces(h)
        for h in self.getComputeHosts():
            h.setup()
            self.setupHostInterfaces(h)
        for router in self.getRouters():
            router.setup()
        for h in self.getComputeHosts():
            h.setupHosts()
        for vlan in self.getVLANs():
            Pass
        for iface in self.getHWInterfaces():
            iface.setup()
            iface.up()

    def cleanup(self):
        for iface in self.getHWInterfaces():
            iface.down()
            iface.cleanup()
        for vlan in self.getVLANs():
            Pass
        for h in self.getComputeHosts():
            h.cleanupHosts()
        for router in self.getRouters():
            router.cleanup()
        for h in self.getComputeHosts():
            self.cleanupInterfaces(h)
            h.cleanup()
        for h in self.getZookeeperHosts():
            self.cleanupInterfaces(h)
            h.cleanup()
        for h in self.getCassandraHosts():
            self.cleanupInterfaces(h)
            h.cleanup()
        for b in self.getBridges():
            b.down()
            b.cleanup()

class ConfigObjectBase(object):
    def __init__(self, name):
        self._name = name

    def getName(self):
        return self._name

class IPListConfig(ConfigObjectBase):
    def __init__(self, name, ipTuple):
        super(IPListConfig, self).__init__(name)
        self._ipList = ipTuple

    def getIPList(self):
        return self._ipList

class BridgeConfig(IPListConfig):
    def __init__(self, nameIPTuple):
        super(BridgeConfig, self).__init__(nameIPTuple[0], nameIPTuple[2])
        self._baseHost = nameIPTuple[1]

    def getBaseHost(self):
        return self._baseHost
        
class HostConfig(IPListConfig):
    def __init__(self, nameIPTuple):
        super(HostConfig, self).__init__(nameIPTuple[0], nameIPTuple[2])
        self._linkedBridge = nameIPTuple[1]

    def getLinkedBridge(self):
        return self._linkedBridge

class InterfaceConfig(IPListConfig):
    def __init__(self, ifaceTuple):
        super(InterfaceConfig, self).__init__(ifaceTuple[0], ifaceTuple[2])
        self._farHostName = ifaceTuple[1][0]
        self._farHostIfaceName = ifaceTuple[1][1]

    def getFarHostName(self):
        return self._farHostName

    def getFarHostInterfaceName(self):
        return self._farHostIfaceName
            
class RouterConfig(ConfigObjectBase):
    def __init__(self, hostIfaceTuple):
        super(RouterConfig, self).__init__(hostIfaceTuple[0])
        self._interfaces = []
        for ifaceDef in hostIfaceTuple[1]:
            self._interfaces.append(InterfaceConfig(ifaceDef))
        
    def getInterfaces(self):
        return self._interfaces

class VMConfig(ConfigObjectBase):
    def __init__(self, hostTuple):
        super(VMConfig, self).__init__(hostTuple[0])
        self._vm = HostConfig(hostTuple[1:])
        
    def getVM(self):
        return self._vm
