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

class Bridge(Interface):
    def setup(self):
        self.getCLI().cmd('brctl addbr '  + self.getName())
        for ip in self._ipList:
            self.getCLI().cmd('ip addr add ' + ip[0] + '/' + ip[1] + ' dev '  + self.getName())

    def cleanup(self):
        self.getCLI().cmd('brctl delbr '  + self.getName())

    def up(self):
        self.getCLI().cmd('ip link set dev '  + self.getName() + ' up')

    def down(self):
        self.getCLI().cmd('ip link set dev '  + self.getName() + ' down')

    def addLinkInterface(self, iface):
        self.getCLI().cmd('brctl addif ' + self.getName() + ' ' + iface)

    def delLinkInterface(self, iface):
        self.getCLI().cmd('brctl delif ' + self.getName() + ' ' + iface)
