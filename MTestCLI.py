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

DEBUG=False

CREATENSCMD = lambda name: LinuxCLI().cmd('ip netns add ' + name)
REMOVENSCMD = lambda name: LinuxCLI().cmd('ip netns del ' + name)

class LinuxCLI(object):
    def cmd(self, cmd_line, return_output = False, dbg = DEBUG):
        if dbg is True:
            cmd = "echo '" + self.create_cmd(cmd_line) + "'"
            return 0
        else:
            cmd = self.create_cmd(cmd_line)
            print '>>> ' + cmd
            if return_output is False:
                return subprocess.call(cmd, shell=True)
            else:
                try:
                    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    return p.stdout.readline()
                except subprocess.CalledProcessError:
                    return -1

    def create_cmd(self, cmd_line):
        return 'sudo ' + cmd_line
        
    def oscmd(self, cmd_line):
        return LinuxCLI().cmd(cmd_line)

    def grep_file(self, file, grep):
        if LinuxCLI().cmd('grep -q ' + grep + ' ' + file) == 0:
            return True
        else:
            return False

    def grep_cmd(self, cmd_line, grep):
        if self.cmd(cmd_line + '| grep -q ' + grep) == 0:
            return True
        else:
            return False

    def mkdir(self, dir_name):
        return LinuxCLI().cmd('mkdir -p ' + dir_name)

    def chown(self, file_name, user_name, group_name):
        return LinuxCLI().cmd('chown -R ' + user_name + '.' + group_name + ' ' + file_name)        

    def regex_file(self, file, regex):
        return LinuxCLI().cmd('sed -e "' + regex + '" -i ' + file)

    def regex_file_multi(self, file, *args):
        sed_str = ''.join(['-e "' + str(i) + '" ' for i in args])
        return LinuxCLI().cmd('sed ' + sed_str + ' -i ' + file)

    def copy_dir(self, old_dir, new_dir):
        return LinuxCLI().cmd('cp -RL --preserve=all ' + old_dir + ' ' + new_dir)

    def copy_file(self, old_file, new_file):
        return LinuxCLI().cmd('cp ' + old_file + ' ' + new_file)

    def read_from_file(self, file_name):
        file_ptr = open(file_name, 'r')
        return file_ptr.read()
        
    def write_to_file(self, file, data, append=False):
        mode = 'w'
        self.rm("./.tmp.file")
        if append is True:
            self.copy_file(file, "./.tmp.file")
            mode = 'a'
        file_ptr = open("./.tmp.file", mode)
        file_ptr.write(data)
        file_ptr.close()
        return self.copy_file('./.tmp.file', file)

    def rm(self, old_file):
        return LinuxCLI().cmd('rm -rf ' + old_file)
    
    def rm_files(self, root_dir, match_pattern = ''):
        if match_pattern == '':
            return LinuxCLI().cmd('find ' + root_dir + ' -type f -exec sudo rm -f {} \; || true')
        else:
            return LinuxCLI().cmd('find ' + root_dir + ' -name ' + match_pattern + ' -exec sudo rm -f {} \; || true')

    def exists(self, file):
        return os.path.exists(file)

    def mount(self, drive, as_drive):
        return LinuxCLI().cmd('mount --bind ' + drive + ' ' + as_drive)

    def unmount(self, drive):
        return LinuxCLI().cmd('umount -l ' + drive + " > /dev/null 2>&1")

    def start_screen(self, host, window_name, cmd_line):
        cmd_in_screen = self.create_cmd(cmd_line)
        if LinuxCLI().grep_cmd('screen -ls', host) is False:
            # first screen = main screen
            cmd_opts = '-d -m -S ' + host
        else:
            # subsequent screens = sub screens
            cmd_opts = '-S ' + host + ' -X screen'
        return LinuxCLI().cmd('screen ' + cmd_opts + ' -t ' + window_name + ' /bin/bash -c "' + cmd_in_screen + '"')

    def start_screen_unshare(self, host, window_name, cmd_line):
        return self.start_screen(host, window_name, 'unshare -m ' + cmd_line)

    def cmd_unshare(self, cmd_line):
        return LinuxCLI().cmd('unshare --mount -- /bin/bash -x -c "' + cmd_line + '"')

class NetNSCLI(LinuxCLI):
    def __init__(self, name):
        self.name = name

    def create_cmd(self, cmd_line):
        return super(NetNSCLI, self).create_cmd('ip netns exec ' + self.name + ' ' + cmd_line)
