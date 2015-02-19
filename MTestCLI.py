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
    def cmd(self, cmd_line, dbg = DEBUG):
        if dbg is True:
            cmd = "echo '" + self.create_cmd(cmd_line) + "'"
        else:
            cmd = self.create_cmd(cmd_line)
        return subprocess.call(cmd, shell=True)

    def create_cmd(self, cmd_line):
        return 'sudo ' + cmd_line
        
    def grep_file(self, file, grep):
        if self.cmd('grep -q ' + grep + ' ' + file) is 0:
            return True
        else:
            return False

    def grep_cmd(self, cmd_line, grep):
        if self.cmd(cmd_line + '| grep -q ' + grep) is 0:
            return True
        else:
            return False

    def regex_file(self, file, regex):
        self.cmd('sed -e "' + regex + '" -i ' + file)

    def regex_file_multi(self, file, *args):
        sed_str = ''.join(['-e "' + str(i) + '"' for i in args])
        self.cmd('sed ' + sed_str + '" -i ' + file)

    def copy_dir(self, old_dir, new_dir):
        self.cmd('cp -RL --preserve=all ' + old_dir + ' ' + new_dir)

    def copy_file(self, old_file, new_file):
        self.cmd('cp ' + old_file + ' ' + new_file)

    def rm(self, old_file):
        self.cmd('rm -rf ' + old_file)

    def exists(self, file):
        return os.path.exists(file)

    def mount(self, drive, as_drive):
        self.cmd('mount --bind ' + drive + ' ' + as_drive)

    def start_screen(self, host, window_name, cmd_line):
        cmd_in_screen = self.create_cmd(cmd_line)
        if LinuxCLI().grep_cmd('screen -ls', host) is False:
            # first screen = main screen
            cmd_opts = '-d -m -S ' + host
        else:
            # subsequent screens = sub screens
            cmd_opts = '-S ' + host + ' -X screen'
        LinuxCLI().cmd('screen ' + cmd_opts + ' -t ' + window_name + ' /bin/bash -c "' + cmd_in_screen + '"')

    def start_screen_unshare(self, host, window_name, cmd_line):
        self.start_screen(host, window_name, 'unshare -m ' + cmd_line)

    def cmd_unshare(self, cmd_line):
        self.cmd('unshare -m ' + cmd_line)

class NetNSCLI(LinuxCLI):
    def __init__(self, name):
        self.name = name

    def create_cmd(self, cmd_line):
        return super(NetNSCLI, self).create_cmd('ip netns exec ' + self.name + ' ' + cmd_line)
