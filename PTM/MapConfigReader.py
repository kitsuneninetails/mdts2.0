__author__ = 'micucci'
# Copyright 2015 Midokura SARL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from RootServer import RootServer


class MapConfigReader(object):
    def __init__(self):
        pass

    @staticmethod
    def root_server_from_python_map(cfg_obj):
        rt = RootServer()

        for i in cfg_obj['bridges']:
            br_cfg = BridgeConfig(i)
            rt.config_bridge(br_cfg.get_name(), br_cfg.get_ip_list())

        for i in cfg_obj['zookeeper']:
            host_cfg = HostConfig(i)
            rt.config_zookeeper(host_cfg.get_name(),
                                host_cfg.get_linked_bridge(),
                                host_cfg.get_ip_list())

        for i in cfg_obj['cassandra']:
            host_cfg = HostConfig(i)
            rt.config_cassandra(host_cfg.get_name(),
                                host_cfg.get_linked_bridge(),
                                host_cfg.get_ip_list(),
                                host_cfg.get_extra_data())

        for i in cfg_obj['compute']:
            host_cfg = HostConfig(i)
            rt.config_compute(host_cfg.get_name(),
                              host_cfg.get_linked_bridge(),
                              host_cfg.get_ip_list())

        for i in cfg_obj['routers']:
            host_cfg = RouterConfig(i)
            rt.config_router(host_cfg.get_name(),
                             host_cfg.get_interfaces())

        for i in cfg_obj['hosted_vms']:
            vm_cfg = VMConfig(i)
            rt.config_vm(vm_cfg.get_vm().get_name(), vm_cfg.get_name(),
                         vm_cfg.get_vm().get_linked_bridge(), vm_cfg.get_vm().get_ip_list())

        for i in cfg_obj['vlans']:
            pass

        return rt


class ConfigObjectBase(object):
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


class IPListConfig(ConfigObjectBase):
    def __init__(self, name, ip_tuple):
        super(IPListConfig, self).__init__(name)
        self.ip_list = ip_tuple

    def get_ip_list(self):
        return self.ip_list


class BridgeConfig(IPListConfig):
    def __init__(self, name_ip_tuple):
        super(BridgeConfig, self).__init__(name_ip_tuple[0], name_ip_tuple[2])
        self.base_host = name_ip_tuple[1]

    def get_base_host(self):
        return self.base_host


class HostConfig(IPListConfig):
    def __init__(self, name_ip_tuple):
        super(HostConfig, self).__init__(name_ip_tuple[0], name_ip_tuple[2])
        self.linked_bridge = name_ip_tuple[1]
        self.extra_data = name_ip_tuple[3:]

    def get_linked_bridge(self):
        return self.linked_bridge

    def get_extra_data(self):
        return self.extra_data


class InterfaceConfig(IPListConfig):
    def __init__(self, iface_tuple):
        super(InterfaceConfig, self).__init__(iface_tuple[0], iface_tuple[2])
        self.far_host_name = iface_tuple[1][0]
        self.far_host_iface_name = iface_tuple[1][1]

    def get_far_host_name(self):
        return self.far_host_name

    def get_far_host_interface_name(self):
        return self.far_host_iface_name


class RouterConfig(ConfigObjectBase):
    def __init__(self, host_iface_tuple):
        super(RouterConfig, self).__init__(host_iface_tuple[0])
        self.interfaces = []
        for iface_def in host_iface_tuple[1]:
            self.interfaces.append(InterfaceConfig(iface_def))

    def get_interfaces(self):
        return self.interfaces


class VMConfig(ConfigObjectBase):
    def __init__(self, host_tuple):
        super(VMConfig, self).__init__(host_tuple[0])
        self.vm = HostConfig(host_tuple[1:])

    def get_vm(self):
        return self.vm
