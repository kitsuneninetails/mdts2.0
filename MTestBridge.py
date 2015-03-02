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
        self.cli.cmd('brctl addbr '  + self.get_name())
        for ip in self.ip_list:
            self.cli.cmd('ip addr add ' + ip[0] + '/' + ip[1] + ' dev '  + self.get_name())

    def cleanup(self):
        self.cli.cmd('brctl delbr '  + self.get_name())

    def up(self):
        self.cli.cmd('ip link set dev '  + self.get_name() + ' up')

    def down(self):
        self.cli.cmd('ip link set dev '  + self.get_name() + ' down')

    def add_link_interface(self, iface):
        self.cli.cmd('brctl addif ' + self.get_name() + ' ' + iface)

    def del_link_interface(self, iface):
        self.cli.cmd('brctl delif ' + self.get_name() + ' ' + iface)
