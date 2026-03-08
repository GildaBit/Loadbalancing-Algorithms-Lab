from consistent_hash import ConsistentHash

# Strategy constants
STRATEGY_ROUND_ROBIN = "ROUND_ROBIN"
STRATEGY_WEIGHTED = "WEIGHTED"
STRATEGY_CONSISTENT_HASH = "CONSISTENT_HASH"


class LoadBalancer:
    def __init__(self, servers=None, strategy=STRATEGY_ROUND_ROBIN):
        self.servers = servers if servers else []
        self.strategy = strategy
        self.current_index = 0
        
        # weighted server list for weighted strategy
        self.weighted_servers = []
        
        # Consistent Hash helper
        self.consistent_hash = ConsistentHash()
        
        if self.servers:
            for s in self.servers:
                self.add_server_internal(s)

    def add_server(self, server):
        self.servers.append(server)
        self.add_server_internal(server)

    def add_server_internal(self, server):
        if self.strategy == STRATEGY_CONSISTENT_HASH:
            self.consistent_hash.add_node(server)
        elif self.strategy == STRATEGY_WEIGHTED:
            # adding internal server for weighted strategy
            for _ in range(server.weight):
                self.weighted_servers.append(server)

    # remove server from both main and internal lists
    def remove_server(self, server_id):
        # new server list without the removed server
        server_obj = next((s for s in self.servers if s.id == server_id), None)

        # if server not found, return early
        if not server_obj:
            return

        # removes the server from the main servers list
        self.servers.remove(server_obj)

        # Calls the internal remove method for the hash ring implementation
        if self.strategy == STRATEGY_CONSISTENT_HASH:
            self.consistent_hash.remove_node(server_obj)
        
        # For weighted strategy, we need to remove all instances of the server from the weighted_servers list.
        elif self.strategy == STRATEGY_WEIGHTED:
            self.weighted_servers = [s for s in self.weighted_servers if s.id != server_id]
        

    def get_next_server(self, request_id):
        if not self.servers:
            return None

        if self.strategy == STRATEGY_ROUND_ROBIN:
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            return server

        # For weighted strategy, we can simply return the next server in the weighted_servers list.
        elif self.strategy == STRATEGY_WEIGHTED:
            server = self.weighted_servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.weighted_servers)
            return server

        # For consistent hashing, we use the request_id to find the appropriate server.
        elif self.strategy == STRATEGY_CONSISTENT_HASH:
            return self.consistent_hash.get_node(request_id)

        return None
