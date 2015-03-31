__author__ = 'micucci'

from PTM.RootServer import RootServer
from PTM.MapConfigReader import MapConfigReader
from PTM.PhysicalTopologyConfig import *
import unittest


class RootServerUnitTest(unittest.TestCase):

    def test_create_server_from_api(self):
        test_server1 = RootServer()
        test_server1.config_bridge(name='br0', ip_list=[('10.0.0.240', '16')])
        test_server1.config_bridge(name='brv0', options=['stp'])
        test_server1.config_zookeeper(name='zoo1', interface={'iface':  'eth0', 'bridge':  'br0',
                                                              'ips':  [('10.0.0.2', '24')]})
        test_server1.config_zookeeper(name='zoo2', interface={'iface':  'eth0', 'bridge':  'br0',
                                                              'ips':  [('10.0.0.3', '24')]})
        test_server1.config_zookeeper(name='zoo3', interface={'iface': 'eth0', 'bridge': 'br0',
                                                              'ips': [('10.0.0.4', '24')]})
        test_server1.config_cassandra(name='cass1', interface={'iface': 'eth0', 'bridge': 'br0',
                                                               'ips': [('10.0.0.5', '24')]},
                                      extra_data=['56713727820156410577229101238628035242'])
        test_server1.config_cassandra(name='cass2', interface={'iface': 'eth0', 'bridge': 'br0',
                                                               'ips': [('10.0.0.6', '24')]},
                                      extra_data=['113427455640312821154458202477256070484'])
        test_server1.config_cassandra(name='cass3', interface={'iface': 'eth0', 'bridge': 'br0',
                                                               'ips': [('10.0.0.7', '24')]},
                                      extra_data=['170141183460469231731687303715884105726'])
        test_server1.config_compute(name='cmp1', interface={'iface': 'eth0', 'bridge': 'br0',
                                                            'ips': [('10.0.0.8', '24')]})
        test_server1.config_compute(name='cmp2', interface={'iface': 'eth0', 'bridge': 'br0',
                                                            'ips': [('10.0.0.9', '24')]})
        test_server1.config_compute(name='cmp3', interface={'iface': 'eth0', 'bridge': 'br0',
                                                            'ips': [('10.0.0.10', '24')]})
        test_server1.config_router(name='quagga',
                                   interfaces=[{'iface': 'eth0',
                                                'ips': [('10.0.1.240', '24')],
                                                'target_host': 'cmp1',
                                                'target_iface': 'eth0'},
                                               {'iface': 'eth1',
                                                'ips': [('10.0.1.240', '24')],
                                                'target_host': 'cmp2',
                                                'target_iface': 'eth0'}])
        test_server1.config_generic_host(name='v1.1', interface_list=[{'iface': 'eth0', 'bridge': 'brv0'},
                                                                      {'iface': 'eth1', 'bridge': 'brv0'}])
        test_server1.config_generic_host(name='v1.2', interface_list=[{'iface': 'eth0', 'bridge': 'brv0'}])
        test_server1.config_generic_host(name='v2.1', interface_list=[{'iface': 'eth0', 'bridge': 'brv0'}])
        test_server1.config_generic_host(name='v2.2', interface_list=[{'iface': 'eth0', 'bridge': 'brv0'}])
        test_server1.config_vlan(vlan_id='1', vlan_if_list=[{'host': 'v1.1',
                                                             'iface': 'eth0',
                                                             'ips': [('172.16.0.224', '24')]},
                                                            {'host': 'v1.1',
                                                             'iface': 'eth1',
                                                             'ips': [('172.16.0.223', '24')]},
                                                            {'host': 'v2.1',
                                                             'iface': 'eth0',
                                                             'ips': [('172.16.0.225', '24')]}])
        test_server1.config_vlan(vlan_id='2', vlan_if_list=[{'host': 'v1.2',
                                                             'iface': 'eth0',
                                                             'ips': [('172.16.0.224', '24')]},
                                                            {'host': 'v2.2',
                                                             'iface': 'eth0',
                                                             'ips': [('172.16.0.225', '24')]}])
        self.assertEqual(True, True)

    def test_create_test_server_from_json(self):
        config_json = {
            "bridges": [
                {
                    "name": "br0",
                    "ip_list": [
                        {
                            "ip": "10.0.0.240",
                            "subnet": "24"
                        }
                    ]
                },
            ],
            "computes": [
                {
                    "interface_list": [
                        {
                            "bridge_link": {
                                "name": "br0"
                            },
                            "name": "eth0",
                            "ip_list": [
                                {
                                    "ip": "10.0.0.8",
                                    "subnet": "24"
                                }
                            ]
                        }
                    ],
                    "name": "cmp1"
                },
            ],
            "vlans": [],
            "hosts": [
                {
                    "name": "v1.1",
                    "interface_list": [
                        {
                            "bridge_link": {
                                "name": "brv0"
                            },
                            "name": "eth0"
                        }
                    ]
                },
            ],
            "hosted_vms": [],
            "routers": [],
            "cassandras": [],
            "zookeepers": []
        }

        config = MapConfigReader.get_physical_topology_config(config_json)
        test_server2 = RootServer.create_from_physical_topology_config(config)
        test_server2.init()
        self.assertEqual(True, True)

    def test_create_test_server_from_ptc(self):
        ptc = PhysicalTopologyConfig()
        ptc.add_bridge_def(BridgeDef('br0', '', [IPDef('0.0.0.0', '32')], ''))
        ptc.add_compute_def(HostDef('host1',
                                    [InterfaceDef('eth0',
                                                  BridgeLinkDef('', 'br0'),
                                                  [IPDef('1.1.1.1', '32')],
                                                  '')],
                                    ''))
        ptc.add_host_def(HostDef('host1',
                                 [InterfaceDef('eth0',
                                               BridgeLinkDef('', 'br0'),
                                               [IPDef('2.2.2.2', '32')],
                                               '')],
                                 ''))

        test_server = RootServer.create_from_physical_topology_config(ptc)
        test_server.init()
        # test_server.prepare_files()
        # test_server.setup()
        # test_server.start()

        # test_server.stop()
        # test_server.cleanup()
        self.assertEqual(True, True)

    def test_get_host_on_server(self):
        test_system = RootServer()
        test_system.config_compute('cmp1', {'iface': 'eth0', 'ips': ['2.2.2.2', '32']})
        h = test_system.get_host('cmp1')

        self.assertEqual(True, True)

    def test_get_vm_host_on_server(self):
        test_system = RootServer()
        test_system.config_compute('cmp1', {'iface': 'eth0', 'ips': ['2.2.2.2', '32']})
        test_system.config_vm('cmp1', 'vm1', [{'iface': 'eth0', 'ips': ['3.3.3.3', '32']}])
        h = test_system.get_host('cmp1')
        """ :type: ComputeHost"""
        vm = h.get_vm('vm1')
        self.assertEqual(True, True)


try:
    suite = unittest.TestLoader().loadTestsFromTestCase(RootServerUnitTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
except Exception as e:
    print 'Exception: ' + e.message + ', ' + str(e.args)
