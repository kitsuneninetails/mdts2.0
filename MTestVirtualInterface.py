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

from MTestInterface import Interface
from MTestCLI import LinuxCLI

class VirtualInterface(Interface):
    def __init__(self, name, nearHost, farIfaceName, farHost, peerExt = '.p'):
        super(VirtualInterface, self).__init__(name, nearHost)
        self._peerName = self.getName() + peerExt
        self._farHost = farHost
        self._farIfaceName = farIfaceName

    def setup(self):
        # Add a veth-type interface with a peer
        self.getCLI().cmd('ip link add dev ' + self.getName() + ' type veth peer name ' + self._peerName)
        # Move peer iface onto far host's namespace
        self.getCLI().cmd('ip link set dev ' + self._peerName + ' netns ' + self._farHost.getName() + ' name ' + self._farIfaceName)
        # Add IPs
        for ip in self._ipList:
            self._farHost.getCLI().cmd('ip addr add ' + ip[0] + '/' + ip[1] + ' dev '  + self._farIfaceName)

    def up(self):
        # Set main iface up
        super(VirtualInterface, self).up()
        # Set peer iface up on far host's namespace
        self._farHost.getCLI().cmd('ip link set dev ' + self._farIfaceName + ' up')
        
    def down(self):
        super(VirtualInterface, self).down()
        self._farHost.getCLI().cmd('ip link set dev ' + self._farIfaceName + ' down')

    def addPeerRoute(self, routeIP, gwIP):
        self._farHost.getCLI().cmd('ip route add ' + routeIP[0] + '/' + routeIP[1] + ' via ' + gwIP[0])

    def delPeerRoute(self, routeIP):
        self._farHost.getCLI().cmd('ip route del ' + routeIP[0] + '/' + routeIP[1])

    def getFarHost(self):
        return self._farHost

    def getFarHostInterfaceName(self):
        return self._farIfaceName

