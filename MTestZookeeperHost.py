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
from MTestCLI import LinuxCLI

class ZookeeperHost(Host):
    global_id = 1
    
    def __init__(self, name, cli, host_create_func, host_remove_func):
        super(ZookeeperHost, self).__init__(name, cli, host_create_func, host_remove_func)
        self.zookeeper_ips = []
        self.num_id = str(ZookeeperHost.global_id)
        ZookeeperHost.global_id += 1
        self.ip = ()

    def print_config(self, indent=0):
        super(ZookeeperHost, self).print_config(indent)
        print ('    ' * (indent + 1)) + 'Num-id: ' + self.num_id
        print ('    ' * (indent + 1)) + 'Self-IP: ' + str(self.ip)
        print ('    ' * (indent + 1)) + 'Zookeeper-IPs: ' + str(self.zookeeper_ips)

    def prepareFiles(self):
        var_lib_dir = '/var/lib/zookeeper.' + self.num_id
        var_log_dir = '/var/log/zookeeper.' + self.num_id
        var_run_dir = '/run.' + self.num_id + '/zookeeper'

        LinuxCLI().rm(var_lib_dir)
        LinuxCLI().cmd('mkdir -p ' + var_lib_dir + '/data')
        LinuxCLI().write_to_file(var_lib_dir + '/data/myid', self.num_id, False)
        LinuxCLI().write_to_file(var_lib_dir + '/myid', self.num_id, False)
        LinuxCLI().cmd('chown -R zookeeper.zookeeper ' + var_lib_dir)

        LinuxCLI().rm(var_log_dir)
        LinuxCLI().cmd('mkdir -p ' + var_log_dir)
        LinuxCLI().cmd('chown -R zookeeper.zookeeper ' + var_log_dir)

        LinuxCLI().rm(var_run_dir)
        LinuxCLI().cmd('mkdir -p ' + var_run_dir)
        LinuxCLI().cmd('chown -R zookeeper.zookeeper ' + var_run_dir)

    def start(self):
        self.cli.cmd_unshare('python ./MTestEnvConfigure control zookeeper '+ self.num_id + ' start')

        # Checking Zookeeper status
        retries = 0
        max_retries = 1
        while not self.cli.grep_cmd('echo ruok | nc ' + self.ip[0] + ' 2181', 'imok'):
            retries += 1
            if retries > max_retries:
                print 'Zookeeper host ' + self.num_id + ' timed out while starting'
                return
            time.sleep(5)

    def stop(self):
        self.cli.cmd_unshare('python ./MTestEnvConfigure control zookeeper '+ self.num_id + ' stop')

    def mount_shares(self):
        self.cli.mount('/run.' + self.num_id, '/run')
        self.cli.mount('/var/lib/zookeeper.' + self.num_id, '/var/lib/zookeeper')
        self.cli.mount('/var/log/zookeeper.' + self.num_id, '/var/log/zookeeper')
        self.cli.mount('/etc/zookeeper.' + self.num_id, '/etc/zookeeper')

    def control_start(self, *args):
        self.mount_shares()

        self.cli.cmd("find /var/log/zookeeper -type f -exec sudo rm -f {} \; || true")
        self.cli.cmd("/etc/init.d/zookeeper start")

    def control_stop(self, *args):
        self.mount_shares()

        self.cli.cmd("/etc/init.d/zookeeper stop")


