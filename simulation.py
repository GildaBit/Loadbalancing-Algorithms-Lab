import random
import time
from server import Server
from consistent_hash import ConsistentHash
from load_balancer import (
    LoadBalancer,
    STRATEGY_ROUND_ROBIN,
    STRATEGY_WEIGHTED,
    STRATEGY_CONSISTENT_HASH,
)

# Simulation configuration
NUM_SERVERS = 3
NUM_REQUESTS = 10000
NUM_CH_SERVERS = 5
USER_ID_RANGE_MIN = 1000
USER_ID_RANGE_MAX = 9999
CH_USER_ID_RANGE_MIN = 10000
CH_USER_ID_RANGE_MAX = 99999
HEAVY_SERVER_WEIGHT = 3
LIGHT_SERVER_WEIGHT = 1
REPLICA_COUNTS = [1, 3, 50, 150]

# Strategies that should display standard deviation
EVEN_DISTRIBUTION_STRATEGIES = [STRATEGY_ROUND_ROBIN, STRATEGY_CONSISTENT_HASH]


def run_simulation(servers, requests, strategy):
    print(f"\n--- Running Simulation: {strategy} ---")
    lb = LoadBalancer(servers, strategy=strategy)
    
    # Track stats
    start_time = time.time()
    
    for req_id in requests:
        server = lb.get_next_server(req_id)
        if server:
            server.handle_request()
        else:
            print(f"Request {req_id} dropped (No Server)")
            
    duration = time.time() - start_time
    
    # Print Results
    total_requests = len(requests)
    print(f"Processed {total_requests} requests in {duration:.4f} seconds.")
    
    for s in servers:
        print(f"{s.id}: {s.request_count} requests (Weight: {s.weight})")
        
    # Calculate Standard Deviation (for evenness check)
    if strategy in EVEN_DISTRIBUTION_STRATEGIES and servers:
        # Note: CH won't be perfectly even with few requests/servers
        counts = [s.request_count for s in servers]
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        std_dev = variance ** 0.5
        print(f"Standard Deviation: {std_dev:.2f}")

def main():
    # 1. Round Robin
    servers_rr = [Server(f"Server-{i}") for i in range(NUM_SERVERS)]
    requests_rr = [f"User-{random.randint(USER_ID_RANGE_MIN, USER_ID_RANGE_MAX)}" for _ in range(NUM_REQUESTS)]
    run_simulation(servers_rr, requests_rr, STRATEGY_ROUND_ROBIN)
    
    # 2. Weighted
    # S1=HEAVY_SERVER_WEIGHT, S2=LIGHT_SERVER_WEIGHT, S3=LIGHT_SERVER_WEIGHT.
    # Expected: S1 gets 60%, S2 20%, S3 20%
    s_weighted = [
        Server("Server-Heavy", HEAVY_SERVER_WEIGHT),
        Server("Server-Light-1", LIGHT_SERVER_WEIGHT),
        Server("Server-Light-2", LIGHT_SERVER_WEIGHT),
    ]
    requests_w = [f"User-{i}" for i in range(NUM_REQUESTS)]  # Simple IDs
    run_simulation(s_weighted, requests_w, STRATEGY_WEIGHTED)
    
    # 3. Consistent Hashing
    servers_ch = [Server(f"Server-{i}") for i in range(NUM_CH_SERVERS)]
    requests_ch = [f"User-{random.randint(CH_USER_ID_RANGE_MIN, CH_USER_ID_RANGE_MAX)}" for _ in range(NUM_REQUESTS)]
    run_simulation(servers_ch, requests_ch, STRATEGY_CONSISTENT_HASH)
    
    # 4. Replica Count Comparison (Consistent Hashing)
    print("\n--- Replica Count Comparison (Consistent Hashing) ---")
    print(f"Routing {NUM_REQUESTS} requests to {NUM_CH_SERVERS} servers at different replica counts\n")
    requests_replica = [f"User-{i}" for i in range(NUM_REQUESTS)]
    for num_replicas in REPLICA_COUNTS:
        ch = ConsistentHash(num_replicas=num_replicas)
        servers_replica = [Server(f"S{i}") for i in range(NUM_CH_SERVERS)]
        for s in servers_replica:
            ch.add_node(s)
        for req_id in requests_replica:
            node = ch.get_node(req_id)
            if node:
                node.handle_request()
        counts = [s.request_count for s in servers_replica]
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        std_dev = variance ** 0.5
        pcts = [f"{s.id}: {s.request_count / NUM_REQUESTS * 100:.1f}%" for s in servers_replica]
        print(f"  Replicas={num_replicas:>3}  |  Std Dev: {std_dev:>7.1f}  |  {', '.join(pcts)}")

    # 5. Resilience Test (Consistent Hashing)
    print("\n--- Resilience Test (Consistent Hashing) ---")
    lb = LoadBalancer([], strategy=STRATEGY_CONSISTENT_HASH)
    s1 = Server("S1")
    s2 = Server("S2")
    s3 = Server("S3")
    lb.add_server(s1)
    lb.add_server(s2)
    lb.add_server(s3)
    
    req = "User-Special-1"
    assigned_1 = lb.get_next_server(req)
    if assigned_1:
        print(f"1. {req} assigned to {assigned_1.id}")
        
        print(f"Removing {assigned_1.id}...")
        lb.remove_server(assigned_1.id)
        
        assigned_2 = lb.get_next_server(req)
        if assigned_2:
             print(f"2. {req} assigned to {assigned_2.id}")
        
             if assigned_1.id != assigned_2.id:
                 print("SUCCESS: Traffic rerouted correctly.")
             else:
                 print("FAIL: Traffic not rerouted.")
        else:
            print("FAIL: No server found after removal.")
    else:
        print("FAIL: Initial assignment failed.")

if __name__ == "__main__":
    main()
