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
from MTestCLI import LinuxCLI, NetNSCLI, CREATENSCMD, REMOVENSCMD

class ComputeHost(Host):
    global_id = 1

    def __init__(self, name, cli, host_create_func, host_remove_func):
        super(ComputeHost, self).__init__(name, cli, host_create_func, host_remove_func)
        self.vms = []
        self.num_id = str(ComputeHost.global_id)
        ComputeHost.global_id += 1
        self.zookeeper_ips = []
        self.cassandra_ips = []

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
        print ('    ' * (indent + 1)) + 'Num-id: ' + self.num_id
        print ('    ' * (indent + 1)) + 'Zookeeper-IPs: ' + str(self.zookeeper_ips)
        print ('    ' * (indent + 1)) + 'Cassandra-IPs: ' + str(self.cassandra_ips)
        print ('    ' * (indent + 1)) + 'Hosted vms: '
        for vm in self.vms:
            vm.print_config(indent + 2)
            print ('    ' * (indent + 4)) + 'Interfaces:' 
            for i in self.get_interfaces_for_host(vm.get_name()):
                i.print_config(indent + 5)

    def prepareFiles(self):
        etc_dir = '/etc/midolman.' + self.num_id
        var_lib_dir = '/var/lib/midolman.' + self.num_id
        var_log_dir = '/var/lib/midolman.' + self.num_id

        LinuxCLI().rm(etc_dir)
        LinuxCLI().copy_dir('/etc/midolman', etc_dir)

	# generates host uuid
        host_uuid = ('# generated for MMM MM $n\n'
                     'host_uuid=00000000-0000-0000-0000-00000000000$n')
        LinuxCLI().write_to_file(etc_dir + '/host_uuid.properties', host_uuid, False)

        mmconf = etc_dir + '/midolman.conf'

        if len(self.zookeeper_ips) is not 0:
            z_ip_str = ''.join([str(ip[0]) + ':2181,' for ip in self.zookeeper_ips])[:-1]
        else :
            z_ip_str = ''

        if len(self.cassandra_ips) is not 0:
            c_ip_str = ''.join([str(ip[0]) + ',' for ip in self.cassandra_ips])[:-1]
        else :
            c_ip_str = ''

        LinuxCLI().regex_file(mmconf,
                            '/^\[zookeeper\]/,/^$/ s/^zookeeper_hosts =.*$/zookeeper_hosts = ' + \
                             z_ip_str + '/')

        LinuxCLI().regex_file(mmconf,
                            '/^\[cassandra\]/,/^$/ s/^servers =.*$/servers = ' + \
                             c_ip_str + '/;s/^replication_factor =.*$/replication_factor = 3/')

        LinuxCLI().regex_file(mmconf,
                            ('/^\[midolman\]/,/^\[/ s%^[# ]*bgpd_binary = /usr/lib/quagga.*$%bg'
                             'pd_binary = /usr/lib/quagga%'))

	if not LinuxCLI().grep_file(mmconf, '\[haproxy_health_monitor\]'):
            hmoncfg = ('# Enable haproxy on the node.\n'
                       '[haproxy_health_monitor]\n'
                       'namespace_cleanup = true\n'
                       'health_monitor_enable = true\n'
                       'haproxy_file_loc =')  + etc_dir + '/l4lb/\n'
            LinuxCLI().write_to_file(mmconf, hmoncfg, True)

        lb = etc_dir + '/logback.xml'

        LinuxCLI().regex_file(lb, 's/root level="INFO"/root level="DEBUG"/')
        LinuxCLI().regex_file(lb, '/<rollingPolicy/, /<\/rollingPolicy/d')
        LinuxCLI().regex_file(lb, 's/rolling.RollingFileAppender/FileAppender/g')

        LinuxCLI().rm(var_lib_dir)
        LinuxCLI().cmd('mkdir -p ' + var_lib_dir)

        LinuxCLI().rm(var_log_dir)
        LinuxCLI().cmd('mkdir -p ' + var_log_dir)

        mmenv = etc_dir + '/midolman-env.sh'

	# Allow connecting via debugger - MM 1 listens on 1411, MM 2 on 1412, MM 3 on 1413
        LinuxCLI().regex_file(mmenv, '/runjdwp/s/^..//g')
        LinuxCLI().regex_file(mmenv, '/runjdwp/s/1414/141' + self.num_id + '/g')

	# Setting memory to the ones before
	# https://github.com/midokura/midonet/commit/65ace0e84265cd777b2855d15fce60148abd9330
        LinuxCLI().regex_file(mmenv, 's/MAX_HEAP_SIZE=.*/MAX_HEAP_SIZE="300M"/')
        LinuxCLI().regex_file(mmenv, 's/HEAP_NEWSIZE=.*/HEAP_NEWSIZE="200M"/')

    def start(self):
        if self.num_id == '1':
            self.cli.cmd('dnsmasq --no-host --no-resolv -S 8.8.8.8')
       
        self.cli.cmd_unshare('python ./MTestEnvConfigure control compute '+ self.num_id + ' start')

    def stop(self):
        self.cli.cmd_unshare('python ./MTestEnvConfigure control compute '+ self.num_id + ' stop')

    def mount_shares(self):
        self.cli.mount('/run.' + self.num_id, '/run')
        self.cli.mount('/var/lib/midolman.' + self.num_id, '/var/lib/midolman')
        self.cli.mount('/var/log/midolman.' + self.num_id, '/var/log/midolman')
        self.cli.mount('/etc/midolman.' + self.num_id, '/etc/midolman')

    def control_start(self, *args):
        self.mount_shares()

        self.cli.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        self.cli.cmd('start midolman')

    def control_stop(self, *args):
        self.mount_shares()
        self.cli.cmd('stop midolman')

    def start_vms(self):
        for host in self.vms:
            host.start()

    def stop_vms(self):
        for host in self.vms:
            host.stop()

