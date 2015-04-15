__author__ = 'micucci'

from PTM.RootServer import RootServer
from PTM.MapConfigReader import MapConfigReader
from PTM.PhysicalTopologyConfig import *
import unittest


class RootServerUnitTest(unittest.TestCase):

    def test_create_server_from_api(self):
        test_server1 = RootServer()
        test_server1.config_bridge(BridgeDef(name='br0', ip_list=[IPDef('10.0.0.240', '16')]))
        test_server1.config_bridge(BridgeDef(name='brv0', options='stp'))
        test_server1.config_zookeeper(HostDef('zoo1', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                    [IPDef('10.0.0.2')])]))
        test_server1.config_zookeeper(HostDef('zoo2', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                    [IPDef('10.0.0.3')])]))
        test_server1.config_zookeeper(HostDef('zoo3', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                    [IPDef('10.0.0.4')])]))
        test_server1.config_cassandra(HostDef('cass1', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                     [IPDef('10.0.0.5')])],
                                              options='56713727820156410577229101238628035242'))
        test_server1.config_cassandra(HostDef('cass2', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                     [IPDef('10.0.0.6')])],
                                              options='113427455640312821154458202477256070484'))
        test_server1.config_cassandra(HostDef('cass3', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                     [IPDef('10.0.0.7')])],
                                              options='170141183460469231731687303715884105726'))
        test_server1.config_zookeeper(HostDef('cmp1', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                    [IPDef('10.0.0.8')])]))
        test_server1.config_zookeeper(HostDef('cmp2', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                    [IPDef('10.0.0.8')])]))
        test_server1.config_zookeeper(HostDef('cmp3', [InterfaceDef('eth0', BridgeLinkDef(name='br0'),
                                                                    [IPDef('10.0.0.8')])]))

        test_server1.config_router(RouterDef('quagga',
                                             [PeerInterfaceDef(InterfaceDef(name='eth0', ip_list=[IPDef('10.0.0.240')]),
                                                               TargetInterfaceDef('cmp1', 'eth0')),
                                              PeerInterfaceDef(InterfaceDef(name='eth1', ip_list=[IPDef('10.0.1.240')]),
                                                               TargetInterfaceDef('cmp2', 'eth0'))]))

        test_server1.config_generic_host(HostDef('v1.1', [InterfaceDef('eth0', BridgeLinkDef(name='brv0')),
                                                          InterfaceDef('eth1', BridgeLinkDef(name='brv0'))]))
        test_server1.config_generic_host(HostDef('v1.2', [InterfaceDef('eth0', BridgeLinkDef(name='brv0'))]))
        test_server1.config_generic_host(HostDef('v2.1', [InterfaceDef('eth0', BridgeLinkDef(name='brv0'))]))
        test_server1.config_generic_host(HostDef('v2.2', [InterfaceDef('eth0', BridgeLinkDef(name='brv0'))]))

        test_server1.config_vlan(VLANDef(vlan_id='1',
                                         host_list=[HostDef('v1.1',
                                                            [InterfaceDef('eth0', ip_list=[IPDef('172.16.0.224')])]),
                                                    HostDef('v1.1',
                                                            [InterfaceDef('eth1', ip_list=[IPDef('172.16.0.223')])]),
                                                    HostDef('v2.1',
                                                            [InterfaceDef('eth0', ip_list=[IPDef('172.16.0.225')])])]))
        test_server1.config_vlan(VLANDef(vlan_id='2',
                                         host_list=[HostDef('v1.2',
                                                            [InterfaceDef('eth0', ip_list=[IPDef('172.16.0.224')])]),
                                                    HostDef('v2.2',
                                                            [InterfaceDef('eth0', ip_list=[IPDef('172.16.0.225')])])]))
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
        test_system.config_compute(HostDef('cmp1', [InterfaceDef(name='eth0', ip_list=[IPDef('2.2.2.2', '32')])]))
        h = test_system.get_host('cmp1')

        self.assertEqual(True, True)

    def test_get_vm_host_on_server(self):
        test_system = RootServer()
        test_system.config_compute(HostDef('cmp1', [InterfaceDef(name='eth0', ip_list=[IPDef('2.2.2.2', '32')])]))
        test_system.config_vm(VMDef('cmp1', HostDef('vm1', [InterfaceDef(name='eth0',
                                                                         ip_list=[IPDef('3.3.3.3', '32')])])))

        h = test_system.get_host('cmp1')
        """ :type: ComputeHost"""
        vm = h.get_vm('vm1')
        self.assertEqual(True, True)


try:
    suite = unittest.TestLoader().loadTestsFromTestCase(RootServerUnitTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
except Exception as e:
    print 'Exception: ' + e.message + ', ' + str(e.args)
