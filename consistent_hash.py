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
        # TODO: Implement this according to the prompt.
        pass

    def add_node(self, node):
        """Adds a node (server) to the ring with replicas."""
        # TODO: Implement this according to the prompt.
        pass

    def remove_node(self, node):
        """Removes a node and its replicas from the ring."""
        # TODO: Implement this according to the prompt.
        pass

    def get_node(self, key):
        """Returns the node responsible for the given key."""
        # TODO: Implement this according to the prompt.
        return None
