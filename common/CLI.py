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

DEBUG = False

CREATENSCMD = lambda name: LinuxCLI().cmd('ip netns add ' + name)
REMOVENSCMD = lambda name: LinuxCLI().cmd('ip netns del ' + name)
CONTROL_CMD_NAME = './mdts-ctl.py'


class LinuxCLI(object):
    def __init__(self, priv=True, debug=False):
        self.env_map = None
        """ :type: dict[str, str]"""
        self.priv = priv
        """ :type: bool"""
        self.debug = debug
        """ :type: bool"""

    def add_environment_variable(self, name, val):
        if (self.env_map is None):
            self.env_map = {}
        self.env_map[name] = val

    def remove_environment_variable(self, name):
        if (self.env_map is not None):
            self.env_map.pop(name)

    def cmd(self, cmd_line, return_output=False):
        if self.debug is True:
            cmd = "echo '" + self.create_cmd(cmd_line) + "'"
        else:
            if self.priv is True:
                cmd = self.create_cmd_priv(cmd_line)
            else:
                cmd = self.create_cmd(cmd_line)
        print '>>> ' + cmd
        if self.debug is True or return_output is False:
            return subprocess.call(cmd, shell=True, env=self.env_map)
        else:
            try:
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, env=self.env_map)
                return p.stdout.readline()
            except subprocess.CalledProcessError:
                return -1

    def create_cmd(self, cmd_line):
        return cmd_line

    def create_cmd_priv(self, cmd_line):
        return 'sudo ' + cmd_line

    @staticmethod
    def oscmd(cmd_line):
        return LinuxCLI().cmd(cmd_line)

    @staticmethod
    def grep_file(gfile, grep):
        if LinuxCLI().cmd('grep -q ' + grep + ' ' + gfile) == 0:
            return True
        else:
            return False

    def grep_cmd(self, cmd_line, grep):
        if self.cmd(cmd_line + '| grep -q ' + grep) == 0:
            return True
        else:
            return False

    @staticmethod
    def mkdir(dir_name):
        return LinuxCLI().cmd('mkdir -p ' + dir_name)

    @staticmethod
    def chown(file_name, user_name, group_name):
        return LinuxCLI().cmd('chown -R ' + user_name + '.' + group_name + ' ' + file_name)        

    @staticmethod
    def regex_file(rfile, regex):
        return LinuxCLI().cmd('sed -e "' + regex + '" -i ' + rfile)

    @staticmethod
    def regex_file_multi(rfile, *args):
        sed_str = ''.join(['-e "' + str(i) + '" ' for i in args])
        return LinuxCLI().cmd('sed ' + sed_str + ' -i ' + rfile)

    @staticmethod
    def copy_dir(old_dir, new_dir):
        return LinuxCLI().cmd('cp -RL --preserve=all ' + old_dir + ' ' + new_dir)

    @staticmethod
    def copy_file(old_file, new_file):
        return LinuxCLI().cmd('cp ' + old_file + ' ' + new_file)

    @staticmethod
    def read_from_file(file_name):
        file_ptr = open(file_name, 'r')
        return file_ptr.read()
        
    def write_to_file(self, wfile, data, append=False):
        mode = 'w'
        self.rm("./.tmp.file")
        if append is True:
            self.copy_file(wfile, "./.tmp.file")
            mode = 'a'
        file_ptr = open("./.tmp.file", mode)
        file_ptr.write(data)
        file_ptr.close()
        return self.copy_file('./.tmp.file', wfile)

    @staticmethod
    def rm(old_file):
        return LinuxCLI().cmd('rm -rf ' + old_file)
    
    @staticmethod
    def rm_files(root_dir, match_pattern=''):
        if match_pattern == '':
            return LinuxCLI().cmd('find ' + root_dir + ' -type f -exec sudo rm -f {} \; || true')
        else:
            return LinuxCLI().cmd('find ' + root_dir + ' -name ' + match_pattern + ' -exec sudo rm -f {} \; || true')

    @staticmethod
    def exists(efile):
        return os.path.exists(efile)

    @staticmethod
    def mount(drive, as_drive):
        return LinuxCLI().cmd('mount --bind ' + drive + ' ' + as_drive)

    @staticmethod
    def unmount(drive):
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

    @staticmethod
    def cmd_unshare(cmd_line):
        return LinuxCLI().cmd('unshare --mount -- /bin/bash -x -c "' + cmd_line + '"')

    @staticmethod
    def cmd_unshare_control(cmd_line):
        return LinuxCLI().cmd_unshare('PYTHONPATH=.. python -u ' + CONTROL_CMD_NAME + ' ' + cmd_line)


class NetNSCLI(LinuxCLI):
    def __init__(self, name):
        self.name = name

    def create_cmd(self, cmd_line):
        return super(NetNSCLI, self).create_cmd('ip netns exec ' + self.name + ' ' + cmd_line)

    def create_cmd_priv(self, cmd_line):
        return super(NetNSCLI, self).create_cmd_priv('ip netns exec ' + self.name + ' ' + cmd_line)
