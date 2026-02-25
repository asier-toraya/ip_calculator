import ipaddress
import unittest

from core import cpt_advanced_generator, cpt_generator, network_calc, subnet_calc


class CoreCalculationsTests(unittest.TestCase):
    def test_network_details_standard_case(self):
        details = network_calc.calculate_network_details("192.168.10.99/24")

        self.assertEqual(details["mask_str"], "255.255.255.0")
        self.assertEqual(details["network_addr"], "192.168.10.0")
        self.assertEqual(details["broadcast_addr"], "192.168.10.255")
        self.assertEqual(details["block_size"], 256)
        self.assertEqual(details["total_hosts"], 254)

    def test_network_details_prefix_31_has_no_usable_hosts(self):
        details = network_calc.calculate_network_details("10.0.0.1/31")

        self.assertEqual(details["total_hosts"], 0)
        self.assertIsNone(details["first_host"])
        self.assertIsNone(details["last_host"])

    def test_calculate_subnets(self):
        base_network = ipaddress.IPv4Network("10.0.0.0/24")
        subnet_info, error = subnet_calc.calculate_subnets(base_network, 4)

        self.assertIsNone(error)
        self.assertEqual(subnet_info["bits_needed"], 2)
        self.assertEqual(subnet_info["new_prefix"], 26)
        self.assertEqual(subnet_info["hosts_per_subnet"], 62)
        self.assertEqual(len(subnet_info["subnets"]), 4)

    def test_subnets_by_devices(self):
        base_network = ipaddress.IPv4Network("192.168.1.0/24")
        result = subnet_calc.calculate_subnets_by_devices(base_network, [50, 20, 10])

        self.assertEqual(len(result), 3)
        self.assertNotIn("error", result[0])
        self.assertEqual(result[0]["prefix"], 26)


class CPTGeneratorTests(unittest.TestCase):
    def test_basic_cpt_generation(self):
        base_network = ipaddress.IPv4Network("172.16.0.0/24")
        output, error = cpt_generator.generate_cpt_topology(
            base_network,
            num_subnets=3,
            num_routers=2,
            num_switches=2,
            devices_list=[40, 20, 10],
        )

        self.assertIsNone(error)
        self.assertIn("CONFIGURACION DE ROUTERS", output)
        self.assertIn("RECOMENDACIONES", output)

    def test_basic_cpt_generation_validates_switches(self):
        base_network = ipaddress.IPv4Network("172.16.0.0/24")
        output, error = cpt_generator.generate_cpt_topology(
            base_network,
            num_subnets=1,
            num_routers=1,
            num_switches=0,
            devices_list=[10],
        )

        self.assertIsNone(output)
        self.assertIn("switches", error.lower())

    def test_advanced_cpt_generation(self):
        base_network = ipaddress.IPv4Network("10.10.0.0/16")
        subnet_configs = [
            {"routers": 1, "switches": 1, "hosts": 40},
            {"routers": 1, "switches": 1, "hosts": 20},
        ]

        output, error = cpt_advanced_generator.generate_advanced_cpt(
            base_network,
            subnet_configs,
            routing_type="rip",
        )

        self.assertIsNone(error)
        self.assertIn("ENRUTAMIENTO:       RIP", output)
        self.assertIn("CONFIGURACION DETALLADA POR SUBRED", output)


if __name__ == "__main__":
    unittest.main()
