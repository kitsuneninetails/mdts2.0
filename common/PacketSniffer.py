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

from common.Exceptions import *
from common.CLI import LinuxCLI

class PS_Rule(object):
    def __init__(self):
        pass

    def to_str(self):
        raise ArgMismatchException('All Rules should override the "to_str" method!')


class PS_Explicit(PS_Rule):
    def __init__(self, val):
        """
        :param val: str
        """
        super(PS_Explicit, self).__init__()
        self.explicit_val = val

    def to_str(self):
        return self.explicit_val


class PS_BinaryBoolean(PS_Rule):
    def __init__(self, operation, rule_set):
        """
        :param operation: str
        :param rule_set: list[PS_Rule]
        """
        super(PS_BinaryBoolean, self).__init__()
        self.operation = operation
        self.rule_set = rule_set

    def to_str(self):
        if len(self.rule_set) < 2:
            return ''.join([i.to_str() for i in self.rule_set])
        return (' ' + self.operation + ' ').join([i.to_str() for i in self.rule_set])


class PS_And(PS_BinaryBoolean):
    def __init__(self, rule_set):
        """
        :param rule_set: list[PS_Rule]
        """
        super(PS_And, self).__init__('and', rule_set)


class PS_Or(PS_BinaryBoolean):
    def __init__(self, rule_set):
        """
        :param rule_set: list[PS_Rule]
        """
        super(PS_Or, self).__init__('or', rule_set)


class PS_Not(PS_Rule):
    def __init__(self, rule):
        """
        :param rule: PS_Rule
        """
        super(PS_Not, self).__init__()
        self.rule = rule

    def to_str(self):
        return 'not ' + self.rule.to_str()


class PS_Comparison(PS_Rule):
    def __init__(self, operation, lhs, rhs):
        """
        :param operation: str
        :param lhs: str
        :param rhs: str
        """
        super(PS_Comparison, self).__init__()
        self.operation = operation
        self.lhs = lhs
        self.rhs = rhs

    def to_str(self):
        return self.lhs + ' ' + self.operation + ' ' + self.rhs


class PS_GreaterThanEqual(PS_Comparison):
    def __init__(self, lhs, rhs):
        """
        :param lhs: str
        :param rhs: str
        """
        super(PS_GreaterThanEqual, self).__init__('>=', lhs, rhs)


class PS_GreaterThan(PS_Comparison):
    def __init__(self, lhs, rhs):
        """
        :param lhs: str
        :param rhs: str
        """
        super(PS_GreaterThan, self).__init__('>', lhs, rhs)


class PS_Equal(PS_Comparison):
    def __init__(self, lhs, rhs):
        """
        :param lhs: str
        :param rhs: str
        """
        super(PS_Equal, self).__init__('=', lhs, rhs)


class PS_NotEqual(PS_Comparison):
    def __init__(self, lhs, rhs):
        """
        :param lhs: str
        :param rhs: str
        """
        super(PS_NotEqual, self).__init__('!=', lhs, rhs)


class PS_LessThan(PS_Comparison):
    def __init__(self, lhs, rhs):
        """
        :param lhs: str
        :param rhs: str
        """
        super(PS_LessThan, self).__init__('<', lhs, rhs)


class PS_LessThanEqual(PS_Comparison):
    def __init__(self, lhs, rhs):
        """
        :param lhs: str
        :param rhs: str
        """
        super(PS_LessThanEqual, self).__init__('<=', lhs, rhs)


class PS_PrimitiveTypeRule(PS_Rule):
    def __init__(self, param, proto='', source=False, dest=False):
        """
        :param proto: str
        :param source: bool
        :param dest: bool
        """
        super(PS_PrimitiveTypeRule, self).__init__()
        self.proto = proto
        self.source = source
        self.dest = dest
        self.param = param

    def to_str(self):
        cmd = self.proto + ' ' if self.proto != '' else ''
        if not self.source and not self.dest:
            cmd += ''
        elif self.source and not self.dest:
            cmd += 'src '
        elif not self.source and self.dest:
            cmd += 'dst '
        elif self.source and self.dest:
            cmd += 'src and dst '
        return cmd + self.param


class PS_Host(PS_PrimitiveTypeRule):
    def __init__(self, host, proto='', source=False, dest=False):
        """
        :param host: str
        :param proto: str
        :param source: bool
        :param dest: bool
        """
        super(PS_Host, self).__init__('host ' + host, proto, source, dest)


