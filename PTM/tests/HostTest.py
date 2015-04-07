__author__ = 'micucci'

import unittest

from PTM.Host import *
from PTM.RootServer import RootServer

class HostTest(unittest.TestCase):
    def test_send_packet(self):
        rs = RootServer()
        h1 = rs.config_generic_host('host1', [{'iface': 'eth0', 'ips': ['10.0.1.2', '24']}])
        """ :type: Host"""
        h2 = rs.config_generic_host('host2', [{'iface': 'eth0', 'ips': ['10.0.1.3', '24']}])
        h1.send_packet('eth0', 'icmp', '10.0.1.3')
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
