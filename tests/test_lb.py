import unittest
from server import Server
from consistent_hash import ConsistentHash, DEFAULT_NUM_REPLICAS
from load_balancer import (
    LoadBalancer,
    STRATEGY_ROUND_ROBIN,
    STRATEGY_WEIGHTED,
    STRATEGY_CONSISTENT_HASH,
)

# Round robin configuration
NUM_RR_SERVERS = 5

# Simulation configuration
SIMULATION_REQUESTS = 10000

# Consistent hash thresholds
MAX_CH_LOAD_PERCENT = 50
MIN_CH_LOAD_PERCENT = 1
STABILITY_RETENTION_THRESHOLD = 0.5

# Weighted test configuration
WEIGHT_HEAVY = 5
WEIGHT_MEDIUM = 2
WEIGHT_LIGHT = 1


class TestRoundRobin(unittest.TestCase):

    def test_rr_cycling_order(self):
        """Round Robin cycles through 5 servers in order"""
        servers = [Server(f"S{i}") for i in range(NUM_RR_SERVERS)]
        lb = LoadBalancer(servers, STRATEGY_ROUND_ROBIN)
        for cycle in range(2):
            for i in range(NUM_RR_SERVERS):
                result = lb.get_next_server(f"req_{cycle}_{i}")
                self.assertEqual(result.id, f"S{i}")

    def test_rr_even_distribution(self):
        """Round Robin distributes 10000 requests evenly across 5 servers"""
        servers = [Server(f"S{i}") for i in range(NUM_RR_SERVERS)]
        lb = LoadBalancer(servers, STRATEGY_ROUND_ROBIN)
        for i in range(SIMULATION_REQUESTS):
            server = lb.get_next_server(f"req_{i}")
            server.handle_request()
        expected_per_server = SIMULATION_REQUESTS // NUM_RR_SERVERS
        for s in servers:
            self.assertEqual(s.request_count, expected_per_server)

    def test_rr_single_server(self):
        """Round Robin with single server sends all requests there"""
        s = Server("Solo")
        lb = LoadBalancer([s], STRATEGY_ROUND_ROBIN)
        for i in range(10):
            self.assertEqual(lb.get_next_server(f"req_{i}").id, "Solo")


class TestWeightedRoundRobin(unittest.TestCase):

    def test_weighted_basic_two_servers(self):
        """Weighted RR: 2 servers (3:1) distributes traffic proportionally"""
        s1 = Server("S1", 3)
        s2 = Server("S2", 1)
        lb = LoadBalancer([s1, s2], STRATEGY_WEIGHTED)
        ids = [lb.get_next_server(f"req{i}").id for i in range(8)]
        self.assertEqual(ids.count("S1"), 6)
        self.assertEqual(ids.count("S2"), 2)

    def test_weighted_three_servers(self):
        """Weighted RR: 3 servers (5:2:1) distributes traffic proportionally"""
        s1 = Server("S1", WEIGHT_HEAVY)
        s2 = Server("S2", WEIGHT_MEDIUM)
        s3 = Server("S3", WEIGHT_LIGHT)
        total_weight = WEIGHT_HEAVY + WEIGHT_MEDIUM + WEIGHT_LIGHT
        lb = LoadBalancer([s1, s2, s3], STRATEGY_WEIGHTED)
        num_requests = total_weight * 10
        ids = [lb.get_next_server(f"req{i}").id for i in range(num_requests)]
        self.assertEqual(ids.count("S1"), WEIGHT_HEAVY * 10)
        self.assertEqual(ids.count("S2"), WEIGHT_MEDIUM * 10)
        self.assertEqual(ids.count("S3"), WEIGHT_LIGHT * 10)

    def test_weighted_equal_weights(self):
        """Weighted RR: equal weights produce even distribution"""
        num_servers = 5
        servers = [Server(f"S{i}", 1) for i in range(num_servers)]
        lb = LoadBalancer(servers, STRATEGY_WEIGHTED)
        num_requests = 50
        ids = [lb.get_next_server(f"req{i}").id for i in range(num_requests)]
        expected_each = num_requests // num_servers
        for s in servers:
            self.assertEqual(ids.count(s.id), expected_each)

    def test_weighted_large_scale_simulation(self):
        """Weighted RR: 4 servers (4:3:2:1) with 10000 requests match weight ratios"""
        weights = [4, 3, 2, 1]
        total_weight = sum(weights)
        servers = [Server(f"S{i}", w) for i, w in enumerate(weights)]
        lb = LoadBalancer(servers, STRATEGY_WEIGHTED)
        for i in range(SIMULATION_REQUESTS):
            server = lb.get_next_server(f"req_{i}")
            server.handle_request()
        for s, w in zip(servers, weights):
            expected = SIMULATION_REQUESTS * w // total_weight
            self.assertEqual(s.request_count, expected)


