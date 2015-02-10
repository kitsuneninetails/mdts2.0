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

from MTestNetworkObject import NetworkObject
from MTestCLI import LinuxCLI

class Interface(NetworkObject):
    def __init__(self, name, nearHost):
        super(Interface, self).__init__(name, nearHost.getCLI())
        self._nearHost = nearHost
        self._ipList = []

    def setup(self):
        self.getCLI().cmd('ip link add dev ' + self.getName())
        for ip in self._ipList:
            self.getCLI().cmd('ip addr add ' + ip[0] + '/' + ip[1] + ' dev '  + self.getName())

    def cleanup(self):
        self.getCLI().cmd('ip link del dev '  + self.getName())

    def up(self):
        self.getCLI().cmd('ip link set dev ' + self.getName() + ' up')

    def down(self):
        self.getCLI().cmd('ip link set dev ' + self.getName() + ' down')

    def addIPs(self, ipList):
        self._ipList = ipList

    def getIPs(self):
        return self._ipList
        
    def addRoute(self, routeIP, gwIP):
        self.getCLI().cmd('ip route add ' + routeIP[0] + '/' + routeIP[1] + ' via ' + gwIP[0])

    def delRoute(self, routeIP):
        self.getCLI().cmd('ip route del ' + routeIP[0] + '/' + routeIP[1])

    def getNearHost(self):
        return self._nearHost

