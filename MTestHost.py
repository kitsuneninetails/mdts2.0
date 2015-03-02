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

class Host(NetworkObject):
    def __init__(self, name, cli, host_create_func, host_remove_func):
        super(Host, self).__init__(name, cli)
        self.bridges = {}
        self.interfaces_for_host = {}
        self.hwinterfaces = []
        self.create_func = host_create_func
        self.remove_func = host_remove_func
        self.linked_bridge = ''

    def setup(self):
        self.create_func(self.name)

        for bridge in self.bridges:
            bridge.setup()
            bridge.up()

        for iface in self.hwinterfaces:
            iface.setup()
            iface.up()

    def setup_host_interfaces(self, host):
        for interface in self.get_interfaces_for_host(host.get_name()):
            interface.setup()
            interface.up()
            if host.linked_bridge is not '':
                br = self.get_bridge(host.linked_bridge)
                br.add_link_interface(interface.get_name())
                if len(br.get_ips()) is not 0:
                    interface.add_peer_route(('0.0.0.0','0'), br.get_ips()[0])

    def cleanup(self):
        for bridge in self.bridges:
            bridge.down()
            bridge.cleanup()

        for interface in self.hwinterfaces:
            interface.down()
            interface.cleanup()

        self.remove_func(self.name)

    def cleanup_interfaces(self, host):
        for interface in self.get_interfaces_for_host(host.get_name()):
            interface.down()
            interface.cleanup()

    def set_loopback(self, ip):
        self.cli.cmd('ip link set dev lo up')
        self.cli.cmd('ip addr add ' + ip[0] + '/' + ip[1] + ' dev lo')

    def add_bridge(self, name):
        new_bridge = Bridge(name, self)
        self.bridges[name] = new_bridge
        return new_bridge

    def get_bridge(self, name):
        if name not in self.bridges:
            raise ObjectNotFoundException(name)
        return self.bridges[name]

    def add_hwinterface(self, name, far_iface_name, far_host):
        new_if = VirtualInterface(name, self, far_iface_name, far_host, '.p')
        self.hwinterfaces.append(new_if)
        return new_if

    def add_virt_interface(self, name, far_iface_name, far_host):
        new_if = VirtualInterface(name, self, far_iface_name, far_host, '.p')
        if far_host not in self.interfaces_for_host:
            self.interfaces_for_host[far_host.get_name()] = []
        self.interfaces_for_host[far_host.get_name()].append(new_if)
        return new_if

    def get_interfaces_for_host(self, far_host):
        if far_host not in self.interfaces_for_host:
            raise ObjectNotFoundException(farHost)
        return self.interfaces_for_host[far_host]

    def print_config(self, indent=0):
        print ('    ' * indent) + self.name + ' linked on bridge: ' + self.linked_bridge

    def start(self):
        pass

    def stop(self):
        pass

    def control_start(self, *args):
        pass

    def control_stop(self, *args):
        pass

    def mount_shares(self):
        pass

    def unmount_shared(self):
        pass
