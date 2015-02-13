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

import os
import subprocess

DEBUG=True

CREATENSCMD = lambda name: LinuxCLI().cmd('ip netns add ' + name)
REMOVENSCMD = lambda name: LinuxCLI().cmd('ip netns del ' + name)

class LinuxCLI(object):
    def cmd(self, cmd_line):
        if DEBUG is True:
            return subprocess.call('echo "sudo ' + cmd_line + '"', shell=True)
        else:
            return subprocess.call('bash -x -c "sudo ' + cmd_line + '"', shell=True)

    def grep_file(self, file, grep):
        if self.cmd('grep -q ' + grep + ' ' + file) == 0:
            return True
        else:
            return False

    def regex_file(self, file, regex):
        self.cmd('sed -e "' + regex + '" -i ' + file)

    def copy_dir(self, old_dir, new_dir):
        self.cmd('cp -RL --preserve=all ' + old_dir + ' ' + new_dir)

    def copy_file(self, old_file, new_file):
        self.cmd('cp ' + old_file + ' ' + new_file)

    def rm(self, old_file):
        self.cmd('rm -rf ' + old_file)

    def exists(self, file):
        return os.path.exists(file)

class NetNSCLI(LinuxCLI):
    def __init__(self, name):
        self.name = name
    def cmd(self, cmd_line):
        super(NetNSCLI, self).cmd('ip netns exec ' + self.name + ' ' + cmd_line)
