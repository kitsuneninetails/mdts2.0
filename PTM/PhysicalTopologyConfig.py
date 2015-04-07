__author__ = 'micucci'
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

# Topology Grammar (pseudo-BNF)
#
# 'ip' = IPDef := ( ip_address, subnet_mask )
# 'ip_list' = IPDefList := [ IPDef1, ..., IPDefN ]
# 'bridge_link' = BridgeLinkDef := ( host, name )
# 'bridge' = BridgeDef := ( name, host, IPDefList, options )
# 'bridge_list' = BridgeDefList := [ BridgeDef1, ..., BridgeDefN ]
# 'interface' = InterfaceDef := ( name, IPDefList, BridgeLinkDef )
# 'interface_list' = InterfaceDefList := [ InterfaceDef1, ..., InterfaceDefN ]
# 'host' = HostDef := { name, InterfaceDefList, options }
# 'host_list' = HostDefList := [ HostDef1, ..., HostDefN ]
# 'zookeeper_list' = ZookeeperDefList = HostDefList
# 'cassandra_list' = CassandraDefList = HostDefList
# 'compute_list' = ComputeDefList = HostDefList
# 'vm' = VMDef = ( hypervisor_host, HostDef )
# 'vm_list' = VMDefList = [ VMDef1, ..., VMDefN ]
# 'target_interface' = TargetInterfaceDef := ( host, interface_name )
# 'target_interface_list' = TargetInterfaceDefList := [ TargetInterfaceDef1, ..., TargetInterfaceDefN ]
# 'near_interface' = NearInterfaceDef := InterfaceDef
# 'peer_interface' = PeerInterfaceDef := ( NearInterfaceDef, TargetInterfaceDef )
# 'peer_interface_list' = PeerInterfaceDefList := [ PeerInterfaceDef1, ..., PeerInterfaceDefN ]
# 'router' = RouterDef := ( name, PeerInterfaceDefList )
# 'router_list' = RouterDefList := [ RouterDef1, ..,, RouterDefN ]
# 'vlan' = VLANDef := ( vlan_id, HostDefList )
# 'vlan_list' = VLANDefList := [ VLANDef1, ..., VLANDefN ]
# PhysicalTopologyConfig := 
#    { 'bridge_config'=BridgeDefList, 'zookeeper_config'=ZookeeperDefList, 'cassandra_config'=CassandraDefList,
#      'compute_config'=ComputeDefList, 'router_config'=RouterDefList, 'vm_config'=VMDefList,
#      'vlan_config'=VLANDefList, 'hosts'=HostList }


class IPDef(object):
    def __init__(self, ip_address, subnet_mask):
        self.ip_address = ip_address
        """ :type: str"""
        self.subnet_mask = subnet_mask
        """ :type: str"""


class BridgeLinkDef(object):
    def __init__(self, host, name):
        self.host = host
        """ :type: str"""
        self.name = name
        """ :type: str"""


class BridgeDef(object):
    def __init__(self, name, host, ip_list, options):
        self.name = name
        """ :type: str"""
        self.host = host
        """ :type: str"""
        self.ip_list = ip_list
        """ :type: list[IPDef]"""
        self.options = options
        """ :type: str"""


class InterfaceDef(object):
    def __init__(self, name, bridge_link, ip_list, mac_address):
        self.name = name
        """ :type: str"""
        self.ip_list = ip_list
        """ :type: list[IPDef]"""
        self.bridge_link = bridge_link
        """ :type: BridgeLinkDef"""
        self.mac_address = mac_address
        """ :type: str"""


class HostDef(object):
    def __init__(self, name, interface_list, options):
        self.name = name
        """ :type: str"""
        self.interface_list = interface_list
        """ :type: list[InterfaceDef]"""
        self.options = options
        """ :type: str"""


class VMDef(object):
    def __init__(self, hypervisor_host_name, vm_host):
        self.hypervisor_host_name = hypervisor_host_name
        """ :type: str"""
        self.vm_host = vm_host
        """ :type: HostDef"""

        
class TargetInterfaceDef(object):
    def __init__(self, host, interface_name):
        self.host = host
        """ :type: str"""
        self.interface_name = interface_name
        """ :type: str"""


class PeerInterfaceDef(object):
    def __init__(self, near_interface, target_interface):
        self.near_interface = near_interface
        """ :type: InterfaceDef"""
        self.target_interface = target_interface
        """ :type: TargetInterfaceDef"""


class RouterDef(object):
    def __init__(self, name, peer_interface_list):
        self.name = name
        """ :type: str"""
        self.peer_interface_list = peer_interface_list
        """ :type: list[InterfaceDef]"""


class VLANDef(object):
    def __init__(self, vlan_id, host_list):
        self.vlan_id = vlan_id
        """ :type: str"""
        self.host_list = host_list
        """ :type: list[HostDef]"""


class PhysicalTopologyConfig(object):
    def __init__(self):
        self.bridge_config = []
        """ :type: list[BridgeDef]"""
        self.zookeeper_config = []
        """ :type: list[HostDef]"""
        self.cassandra_config = []
        """ :type: list[HostDef]"""
        self.compute_config = []
        """ :type: list[HostDef]"""
        self.router_config = []
        """ :type: list[RouterDef]"""
        self.host_config = []
        """ :type: list[HostDef]"""
        self.vm_config = []
        """ :type: list[VMDef]"""
        self.vlan_config = []
        """ :type: list[VLANDef]"""

    def add_bridge_def(self, bridge):
        """ :type bridge: BridgeDef """
        self.bridge_config.append(bridge)

    def add_zookeeper_def(self, zookeeper):
        """ :type zookeeper: HostDef """
        self.zookeeper_config.append(zookeeper)

    def add_cassandra_def(self, cassandra):
        """ :type cassandra: HostDef """
        self.cassandra_config.append(cassandra)

    def add_compute_def(self, compute):
        """ :type compute: HostDef """
        self.compute_config.append(compute)

    def add_router_def(self, router):
        """ :type router: RouterDef """
        self.router_config.append(router)

    def add_host_def(self, host):
        """ :type host: HostDef """
        self.host_config.append(host)

    def add_vm_def(self, vm):
        """ :type vm: VMDef """
        self.vm_config.append(vm)

    def add_vlan_def(self, vlan):
        """ :type vlan: VLANDef """
        self.vlan_config.append(vlan)
