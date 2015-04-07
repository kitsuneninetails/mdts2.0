__author__ = 'micucci'

import unittest

from VTM.Host import Host
from VTM.VirtualTopologyConfig import VirtualTopologyConfig
from VTM.tests.VirtualTopologyConfigTest import MockClient
from PTM.VMHost import VMHost
from PTM.ComputeHost import ComputeHost
from PTM.RootServer import RootServer
from VTM.Network import Network
from VTM.Port import Port


class MockNetwork(Network):
    def __init__(self, vtc):
        super(MockNetwork, self).__init__(vtc)

    def create_port(self):
        port = None
        port_id = "fe6707e3-9c99-4529-b059-aa669d1463bb"
        self.ports[port_id] = port
        return port_id


class MyTestCase(unittest.TestCase):

    def test_ping_between_two_hosts(self):

        test_system = RootServer()
        test_system.config_compute('cmp1', {'iface': 'eth0', 'ips': ['2.2.2.2', '32']})
        test_system.config_vm('cmp1', 'vm1', [{'iface': 'eth0', 'ips': ['3.3.3.3', '32']}])
        hv = test_system.get_host('cmp1')
        """ :type: ComputeHost"""
        vm = hv.get_vm('vm1')
        """ :type: VMHost"""

        virtual_host = Host(self.vtc, vm)
        virtual_network = MockNetwork(self.vtc)
        port_id = virtual_network.create_port()
        virtual_host.plugin_vm(hv.get_interfaces_for_host('vm1')['eth0'], port_id)
        #
        # Title: basic L2 connectivity in Neutron network
        #
        # When: there is a neutron network on which there are 2 neutron ports
        # Then: spwan VMs for each port
        # Then: VMs can ping to each other
        #
        # Virtual Topology:
        #
        # TODO: visualize the topology
        #

        test_id = 'mdts2_test_ping_between_two_vms' + \
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info('Starting a test %s', test_id)



        tenant_id = test_id
        name = 'test_ping_between_two_vms'

        #
        # Topology setup
        #

        # create network and subnet
        net_data = {'name': name, 'tenant_id': tenant_id}
        net = self.neutron_client.create_network({'network':net_data})

        network_id = net['network']['id']

        subnet = self.neutron_client.create_subnet(
            {'subnet': {'name': name,
                        'tenant_id': tenant_id,
                        'cidr':'1.1.1.0/24',
                        'network_id': network_id,
                        'ip_version': 4}  })

        # create two ports
        port1 = self.neutron_client.create_port(
            {'port': {'tenant_id': tenant_id,
                      'network_id': network_id}})

        port2 = self.neutron_client.create_port(
            {'port': {'tenant_id': tenant_id,
                      'network_id': network_id}})

        # create two VMs on host[0] for each port
        vm1 = self.hosts[0].create_vm('vm1', port1)
        vm2 = self.hosts[0].create_vm('vm2', port2)

        # Test:
        # make sure that vm1 cna vm2 can ping each other
        #
        vm1.assert_pings_to(vm2)
        vm2.assert_pings_to(vm1)

        #
        # teardown VMs and neutron
        #
        vm1.delete()
        vm2.delete()

        # tearing down neutron ports and network
        self.neutron_client.delete_port(port1['port']['id'])
        self.neutron_client.delete_port(port2['port']['id'])
        self.neutron_client.delete_network(network_id)


if __name__ == '__main__':
    unittest.main()
