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

class NetworkHost(Host):
    def __init__(self, name, cli, host_create_func, host_remove_func):
        super(NetworkHost, self).__init__(name, cli, host_create_func, host_remove_func)
        self.zookeeper_ips = []

    def print_config(self, indent=0):
        super(NetworkHost, self).print_config(indent)
        print ('    ' * (indent + 1)) + 'Zookeeper-IPs: ' + str(self.zookeeper_ips)

    def prepareFiles(self):

        if len(self.zookeeper_ips) is not 0:
            ip_str = ''.join([str(ip[0]) + ':2181,' for ip in self.zookeeper_ips])[:-1]
        else :
            ip_str = ''

        self.cli.regex_file('/usr/share/midonet-api/WEB-INF/web.xml', 
                            's/\(127.0.0.1:2181\|' + str(self.zookeeper_ips[0][0]) + \
                            ':2181[^<]*\)/' + ip_str + '/')

        if self.cli.grep_file('zookeeper-curator_enabled', '/usr/share/midonet-api/WEB-INF/web.xml'):
            self.cli.regex_file('/usr/share/midonet-api/WEB-INF/web.xml',
                                ('s/<param-name>zookeeper-zookeeper_hosts<\/param-name>/<param-name>'
                                'zookeeper-curator_enabled<\/param-name>\n    <param-value>true<\/p'
                                'aram-value>\n  <\/context-param>\n  <context-param>\n    <param-na'
                                'me>zookeeper-zookeeper_hosts<\/param-name>/'))

        self.cli.regex_file('/usr/share/midonet-api/WEB-INF/web.xml',
                            ('s/org.midonet.api.auth.keystone.v2_0.KeystoneService/org.midonet.api.a'
                            'uth.MockAuthService/g'))

        self.cli.copy_dir('$MIDONET_SRC_DIR/midonet-api/conf/midonet-api.xml',
                          '/etc/tomcat7/Catalina/localhost/midonet-api.xml')

        if not self.cli.grep_file("/etc/default/tomcat7", "java.security.egd"):
            self.cli.regex_file('/etc/default/tomcat7', 
                                '$aJAVA_OPTS="$JAVA_OPTS -Djava.security.egd=file:/dev/./urandom"')

        if self.cli.exists('/var/www/html/midonet-cp/config.js'):
            self.cli.regex_file('/var/www/html/midonet-cp/config.js',
                                ('s%https://example.com/midonet-api%http://$public:8080/midonet-api%'
                                'g;s/example.com/$public:8443/g'))
        elif self.cli.exists('/var/www/midonet-cp/config.js'):
            self.cli.regex_file('/var/www/midonet-cp/config.js',
                                ('s%https://example.com/midonet-api%http://$public:8080/midonet-api%'
                                'g;s/example.com/$public:8443/g'))

    def start(self):
        pass

    def stop(self):
        pass
