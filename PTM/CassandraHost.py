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
from MTestExceptions import *
import time


class CassandraHost(Host):
    global_id = 1

    def __init__(self, name, cli, host_create_func, host_remove_func):
        super(CassandraHost, self).__init__(name, cli, host_create_func, host_remove_func)
        self.cassandra_ips = []
        self.num_id = str(CassandraHost.global_id)
        CassandraHost.global_id += 1
        self.init_token = ''
        self.ip = ()
        
    def print_config(self, indent=0):
        super(CassandraHost, self).print_config(indent)
        print ('    ' * (indent + 1)) + 'Num-id: ' + self.num_id
        print ('    ' * (indent + 1)) + 'Init-token: ' + self.init_token
        print ('    ' * (indent + 1)) + 'Self-IP: ' + str(self.ip)
        print ('    ' * (indent + 1)) + 'Cassandra-IPs: ' + str(self.cassandra_ips)

    def prepare_files(self):
        if len(self.cassandra_ips) is not 0:
            seed_str = ''.join([str(ip[0]) + ',' for ip in self.cassandra_ips])[:-1]
        else:
            seed_str = ''

        etc_dir = '/etc/cassandra.' + self.num_id
        var_lib_dir = '/var/lib/cassandra.' + self.num_id
        var_log_dir = '/var/log/cassandra.' + self.num_id
        var_run_dir = '/run/cassandra.' + self.num_id

        self.cli.rm(etc_dir)
        self.cli.copy_dir('/etc/cassandra', etc_dir)

        # Work around for https://issues.apache.org/jira/browse/CASSANDRA-5895
        self.cli.regex_file(etc_dir + '/cassandra-env.sh', 's/-Xss[1-9][0-9]*k/-Xss228k/')
        self.cli.regex_file_multi(etc_dir + '/cassandra.yaml',
                                  "s/^cluster_name:.*$/cluster_name: 'midonet'/",
                                  's/^initial_token:.*$/initial_token: ' + self.init_token + '/',
                                  "/^seed_provider:/,/^$/ s/seeds:.*$/seeds: '" + seed_str + "'/",
                                  's/^listen_address:.*$/listen_address: ' + self.ip[0] + '/',
                                  's/^rpc_address:.*$/rpc_address: ' + self.ip[0] + '/')

        self.cli.rm(var_lib_dir)
        self.cli.mkdir(var_lib_dir)
        self.cli.chown(var_lib_dir, 'cassandra', 'cassandra')

        self.cli.rm(var_log_dir)
        self.cli.mkdir(var_log_dir)
        self.cli.chown(var_log_dir, 'cassandra', 'cassandra')

        self.cli.rm(var_run_dir)
        self.cli.mkdir(var_run_dir)
        self.cli.chown(var_run_dir, 'cassandra', 'cassandra')

    def start(self):
        self.cli.cmd_unshare('python ./MTestEnvConfigure.py control cassandra ' + self.num_id + ' start')
        
        # Wait a couple seconds for the process to start before polling nodetool
        time.sleep(2)
        # Checking Cassandra status
        retries = 0
        max_retries = 10
        connected = False
        while not connected:
            if self.cli.oscmd('nodetool -h ' + self.ip[0] + ' status') == 0:
                connected = True
            else:
                retries += 1
                if retries > max_retries:
                    raise SocketException('Zookeeper host ' + self.num_id + ' timed out while starting')
                time.sleep(2)

    def stop(self):
        self.cli.cmd_unshare('python ./MTestEnvConfigure.py control cassandra ' + self.num_id + ' stop')

    def mount_shares(self):
        self.cli.mount('/run/cassandra.' + self.num_id, '/run/cassandra')
        self.cli.mount('/var/lib/cassandra.' + self.num_id, '/var/lib/cassandra')
        self.cli.mount('/var/log/cassandra.' + self.num_id, '/var/log/cassandra')
        self.cli.mount('/etc/cassandra.' + self.num_id, '/etc/cassandra')

    def unmount_shares(self):
        self.cli.unmount('/run/cassandra')
        self.cli.unmount('/var/lib/cassandra')
        self.cli.unmount('/var/log/cassandra')
        self.cli.unmount('/etc/cassandra')

    def control_start(self, *args):
        self.cli.rm_files('/var/log/cassandra')
        self.cli.cmd('/bin/bash -c "MAX_HEAP_SIZE=128M HEAP_NEWSIZE=64M /etc/init.d/cassandra start"')

    def control_stop(self, *args):
        self.cli.cmd("/etc/init.d/cassandra stop")