__author__ = 'micucci'

import unittest
from common.CLI import *

class CLITest(unittest.TestCase):
    def test_send_packet_default(self):
        cli = LinuxCLI(debug=True)
        self.assertRaises(ArgMismatchException, cli.send_packet, 'eth0')

    def test_send_packet_arp(self):
        cli = LinuxCLI(debug=True, print_cmd=True)
        out = cli.send_packet('eth0', pkt_type='arp',
                              src_ip='1.1.1.1', target_ip='2.2.2.2',
                              pkt_cmd='request', pkt_opt={'sip': '1.1.1.1'})
        self.assertTrue('mz eth0' in out)
        self.assertTrue('-t arp "request, sip=1.1.1.1"' in out)
        self.assertTrue('-A 1.1.1.1' in out)
        self.assertTrue('-B 2.2.2.2' in out)
        self.assertTrue('-a' not in out)
        self.assertTrue('-b' not in out)
        self.assertTrue('icmp' not in out)
        self.assertTrue('targetip' not in out)

    def test_send_packet_arp_no_cmd(self):
        cli = LinuxCLI(debug=True)
        self.assertRaises(ArgMismatchException, cli.send_packet,
                          'eth0', pkt_type='arp',
                          src_ip='1.1.1.1', target_ip='2.2.2.2',
                          pkt_opt={'sip': '1.1.1.1'})

    def test_send_packet_ip(self):
        cli = LinuxCLI(debug=True, print_cmd=True)
        out = cli.send_packet('eth0', pkt_type='ip', pkt_opt={'len': '30'})
        self.assertTrue('mz eth0' in out)
        self.assertTrue('-t ip "len=30"' in out)
        self.assertTrue('-a' not in out)
        self.assertTrue('-b' not in out)
        self.assertTrue('-A' not in out)
        self.assertTrue('-B' not in out)
        self.assertTrue('arp' not in out)
        self.assertTrue('sum' not in out)

    def test_send_packet_bytes(self):
        cli = LinuxCLI(debug=True, print_cmd=True)
        out = cli.send_packet('eth0', pkt_type=None,
                              src_mac='rand', target_mac='00:11:22:33:44:55',
                              bytes='deadbeef')
        self.assertTrue('mz eth0' in out)
        self.assertTrue('-a rand' in out)
        self.assertTrue('-b 00:11:22:33:44:55' in out)
        self.assertTrue('deadbeef' in out)
        self.assertTrue('-t' not in out)
        self.assertTrue('-A' not in out)
        self.assertTrue('-B' not in out)
        self.assertTrue('ip' not in out)

    def test_send_packet_real(self):
            cli = LinuxCLI(debug=True, print_cmd=True)
        out = cli.send_packet('eth0', pkt_type='arp',
                              src_ip='1.1.1.1', target_ip='2.2.2.2',
                              pkt_cmd='request', pkt_opt={'sip': '1.1.1.1'})
        self.assertTrue('mz eth0' in out)
        self.assertTrue('-t arp "request, sip=1.1.1.1"' in out)
        self.assertTrue('-A 1.1.1.1' in out)
        self.assertTrue('-B 2.2.2.2' in out)
        self.assertTrue('-a' not in out)
        self.assertTrue('-b' not in out)
        self.assertTrue('icmp' not in out)
        self.assertTrue('targetip' not in out)

    def test_send_packet_and_receive_packet(self):
        cli = LinuxCLI(debug=True, print_cmd=True)
        out = cli.send_packet('eth0', pkt_type='arp',
                              src_ip='1.1.1.1', target_ip='2.2.2.2',
                              pkt_cmd='request', pkt_opt={'sip': '1.1.1.1'})
        self.assertTrue('mz eth0' in out)
        self.assertTrue('-t arp "request, sip=1.1.1.1"' in out)
        self.assertTrue('-A 1.1.1.1' in out)
        self.assertTrue('-B 2.2.2.2' in out)
        self.assertTrue('-a' not in out)
        self.assertTrue('-b' not in out)
        self.assertTrue('icmp' not in out)
        self.assertTrue('targetip' not in out)



try:
    suite = unittest.TestLoader().loadTestsFromTestCase(CLITest)
    unittest.TextTestRunner(verbosity=2).run(suite)
except Exception as e:
    print 'Exception: ' + e.message + ', ' + str(e.args)

