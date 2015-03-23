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


class IPDef:
    def __init__(self, ip_address, subnet_mask):
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask


class BridgeLinkDef:
    def __init__(self, host, name):
        self.host = host
        self.name = name


class BridgeDef:
    def __init__(self, name, host, ip_list, options):
        self.name = name
        self.host = host
        self.ip_list = ip_list
        self.options = options


class InterfaceDef:
    def __init__(self, name, bridge_link, ip_list, mac_address):
        self.name = name
        self.ip_list = ip_list
        self.bridge_link = bridge_link
        self.mac_address = mac_address


class HostDef:
    def __init__(self, name, interface_list, options):
        self.name = name
        self.interface_list = interface_list
        self.options = options


class VMDef:
    def __init__(self, hypervisor_host_name, vm_host):
        self.hypervisor_host_name = hypervisor_host_name
        self.vm_host = vm_host
        
        
class TargetInterfaceDef:
    def __init__(self, host, interface_name):
        self.host = host
        self.interface_name = interface_name


class PeerInterfaceDef:
    def __init__(self, near_interface, target_interface):
        self.near_interface = near_interface
        self.target_interface = target_interface


class RouterDef:
    def __init__(self, name, peer_interface_list):
        self.name = name
        self.peer_interface_list = peer_interface_list


class VLANDef:
    def __init__(self, vlan_id, host_list):
        self.vlan_id = vlan_id
        self.host_list = host_list


class PhysicalTopologyConfig:
    def __init__(self):
        self.bridge_config = []
        self.zookeeper_config = []
        self.cassandra_config = []
        self.compute_config = []
        self.router_config = []
        self.host_config = []
        self.vm_config = []
        self.vlan_config = []

    def add_bridge_def(self, bridge):
        self.bridge_config.append(bridge)

    def add_zookeeper_def(self, zookeeper):
        self.zookeeper_config.append(zookeeper)

    def add_cassandra_def(self, cassandra):
        self.cassandra_config.append(cassandra)

    def add_compute_def(self, compute):
        self.compute_config.append(compute)

    def add_router_def(self, router):
        self.router_config.append(router)

    def add_host_def(self, host):
        self.host_config.append(host)

    def add_vm_def(self, vm):
        self.vm_config.append(vm)

    def add_vlan_def(self, vlan):
        self.vlan_config.append(vlan)
