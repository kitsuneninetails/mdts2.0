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

import re
import time
import sys

from MTestExceptions import *
from MTestRootServer import RootServer
from MTestCLI import LinuxCLI, NetNSCLI
from MTestNetworkObject import NetworkObject
from MTestBridge import Bridge
from MTestInterface import Interface
from MTestVirtualInterface import VirtualInterface

GlobalConfig = {
    'bridges' :
    [
        ( 'br0' , '', [ ('10.0.0.240', '24') ] )
    ],
    'zookeeper' : 
    [
        ( 'zoo1' , 'br0', [ ('10.0.0.2','24') ] ),
        ( 'zoo2' , 'br0', [ ('10.0.0.3','24') ] ),
        ( 'zoo3' , 'br0', [ ('10.0.0.4','24') ] ),
    ],
    'cassandra' :
    [
        ( 'cass1' , 'br0', [ ('10.0.0.5','24') ] ),
        ( 'cass2' , 'br0', [ ('10.0.0.6','24') ] ),
        ( 'cass3' , 'br0', [ ('10.0.0.7','24') ] ), 
    ],
    'compute' :
    [
        ( 'cmp1' , 'br0', [ ('10.0.0.8','24') ] ),
        ( 'cmp2' , 'br0', [ ('10.0.0.9','24') ] ),
        ( 'cmp3' , 'br0', [ ('10.0.0.10','24') ] ), 
    ],
    'routers' :
    [
        ( 'quagga' , 
          [ ( 'eth0', ('cmp1','eth1'), [ ('10.0.1.240','16') ] ), 
            ( 'eth1', ('cmp2','eth1'), [ ('10.0.2.240','16') ] ) ] )
    ],
    'hosted_vms' :
    [
        ( 'cmp1', 'vm1_0', '', [ ('172.16.0.1','24') ] ),
        ( 'cmp2', 'vm2_0', '', [ ('172.16.0.2','24') ] ),
        ( 'cmp2', 'vm2_1', '', [ ('172.16.0.1','24') ] ),
        ( 'cmp2', 'vm2_2', '', [ ('172.16.0.2','24') ] ),
        ( 'cmp3', 'vm3_0', '', [ ('172.16.0.1','24') ] )
    ],
    'vlans' :
    {
    }
}

#VM_GW_IP=172.16.0.240


if len(sys.argv) < 2:
    print 'Usage: python MTestEnvConfigure {boot|init|start|stop|config}'
    exit(-1)
else:
    cmd = sys.argv[1]

if cmd == 'boot':
    os_host = RootServer()
    os_host.init(GlobalConfig)
    os_host.setup()
if cmd == 'init':
    os_host = RootServer()
    os_host.init(GlobalConfig)
    os_host.prepareFiles()
elif cmd == 'stop':
    os_host = RootServer()
    os_host.init(GlobalConfig)
    os_host.cleanup()
elif cmd == 'config':
    os_host = RootServer()
    os_host.init(GlobalConfig)
    os_host.print_config()
    
    

