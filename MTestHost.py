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

from MTestExceptions import *
from MTestCLI import LinuxCLI, NetNSCLI
from MTestNetworkObject import NetworkObject
from MTestBridge import Bridge
from MTestInterface import Interface
from MTestVirtualInterface import VirtualInterface

def createNSHost(name):
    newHost = Host(name, NetNSCLI(name), lambda name: LinuxCLI().cmd('ip netns add ' + name), 
                                         lambda name: LinuxCLI().cmd('ip netns del ' + name))
    return newHost

class Host(NetworkObject):
    def __init__(self, name, cli, hostCreateFunc, hostRemoveFunc):
        super(Host, self).__init__(name, cli)
        self._hosts = {}
        self._bridges = {}
        self._interfacesForHost = {}
        self._vms = {}
        self._hwinterfaces = []
        self._createFunc = hostCreateFunc
        self._removeFunc = hostRemoveFunc
        self._linkedBridge = ''

    def setLinkedBridge(self, bridge):
        self._linkedBridge = bridge
        
    def getLinkedBridge(self):
        return self._linkedBridge

    def setup(self):
        self._createFunc(self.getName())

        for bridge in self.getBridges():
            bridge.setup()
            bridge.up()

        for iface in self.getHWInterfaces():
            iface.setup()
            iface.up()

    def setupHostInterfaces(self, host):
        for interface in self.getInterfacesForHost(host.getName()):
            interface.setup()
            interface.up()
            if host.getLinkedBridge() is not '':
                br = self.getBridge(host.getLinkedBridge())
                br.addLinkInterface(interface.getName())
                if len(br.getIPs()) is not 0:
                    interface.addPeerRoute(('0.0.0.0','0'), br.getIPs()[0])

    def setupHosts(self):
        for host in self.getHosts():
            host.setup()
            self.setupHostInterfaces(host)

    def cleanup(self):
        for bridge in self.getBridges():
            bridge.down()
            bridge.cleanup()

        for interface in self.getHWInterfaces():
            interface.down()
            interface.cleanup()

        self._removeFunc(self.getName())

    def cleanupInterfaces(self, host):
        for interface in self.getInterfacesForHost(host.getName()):
            interface.down()
            interface.cleanup()

    def cleanupHosts(self):
        for host in self.getHosts():
            self.cleanupInterfaces(host)
            host.cleanup()

    def setLoopback(self, ip):
        self.getCLI().cmd('ip link set dev lo up')
        self.getCLI().cmd('ip addr add ' + ip[0] + '/' + ip[1] + ' dev lo')

    def addHost(self, name):
        newHost = createNSHost(name)
        self._hosts[name] = newHost
        self._interfacesForHost[name] = []
        return newHost
        
    def delHost(self, name):
        if name in self._hosts:
            del self._hosts[name]
            del self._interfacesForHost[name]

    def getHost(self, name):
        if name not in self._hosts:
            raise HostNotFoundException(name)
        return self._hosts[name]

    def getHosts(self):
        return self._hosts.values()

    def addBridge(self, name):
        newBridge = Bridge(name, self)
        self._bridges[name] = newBridge
        return newBridge

    def getBridge(self, name):
        if name not in self._bridges:
            raise ObjectNotFoundException(name)
        return self._bridges[name]

    def getBridges(self):
        return self._bridges.values()

    def delBridge(self, name):
        if name in self._bridges:
            del self._bridges[name]

    def addHWInterface(self, name, farIfaceName, farHost):
        newIf = VirtualInterface(name, self, farIfaceName, farHost, '.p')
        self._hwinterfaces.append(newIf)
        return newIf

    def addVirtInterface(self, name, farIfaceName, farHost):
        newIf = VirtualInterface(name, self, farIfaceName, farHost, '.p')
        if farHost not in self._interfacesForHost:
            self._interfacesForHost[farHost.getName()] = []
        self._interfacesForHost[farHost.getName()].append(newIf)
        return newIf

    def getInterfacesForHost(self, farHost):
        if farHost not in self._interfacesForHost:
            raise ObjectNotFoundException(farHost)
        return self._interfacesForHost[farHost]

    def getHWInterfaces(self):
        return self._hwinterfaces
