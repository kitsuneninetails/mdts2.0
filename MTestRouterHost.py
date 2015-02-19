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

class RouterHost(Host):
    global_id = 0

    def __init__(self, name, cli, host_create_func, host_remove_func):
        super(RouterHost, self).__init__(name, cli, host_create_func, host_remove_func)
        self.num_id = str(RouterHost.global_id)
        RouterHost.global_id += 1

    def prepareFiles(self):
        etc_dir = '/etc/quagga.' + self.num_id
        var_lib_dir = '/var/lib/quagga.' + self.num_id
        var_log_dir = '/var/log/quagga.' + self.num_id
        var_run_dir = '/run.' + self.num_id + '/quagga'

        if not self.cli.exists(etc_dir):
            self.cli.cmd('mkdir -p ' + etc_dir)

        if not self.cli.exists(var_lib_dir):
            self.cli.cmd('mkdir -p ' + var_lib_dir)
            self.cli.cmd('chown -R quagga.quagga ' + var_lib_dir)

        if not self.cli.exists(var_log_dir):
            self.cli.cmd('mkdir -p ' + var_log_dir)
            self.cli.cmd('chown -R quagga.quagga ' + var_log_dir)

        if not self.cli.exists(var_run_dir):
            self.cli.cmd('mkdir -p ' + var_run_dir)
            self.cli.cmd('chown -R quagga.quagga ' + var_run_dir)

        if self.num_id is '0':
            self.cli.copy_dir('scripts/quagga.0', etc_dir)
        else:
            mmconf_file = etc_dir + '/midolman.conf'
            self.cli.copy_dir('scripts/quagga.1+', etc_dir)
            self.cli.regex_file(mmconf_file, 's/^\[midolman\]/\[midolman\]\\nbgp_keepalive=1/')
            self.cli.regex_file(mmconf_file, 's/^\[midolman\]/\[midolman\]\\nbgp_holdtime=3/')
            self.cli.regex_file(mmconf_file, 's/^\[midolman\]/\[midolman\]\\nbgp_connect_retry=1/')

    def print_config(self, indent=0):
        super(RouterHost, self).print_config(indent)
        print ('    ' * (indent + 1)) + 'Configured Interfaces:'
        for j in self.hwinterfaces:
            j.print_config(indent + 2)

    def start(self):
        self.cli.cmd_unshare('python ./MTestEnvConfigure control router '+ self.num_id + ' start')

    def stop(self):
        self.cli.cmd_unshare('python ./MTestEnvConfigure control router '+ self.num_id + ' stop')

    def mount_shares(self):
        self.cli.mount('/run.' + self.num_id, '/run')
        self.cli.mount('/var/log/quagga.' + self.num_id, '/var/log/quagga')
        self.cli.mount('/etc/quagga.' + self.num_id, '/etc/quagga')

    def control_start(self, *args):
        self.mount_shares()

        self.cli.cmd('/etc/init.d/quagga stop >/dev/null 2>&1 || true')
        self.cli.cmd("find /var/log/quagga -type f -exec sudo rm -f {} \; || true")
        self.cli.cmd('/etc/init.d/quagga start')

    def control_stop(self, *args):
        self.cli.cmd('/etc/init.d/quagga stop')


