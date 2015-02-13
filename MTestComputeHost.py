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

from MTestHost import Host
from MTestVMHost import VMHost
from MTestCLI import NetNSCLI, CREATENSCMD, REMOVENSCMD

class ComputeHost(Host):
    global_id = 1

    def __init__(self, name, cli, host_create_func, host_remove_func):
        super(ComputeHost, self).__init__(name, cli, host_create_func, host_remove_func)
        self.vms = []
        self.num_id = str(ComputeHost.global_id)
        ComputeHost.global_id += 1

    def prepareFiles(self):
        pass

    def create_vm(self, name):
        new_host = VMHost(name, NetNSCLI(name), CREATENSCMD, REMOVENSCMD)
        self.vms.append(new_host)
        return new_host

    def setup_vms(self):
        for host in self.vms:
            host.setup()
            self.setup_host_interfaces(host)

    def cleanup_vms(self):
        for host in self.vms:
            self.cleanup_interfaces(host)
            host.cleanup()

    def print_config(self, indent=0):
        super(ComputeHost, self).print_config(indent)
        print ('    ' * (indent + 1)) + 'Num ID [' + self.num_id + '], Hosting vms: '
        for vm in self.vms:
            vm.print_config(indent + 2)
            print ('    ' * (indent + 4)) + 'Interfaces:' 
            for i in self.get_interfaces_for_host(vm.get_name()):
                i.print_config(indent + 5)

    def prepareFiles(self):
        etc_dir = '/etc/midolman.' + self.num_id
        var_lib_dir = '/var/lib/midolman.' + self.num_id
        var_log_dir = '/var/lib/midolman.' + self.num_id

        self.cli.rm(etc_dir)
        self.cli.copy_dir('/etc/midolman', etc_dir)

	# generates host uuid
        host_uuid = """
# generated for MMM MM $n
host_uuid=00000000-0000-0000-0000-00000000000$n
"""
        huidfile = open(etc_dir + "/host_uuid.properties", "w+")
        print >>huidfile, host_uuid

        mmconf = etc_dir + '/midolman.conf'

        self.cli.regex_file(mmconf,
                            ('/^\[zookeeper\]/,/^$/ s/^zookeeper_hosts =.*$/zookeeper_hosts = '
                             '$ZOOKEEPER1_IP:2181,$ZOOKEEPER2_IP:2181,$ZOOKEEPER3_IP:2181/'))

        self.cli.regex_file(mmconf,
                            ('/^\[cassandra\]/,/^$/ s/^servers =.*$/servers = $CASSANDRA1_IP,$C'
                            'ASSANDRA2_IP,$CASSANDRA3_IP/;s/^replication_factor =.*$/replicatio'
                             'n_factor = 3/'))

        self.cli.regex_file(mmconf,
                            ('/^\[midolman\]/,/^\[/ s%^[# ]*bgpd_binary = /usr/lib/quagga.*$%bg'
                             'pd_binary = /usr/lib/quagga%'))

	if not self.cli.grep_file(mmconf, '\[haproxy_health_monitor\]'):
            hmoncfg = """
# Enable haproxy on the node.
[haproxy_health_monitor]
namespace_cleanup = true
health_monitor_enable = true
haproxy_file_loc = /etc/midolman.$i/l4lb/
"""
            mmcfgfile = open(mmconf, "a+")
            print >>mmcfgfile, hmoncfg
            
        lb = etc_dir + '/logback.xml'

        self.cli.regex_file(lb, 's/root level="INFO"/root level="DEBUG"/')
        self.cli.regex_file(lb, '/<rollingPolicy/, /<\/rollingPolicy/d')
        self.cli.regex_file(lb, 's/rolling.RollingFileAppender/FileAppender/g')

        self.cli.rm(var_lib_dir)
        self.cli.cmd('mkdir -p ' + var_lib_dir)

        self.cli.rm(var_log_dir)
        self.cli.cmd('mkdir -p ' + var_log_dir)

        mmenv = etcDir + '/midolman-env.sh'

	# Allow connecting via debugger - MM 1 listens on 1411, MM 2 on 1412, MM 3 on 1413
        self.cli.regex_file(mmenv, '/runjdwp/s/^..//g')
        self.cli.regex_file(mmenv, '/runjdwp/s/1414/141' + self.num_id + '/g')

	# Setting memory to the ones before
	# https://github.com/midokura/midonet/commit/65ace0e84265cd777b2855d15fce60148abd9330
        self.cli.regex_file(mmenv, 's/MAX_HEAP_SIZE=.*/MAX_HEAP_SIZE="300M"/')
        self.cli.regex_file(mmenv, 's/HEAP_NEWSIZE=.*/HEAP_NEWSIZE="200M"/')
