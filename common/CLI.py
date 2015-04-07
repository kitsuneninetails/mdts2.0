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
from common.Exceptions import *

CREATENSCMD = lambda name: LinuxCLI().cmd('ip netns add ' + name)
REMOVENSCMD = lambda name: LinuxCLI().cmd('ip netns del ' + name)
CONTROL_CMD_NAME = './mdts-ctl.py'


class LinuxCLI(object):
    def __init__(self, priv=True, debug=False, print_cmd=False):
        self.env_map = None
        """ :type: dict[str, str]"""
        self.priv = priv
        """ :type: bool"""
        self.debug = debug
        """ :type: bool"""
        self.print_cmd = print_cmd
        """ :type: bool"""

    def add_environment_variable(self, name, val):
        if (self.env_map is None):
            self.env_map = {}
        self.env_map[name] = val

    def remove_environment_variable(self, name):
        if (self.env_map is not None):
            self.env_map.pop(name)

    def cmd(self, cmd_line, return_output=False, timeout=None):
        new_cmd_line = ('timeout ' + str(timeout) if timeout is not None else '') + cmd_line

        if self.priv is True:
            cmd = self.create_cmd_priv(new_cmd_line)
        else:
            cmd = self.create_cmd(new_cmd_line)

        if self.print_cmd is True:
            print '>>> ' + cmd

        if self.debug is True:
            return cmd

        if return_output is False:
            return subprocess.call(cmd, shell=True, env=self.env_map)

        try:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, env=self.env_map)
            return p.stdout.readline()
        except subprocess.CalledProcessError:
            return -1

    def create_cmd(self, cmd_line):
        return cmd_line

    def create_cmd_priv(self, cmd_line):
        return 'sudo ' + cmd_line

    def oscmd(self, cmd_line):
        return self.cmd(cmd_line)

    @staticmethod
    def grep_file(self, gfile, grep):
        if self.cmd('grep -q ' + grep + ' ' + gfile) == 0:
            return True
        else:
            return False

    def grep_cmd(self, cmd_line, grep):
        if self.cmd(cmd_line + '| grep -q ' + grep) == 0:
            return True
        else:
            return False

    def mkdir(self, dir_name):
        return self.cmd('mkdir -p ' + dir_name)

    def chown(self, file_name, user_name, group_name):
        return self.cmd('chown -R ' + user_name + '.' + group_name + ' ' + file_name)

    def regex_file(self, rfile, regex):
        return self.cmd('sed -e "' + regex + '" -i ' + rfile)

    def regex_file_multi(self, rfile, *args):
        sed_str = ''.join(['-e "' + str(i) + '" ' for i in args])
        return self.cmd('sed ' + sed_str + ' -i ' + rfile)

    def copy_dir(self, old_dir, new_dir):
        return self.cmd('cp -RL --preserve=all ' + old_dir + ' ' + new_dir)

    def copy_file(self, old_file, new_file):
        return self.cmd('cp ' + old_file + ' ' + new_file)

    @staticmethod
    def read_from_file(file_name):
        file_ptr = open(file_name, 'r')
        return file_ptr.read()

    def write_to_file(self, wfile, data, append=False):
        mode = 'w'
        self.rm("./.tmp.file")
        if append is True:
            LinuxCLI().copy_file(wfile, "./.tmp.file")
            mode = 'a'
        file_ptr = open("./.tmp.file", mode)
        file_ptr.write(data)
        file_ptr.close()
        return self.copy_file('./.tmp.file', wfile)

    def rm(self, old_file):
        return self.cmd('rm -rf ' + old_file)
    
    def rm_files(self, root_dir, match_pattern=''):
        if match_pattern == '':
            return self.cmd('find ' + root_dir + ' -type f -exec sudo rm -f {} \; || true')
        else:
            return self.cmd('find ' + root_dir + ' -name ' + match_pattern + ' -exec sudo rm -f {} \; || true')

    @staticmethod
    def exists(efile):
        return os.path.exists(efile)

    def mount(self, drive, as_drive):
        return self.cmd('mount --bind ' + drive + ' ' + as_drive)

    def unmount(self, drive):
        return self.cmd('umount -l ' + drive + " > /dev/null 2>&1")

    def start_screen(self, host, window_name, cmd_line):
        cmd_in_screen = self.create_cmd(cmd_line)
        if self.grep_cmd('screen -ls', host) is False:
            # first screen = main screen
            cmd_opts = '-d -m -S ' + host
        else:
            # subsequent screens = sub screens
            cmd_opts = '-S ' + host + ' -X screen'
        return self.cmd('screen ' + cmd_opts + ' -t ' + window_name + ' /bin/bash -c "' + cmd_in_screen + '"')

    def start_screen_unshare(self, host, window_name, cmd_line):
        return self.start_screen(host, window_name, 'unshare -m ' + cmd_line)

    def cmd_unshare(self, cmd_line):
        return self.cmd('unshare --mount -- /bin/bash -x -c "' + cmd_line + '"')

    def cmd_unshare_control(self, cmd_line):
        return self.cmd_unshare('PYTHONPATH=.. python -u ' + CONTROL_CMD_NAME + ' ' + cmd_line)

    def send_packet(self, interface, pkt_type=None, src_ip=None, target_ip=None, src_mac=None,
                    target_mac=None, pkt_cmd=None, pkt_opt=None, count=None,
                    delay = None, bytes=None, timeout=None):
        """:type pkt_opt: dict[str, str]"""

        count_str = '-c %d' % count if count is not None else ''
        src_mac_str = '-a %s' % src_mac if src_mac is not None else ''
        target_mac_str = '-b %s' % target_mac if target_mac is not None else ''
        arg_str = ' '.join((src_mac_str, target_mac_str, count_str))

        # Bytes-only mode, only -a, -b, -c, and -p are supported by mz
        if pkt_type is None:
            if bytes is None:
                raise ArgMismatchException('no pkt_type requires "bytes" parameter to send raw bytes')
            full_cmd_str = 'mz %(iface)s %(arglist)s "%(bytes)s"' % \
                           {'iface': interface,
                            'arglist': arg_str,
                            'bytes': bytes}
            return self.cmd(full_cmd_str, return_output=True, timeout=timeout)

        # Packet-builder mode, supports various opts (supported opts depend on packet type)
        pkt_type_str = '-t %s' % pkt_type if pkt_type is not None else ''
        src_ip_str = '-A %s' % src_ip if src_ip is not None else ''
        target_ip_str = '-B %s' % target_ip if target_ip is not None else ''
        delay_str = '-d %d' % delay if delay is not None else ''
        pkt_bldr_arg_str = ' '.join((src_ip_str, target_ip_str, src_mac_str, target_mac_str, count_str, delay_str))
        opt_list = ', '.join('%s=%s' % (k, v) for k, v in pkt_opt.iteritems()) if pkt_opt is not None else ''

        if pkt_type is 'arp' or pkt_type is 'icmp':
            if pkt_cmd is None:
                raise ArgMismatchException('arp and icmp packets need a command or type')
            cmd_str = pkt_cmd + (', ' + opt_list if opt_list != '' else '')
        else:
            cmd_str = opt_list

        full_cmd_str = 'mz %(iface)s %(arglist)s %(extra_args)s %(pkttype)s "%(cmd)s"' % \
                           {'iface': interface,
                            'arglist': arg_str,
                            'extra_args': pkt_bldr_arg_str,
                            'pkttype': pkt_type_str,
                            'cmd': cmd_str}

        return self.cmd(full_cmd_str, return_output=True, timeout=timeout)


class NetNSCLI(LinuxCLI):
    def __init__(self, name, priv=True, debug=False):
        super(NetNSCLI, self).__init__(priv, debug)
        self.name = name

    def create_cmd(self, cmd_line):
        return super(NetNSCLI, self).create_cmd('ip netns exec ' + self.name + ' ' + cmd_line)

    def create_cmd_priv(self, cmd_line):
        return super(NetNSCLI, self).create_cmd_priv('ip netns exec ' + self.name + ' ' + cmd_line)