class TestConsistentHashing(unittest.TestCase):

    def test_ch_single_server(self):
        """CH: single server handles all requests"""
        lb = LoadBalancer([], STRATEGY_CONSISTENT_HASH)
        lb.add_server(Server("S1"))
        for i in range(20):
            self.assertEqual(lb.get_next_server(f"req_{i}").id, "S1")

    def test_ch_deterministic(self):
        """CH: same key always maps to same server"""
        servers = [Server(f"S{i}") for i in range(NUM_RR_SERVERS)]
        lb = LoadBalancer(servers, STRATEGY_CONSISTENT_HASH)
        test_keys = ["user_1", "user_2", "user_3", "session_abc", "data_xyz"]
        for key in test_keys:
            first_result = lb.get_next_server(key).id
            for _ in range(10):
                self.assertEqual(lb.get_next_server(key).id, first_result)

    def test_ch_resilience_and_stability(self):
        """CH: removed server gets no traffic; unaffected keys stay on same server"""
        # TODO: Implement this according to the prompt.
        self.fail("Not implemented yet")

    def test_ch_stability_on_add(self):
        """CH: adding a server, majority of mappings stay the same"""
        # TODO: Implement this according to the prompt.
        self.fail("Not implemented yet")

    def test_ch_distribution(self):
        """CH: 5 servers with 10000 requests, no server handles > 50% and every server gets >= 1%"""
        # TODO: Implement this according to the prompt.
        self.fail("Not implemented yet")

    def test_ch_progressive_removal(self):
        """CH: progressively remove servers, traffic always routes to remaining"""
        servers = [Server(f"S{i}") for i in range(NUM_RR_SERVERS)]
        lb = LoadBalancer(servers, STRATEGY_CONSISTENT_HASH)

        remaining_ids = {f"S{i}" for i in range(NUM_RR_SERVERS)}
        for remove_idx in range(NUM_RR_SERVERS - 1):
            remove_id = f"S{remove_idx}"
            lb.remove_server(remove_id)
            remaining_ids.discard(remove_id)
            for i in range(10):
                result = lb.get_next_server(f"req_{remove_idx}_{i}")
                self.assertIsNotNone(result)
                self.assertIn(result.id, remaining_ids)


class TestConsistentHashReplicas(unittest.TestCase):

    def test_ring_size_after_adding_servers(self):
        """Ring contains exactly num_replicas entries per server"""
        ch = ConsistentHash()
        for i in range(NUM_RR_SERVERS):
            ch.add_node(Server(f"S{i}"))
        self.assertEqual(len(ch.ring), NUM_RR_SERVERS * DEFAULT_NUM_REPLICAS,
            f"Ring should have {NUM_RR_SERVERS * DEFAULT_NUM_REPLICAS} entries "
            f"({NUM_RR_SERVERS} servers x {DEFAULT_NUM_REPLICAS} replicas)")

    def test_ring_shrinks_on_removal(self):
        """Removing a server removes exactly num_replicas entries from ring"""
        ch = ConsistentHash()
        servers = [Server(f"S{i}") for i in range(NUM_RR_SERVERS)]
        for s in servers:
            ch.add_node(s)
        initial_size = len(ch.ring)
        ch.remove_node(servers[0])
        self.assertEqual(len(ch.ring), initial_size - DEFAULT_NUM_REPLICAS,
            f"Removing one server should remove exactly {DEFAULT_NUM_REPLICAS} entries from ring")

    def test_custom_replica_count(self):
        """Custom num_replicas creates correct number of ring entries"""
        custom_replicas = 10
        ch = ConsistentHash(num_replicas=custom_replicas)
        ch.add_node(Server("S1"))
        self.assertEqual(len(ch.ring), custom_replicas)
        ch.add_node(Server("S2"))
        self.assertEqual(len(ch.ring), 2 * custom_replicas)
        ch.remove_node(Server("S1"))
        self.assertEqual(len(ch.ring), custom_replicas)

    def test_replicas_improve_distribution(self):
        """With 50 replicas, every server gets 10-30% of traffic (ideal is 20%)"""
        # TODO: Implement this according to the prompt.
        self.fail("Not implemented yet")


class TestEdgeCases(unittest.TestCase):

    def test_empty_server_list_all_strategies(self):
        """Empty server list returns None for all strategies"""
        for strategy in [STRATEGY_ROUND_ROBIN, STRATEGY_WEIGHTED, STRATEGY_CONSISTENT_HASH]:
            lb = LoadBalancer([], strategy)
            self.assertIsNone(lb.get_next_server("req1"))

    def test_remove_nonexistent_server(self):
        """Removing a non-existent server doesn't crash"""
        for strategy in [STRATEGY_ROUND_ROBIN, STRATEGY_WEIGHTED, STRATEGY_CONSISTENT_HASH]:
            servers = [Server("S1"), Server("S2")]
            lb = LoadBalancer(servers, strategy)
            lb.remove_server("NonExistent")
            result = lb.get_next_server("req1")
            self.assertIsNotNone(result)

    def test_remove_all_servers_returns_none(self):
        """Removing all servers then get_next_server returns None"""
        lb = LoadBalancer([], STRATEGY_CONSISTENT_HASH)
        lb.add_server(Server("S1"))
        lb.add_server(Server("S2"))
        self.assertIsNotNone(lb.get_next_server("req1"))
        lb.remove_server("S1")
        lb.remove_server("S2")
        self.assertIsNone(lb.get_next_server("req1"))

    def test_constructor_init_vs_add_server(self):
        """Constructor initialization produces same routing as add_server"""
        servers_for_constructor = [Server(f"S{i}") for i in range(NUM_RR_SERVERS)]
        lb_constructor = LoadBalancer(servers_for_constructor, STRATEGY_CONSISTENT_HASH)

        lb_add = LoadBalancer([], STRATEGY_CONSISTENT_HASH)
        for i in range(NUM_RR_SERVERS):
            lb_add.add_server(Server(f"S{i}"))

        test_keys = [f"req_{i}" for i in range(20)]
        for key in test_keys:
            r1 = lb_constructor.get_next_server(key)
            r2 = lb_add.get_next_server(key)
            self.assertIsNotNone(r1)
            self.assertIsNotNone(r2)
            self.assertEqual(r1.id, r2.id)


if __name__ == '__main__':
    unittest.main()
