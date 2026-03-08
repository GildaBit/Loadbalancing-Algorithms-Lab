# Author: Gilad Bitton
# RedID: 130621085

import hashlib
import bisect

DEFAULT_NUM_REPLICAS = 3
HASH_ENCODING = "utf-8"
HEX_BASE = 16


class ConsistentHash:
    def __init__(self, num_replicas=DEFAULT_NUM_REPLICAS, nodes=None):
        self.num_replicas = num_replicas
        self.ring = []
        self.nodes = {}  # Map hash to node ID (or object)

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        """Returns the integer hash of the key using MD5."""
        return int(hashlib.md5(key.encode(HASH_ENCODING)).hexdigest(), HEX_BASE)

    def add_node(self, node):
        """Adds a node (server) to the ring with replicas."""
        # Loops through number of replicas and adds them to the ring.
        for i in range(self.num_replicas):
            # key is combination of node ID and index
            replica_key = f"{node.id}:{i}"
            # Hashes the replica key and adds it to the ring and nodes mapping
            hash_val = self._hash(replica_key)
            self.ring.append(hash_val)
            self.nodes[hash_val] = node
        # sorts the ring to maintain order
        self.ring.sort()

    def remove_node(self, node):
        """Removes a node and its replicas from the ring."""
        for i in range(self.num_replicas):
            # gets the key to remove based on hashing function
            replica_key = f"{node.id}:{i}"
            hash_val = self._hash(replica_key)
            # removes the hash from the nodes mapping
            if hash_val in self.nodes:
                del self.nodes[hash_val]
            # finds current leftmost index of the node and removes it from the ring
            index = bisect.bisect_left(self.ring, hash_val)
            if index < len(self.ring) and self.ring[index] == hash_val:
                self.ring.pop(index)

    def get_node(self, key):
        """Returns the node responsible for the given key."""
        # if empty ring, return None
        if not self.ring:
            return None
        
        # gets the hash of the key and finds the appropriate node using bisect
        hash_val = self._hash(key)
        index = bisect.bisect_right(self.ring, hash_val) % len(self.ring)
        node_hash = self.ring[index]
        return self.nodes[node_hash]
