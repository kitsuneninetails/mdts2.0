#!/usr/bin/env python
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

import sys

from PTM.Exceptions import *
from PTM.MapConfigReader import MapConfigReader
from PTM.RootServer import RootServer

GlobalConfig = {
    'bridges':
    [
        {'name': 'br0', 'ip_list': [{'ip': '10.0.0.240', 'subnet': '24'}]},
        {'name': 'brv0', 'options': 'stp'},
    ],
    'zookeepers':
    [
        {'name': 'zoo1',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.2', 'subnet': '24'}]}]},
        {'name': 'zoo2',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.3', 'subnet': '24'}]}]},
        {'name': 'zoo3',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.4', 'subnet': '24'}]}]},
    ],
    'cassandras':
    [
        {'name': 'cass1',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.5', 'subnet': '24'}]}],
         'options': '56713727820156410577229101238628035242'},
        {'name': 'cass2',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.6', 'subnet': '24'}]}],
         'options': '113427455640312821154458202477256070484'},
        {'name': 'cass3',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.7', 'subnet': '24'}]}],
         'options': '170141183460469231731687303715884105726'},
    ],
    'computes':
    [
        {'name': 'cmp1',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.8', 'subnet': '24'}]}]},
        {'name': 'cmp2',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.9', 'subnet': '24'}]}]},
        {'name': 'cmp3',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'br0'},
               'ip_list': [{'ip': '10.0.0.10', 'subnet': '24'}]}]},
    ],
    'routers':
    [
        {'name': 'quagga',
         'peer_interface_list':
             [{'near_interface':
                   {'name': 'eth0',
                    'ip_list': [{'ip': '10.0.1.240', 'subnet': '16'}]},
               'target_interface': {'host': 'cmp1', 'interface_name': 'eth1'}},
              {'near_interface':
                   {'name': 'eth1',
                    'ip_list': [{'ip': '10.0.1.240', 'subnet': '16'}]},
               'target_interface': {'host': 'cmp2', 'interface_name': 'eth1'}},
              ]}
    ],
    'hosted_vms':
    [
    ],
    'hosts':
    [
        {'name': 'v1.1',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'brv0'}}]},
        {'name': 'v1.2',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'brv0'}}]},
        {'name': 'v2.1',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'brv0'}}]},
        {'name': 'v2.2',
         'interface_list':
             [{'name': 'eth0',
               'bridge_link': {'name': 'brv0'}}]},
    ],
    'vlans':
    [
        {'vlan_id': '1',
         'host_list':
             [{'name': 'v1.1',
               'interface_list':
                   [{'name': 'eth0', 'ip_list': [{'ip': '172.16.0.224', 'subnet': '24'}]},
                    {'name': 'eth1', 'ip_list': [{'ip': '172.16.0.223', 'subnet': '24'}]}]},
              {'name': 'v2.1',
               'interface_list':
                   [{'name': 'eth0', 'ip_list': [{'ip': '172.16.0.225', 'subnet': '24'}]}]}]},
        {'vlan_id': '2',
         'host_list':
             [{'name': 'v1.2',
               'interface_list':
                   [{'name': 'eth0', 'ip_list': [{'ip': '172.16.0.224', 'subnet': '24'}]}]},
              {'name': 'v2.2',
               'interface_list':
                   [{'name': 'eth0', 'ip_list': [{'ip': '172.16.0.225', 'subnet': '24'}]}]}]},
    ],
}

try:

    if len(sys.argv) < 2:
        print 'Usage: EnvConfigure {boot|init|start|stop|shutdown|config} [options]'
        raise ExitCleanException()
    else:
        cmd = sys.argv[1]

        config = MapConfigReader.get_physical_topology_config(GlobalConfig)
        os_host = RootServer.create_from_physical_topology_config(config)
        os_host.init()

        if cmd == 'boot':
            os_host.setup()
        elif cmd == 'init':
            os_host.prepare_files()
        elif cmd == 'start':
            os_host.start()
        elif cmd == 'stop':
            os_host.stop()
        elif cmd == 'shutdown':
            os_host.cleanup()
        elif cmd == 'config':
            os_host.print_config()
        elif cmd == 'control':
            os_host.control(*sys.argv[2:])
        else:
            raise ArgMismatchException(' '.join(sys.argv[1:]))
   
except ExitCleanException:
    exit(1)
except ArgMismatchException as a:
    print 'Argument mismatch: ' + str(a)
    print 'Usage: EnvConfigure {boot|init|start|stop|shutdown|config} [options]'
    exit(2)
except ObjectNotFoundException as e:
    print 'Object not found: ' + str(e)
    exit(2)
