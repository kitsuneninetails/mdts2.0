__author__ = 'micucci'

import unittest
from common.PacketSniffer import *

class PacketSnifferTest(unittest.TestCase):
    def test_host_rules(self):
        simple_rule = PS_Host('foo')
        proto_rule = PS_Host('foo', proto='ether')
        proto_with_src_rule = PS_Host('foo', 'ether', source=True)
        src_and_dest_rule = PS_Host('foo', source=True, dest=True)
        dest_rule = PS_Host('foo', dest=True)

        self.assertEqual('host foo', simple_rule.to_str())
        self.assertEqual('ether host foo', proto_rule.to_str())
        self.assertEqual('ether src host foo', proto_with_src_rule.to_str())
        self.assertEqual('src and dst host foo', src_and_dest_rule.to_str())
        self.assertEqual('dst host foo', dest_rule.to_str())

    def test_port_rules(self):
        simple_rule = PS_Port(80)
        proto_rule = PS_Port(80, proto='ether')
        proto_with_src_rule = PS_Port(80, 'ether', source=True)
        src_and_dest_rule = PS_Port(80, source=True, dest=True)
        dest_rule = PS_Port(80, dest=True)

        self.assertEqual('port 80', simple_rule.to_str())
        self.assertEqual('ether port 80', proto_rule.to_str())
        self.assertEqual('ether src port 80', proto_with_src_rule.to_str())
        self.assertEqual('src and dst port 80', src_and_dest_rule.to_str())
        self.assertEqual('dst port 80', dest_rule.to_str())

        range_simple_rule = PS_PortRange(80, 90)
        range_proto_rule = PS_PortRange(80, 90, proto='ether')
        range_proto_with_src_rule = PS_PortRange(80, 90, 'ether', source=True)
        range_src_and_dest_rule = PS_PortRange(80, 90, source=True, dest=True)
        range_dest_rule = PS_PortRange(80, 90, dest=True)

        self.assertEqual('portrange 80-90', range_simple_rule.to_str())
        self.assertEqual('ether portrange 80-90', range_proto_rule.to_str())
        self.assertEqual('ether src portrange 80-90', range_proto_with_src_rule.to_str())
        self.assertEqual('src and dst portrange 80-90', range_src_and_dest_rule.to_str())
        self.assertEqual('dst portrange 80-90', range_dest_rule.to_str())

    def test_net_rules(self):
        simple_rule = PS_Net('192.168.0')
        proto_rule = PS_Net('192.168.0', proto='ether')
        proto_with_src_rule = PS_Net('192.168.0', '', 'ether', source=True)
        src_and_dest_rule = PS_Net('192.168.0', source=True, dest=True)
        dest_rule = PS_Net('192.168.0', dest=True)
        cidr_rule = PS_Net('192.168.0.0/24')
        netmask_rule = PS_Net('192.168.0.0', '255.255.255.0')

        self.assertEqual('net 192.168.0', simple_rule.to_str())
        self.assertEqual('ether net 192.168.0', proto_rule.to_str())
        self.assertEqual('ether src net 192.168.0', proto_with_src_rule.to_str())
        self.assertEqual('src and dst net 192.168.0', src_and_dest_rule.to_str())
        self.assertEqual('dst net 192.168.0', dest_rule.to_str())
        self.assertEqual('net 192.168.0.0/24', cidr_rule.to_str())
        self.assertEqual('net 192.168.0.0 mask 255.255.255.0', netmask_rule.to_str())

    def test_ip_proto_rules(self):
        tcp_rule = PS_IPProto('tcp')
        icmp_rule = PS_IPProto('icmp')
        udp_rule = PS_IPProto('udp')

        self.assertEqual('ip proto tcp', tcp_rule.to_str())
        self.assertEqual('ip proto icmp', icmp_rule.to_str())
        self.assertEqual('ip proto udp', udp_rule.to_str())

    def test_ether_proto_rules(self):
        ip_rule = PS_EtherProto('ip')
        arp_rule = PS_EtherProto('arp')
        stp_rule = PS_EtherProto('stp')

        self.assertEqual('ether proto ip', ip_rule.to_str())
        self.assertEqual('ether proto arp', arp_rule.to_str())
        self.assertEqual('ether proto stp', stp_rule.to_str())

    def test_cast_rules(self):
        localhost_rule = PSRule('host', 'src', 'ether')

        self.assertEqual(True, False)

    def test_comparison_rules(self):
        gt_rule = PS_GreaterThan('len', '500')
        gt_flip_rule = PS_GreaterThan('500', 'len')
        gte_rule = PS_GreaterThanEqual('len', '500')
        e_rule = PS_Equal('len', '500')
        ne_rule = PS_NotEqual('len', '500')
        lt_rule = PS_LessThan('len', '500')
        lte_rule = PS_LessThanEqual('len', '500')

        self.assertEqual('len > 500', gt_rule.to_str())
        self.assertEqual('500 > len', gt_flip_rule.to_str())
        self.assertEqual('len >= 500', gte_rule.to_str())
        self.assertEqual('len = 500', e_rule.to_str())
        self.assertEqual('len != 500', ne_rule.to_str())
        self.assertEqual('len < 500', lt_rule.to_str())
        self.assertEqual('len <= 500', lte_rule.to_str())

    def test_unary_boolean_rules(self):
        not_single_rule = PS_Not(PS_Explicit('foo'))
        self.assertEqual('not foo', not_single_rule.to_str())

    def test_binary_boolean_rules(self):
        and_single_rule = PS_And([PS_Explicit('foo')])
        and_double_rule = PS_And([PS_Explicit('foo'), PS_Explicit('bar')])
        and_triple_rule = PS_And([PS_Explicit('foo'), PS_Explicit('bar'), PS_Explicit('baz')])
        and_null_rule = PS_And([])
        or_single_rule = PS_Or([PS_Explicit('foo')])
        or_double_rule = PS_Or([PS_Explicit('foo'), PS_Explicit('bar')])
        or_triple_rule = PS_Or([PS_Explicit('foo'), PS_Explicit('bar'), PS_Explicit('baz')])
        or_null_rule = PS_Or([])

        self.assertEqual('foo', and_single_rule.to_str())
        self.assertEqual('foo and bar', and_double_rule.to_str())
        self.assertEqual('foo and bar and baz', and_triple_rule.to_str())
        self.assertEqual('', and_null_rule.to_str())
        self.assertEqual('foo', or_single_rule.to_str())
        self.assertEqual('foo or bar', or_double_rule.to_str())
        self.assertEqual('foo or bar or baz', or_triple_rule.to_str())
        self.assertEqual('', or_null_rule.to_str())

    def test_sniff_simple_host_packet(self):
        PacketSniffer.sniff_packet(interface='any', count=1,
                                   ruleset=[
                                       PS_Or([
                                           PS_Host('localhost', proto='ip', source=True, dest=True),
                                           PS_Host('localhost', proto='ether', source=True),
                                           PS_LessThanEqual('len', 1500)
                                       ]),
                                       PS_And([
                                           PS_Port(80, proto='tcp', source_dest=True),
                                           PS_PortRange(6000,6500, proto='tcp', source=True),
                                           PS_GreaterThan('len', 1500)
                                       ]),
                                       PS_Not(PS_Network('192.168.0', dest=True))
                                   ])


if __name__ == '__main__':
    unittest.main()
