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

from NetworkObject import NetworkObject


class Interface(NetworkObject):
    def __init__(self, name, near_host, linked_bridge='', ip_list=list(), mac='default'):
        super(Interface, self).__init__(name, near_host.get_cli())
        self.near_host = near_host
        self.linked_bridge = linked_bridge
        self.ip_list = ip_list
        self.mac = mac

    def setup(self):
        self.get_cli().cmd('ip link add dev ' + self.get_name())

        if self.mac != 'default':
            self.get_cli().cmd('ip link set dev ' + self.get_name() + ' address ' + self.mac)

        for ip in self.ip_list:
            self.get_cli().cmd('ip addr add ' + ip[0] + '/' + ip[1] + ' dev ' + self.get_name())

    def cleanup(self):
        self.get_cli().cmd('ip link del dev ' + self.get_name())

    def up(self):
        self.get_cli().cmd('ip link set dev ' + self.get_name() + ' up')

    def down(self):
        self.get_cli().cmd('ip link set dev ' + self.get_name() + ' down')

    def change_mac(self, new_mac):
        self.mac = new_mac
        self.get_cli().cmd('ip link set dev ' + self.get_name() + ' address ' + new_mac)

    def add_ip(self, new_ip):
        self.ip_list.append(new_ip)
        self.get_cli().cmd('ip addr add ' + new_ip[0] + '/' + new_ip[1] + ' dev ' + self.get_name())

    def link_vlan(self, vlan_id, ip_list):
        vlan_iface = self.name + '.' + str(vlan_id)
        self.get_cli().cmd('ip link add link ' + self.name +
                           ' name ' + vlan_iface + ' type vlan id ' + str(vlan_id))
        self.get_cli().cmd('ip link set dev ' + vlan_iface + ' up')
        for ip in ip_list:
            self.get_cli().cmd('ip addr add ' + ip[0] + '/' + ip[1] + ' dev ' + vlan_iface)

    def add_route(self, route_ip, gw_ip):
        self.get_cli().cmd('ip route add ' + route_ip[0] + '/' + route_ip[1] + ' via ' + gw_ip[0])

    def del_route(self, route_ip):
        self.get_cli().cmd('ip route del ' + route_ip[0] + '/' + route_ip[1])


    def get_host_name(self):
        return self.near_host.get_name()

    def get_interface_name(self):
        return self.name

    def get_near_host(self):
        return self.near_host

    def print_config(self, indent=0):
        link = ' linked on bridge: ' + self.linked_bridge if self.linked_bridge != '' else ''
        print ('    ' * indent) + self.name + ' with ips: ' + ', '.join(ip[0] + '/' + ip[1] for ip in self.ip_list)