class PS_PortRange(PS_PrimitiveTypeRule):
    def __init__(self, start_port, end_port, proto='', source=False, dest=False):
        """
        :param start_port: int
        :param end_port: int
        :param proto: str
        :param source: bool
        :param dest: bool
        """
        super(PS_PortRange, self).__init__('portrange ' + str(start_port) + '-' + str(end_port),
                                           proto, source, dest)


class PS_Port(PS_PrimitiveTypeRule):
    def __init__(self, port, proto='', source=False, dest=False):
        """
        :param port: int
        :param proto: str
        :param source: bool
        :param dest: bool
        """
        super(PS_Port, self).__init__('port ' + str(port), proto, source, dest)


class PS_Net(PS_PrimitiveTypeRule):
    def __init__(self, net, mask='', proto='', source=False, dest=False):
        """
        :param net: str
        :param proto: str
        :param source: bool
        :param dest: bool
        """
        super(PS_Net, self).__init__('net ' + net + (' mask ' + mask if mask != '' else ''),
                                     proto, source, dest)


class PS_PrimitiveProtoRule(PS_Rule):
    def __init__(self, base_proto, filter_proto):
        """
        :param base_proto: str Either 'ip' or 'ether'
        :param filter_proto: str For 'ip', can be 'tcp, icmp, udp'.  For 'ether' can be 'ip', 'arp', 'stp'
        """
        super(PS_PrimitiveProtoRule, self).__init__()
        self.base_proto = base_proto
        self.filter_proto = filter_proto

    def to_str(self):
        return self.base_proto + ' proto ' + self.filter_proto


class PS_IPProto(PS_PrimitiveProtoRule):
    def __init__(self, proto):
        """
        :param proto: str One of 'tcp', 'icmp', or 'udp'
        """
        super(PS_IPProto, self).__init__('ip', proto)


class PS_EtherProto(PS_PrimitiveProtoRule):
    def __init__(self, proto):
        """
        :param proto: str One of 'ip', 'arp', or 'stp'
        """
        super(PS_EtherProto, self).__init__('ether', proto)


class PS_PrimitiveCast(PS_Rule):
    def __init__(self, type, proto='ether'):
        """
        :param type: str Either 'broadcast' or 'multicast'
        :param proto: str Either 'ip' or 'ether'
        """
        super(PS_PrimitiveCast, self).__init__()
        self.type = type
        self.proto = proto

    def to_str(self):
        return self.proto + ' ' + self.type


class PS_Multicast(PS_PrimitiveCast):
    def __init__(self, proto='ether'):
        """
        :param proto: str Either 'ip' or 'ether' (default)
        """
        super(PS_Multicast, self).__init__('multicast', proto)


class PS_Broadcast(PS_PrimitiveCast):
    def __init__(self, proto='ether'):
        """
        :param proto: str Either 'ip' or 'ether' (default)
        """
        super(PS_Broadcast, self).__init__('broadcast', proto)


class PacketSniffer(object):

    @staticmethod
    def sniff_packet(interface='any', max_size=0, count=1, packet_type='',
                     filter_rules=list(),
                     include_packet_data=False):
        """
        Sniff packets on an interface and return the data (optionally returning ALL packet data
        as well).  Returns a list, <count> in length, of matching data (or the entire packet data
        including headers if the include_packet_data option is set to True) in the form of
        (timestamp, data) for each member of the list.

        :param interface: str Interface to sniff on
        :param max_size: int Maximum length of data to return in each packet
        :param count: int Number of packets matching filter to return
        :param packet_type: str If not blank, set the type of packet to watch for (e.g. 'vxlan')
        :param filter_rules: list[PS_Rule] Set of PS_Rule objects to filter the packets
        :param include_packet_data: bool True to return the entire packet, including headers

        :return: list[(str, str)]

        """

        count_str = '-c ' + str(count)
        iface_str = '-i ' + interface
        buffered_str = '-U'
        max_size_str = '-s ' + max_size if max_size != 0 else ''
        type_str = '-T ' + packet_type if packet_type != '' else ''
        cmd_str = 'tcpdump ' + count_str + ' ' + iface_str + ' ' + buffered_str + ' ' + \
                  max_size_str + ' ' + type_str
