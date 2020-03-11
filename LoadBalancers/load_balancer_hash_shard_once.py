from .load_balancer import LoadBalancer
from utils import hash_fn

"""
Hash Shard Load Balancer
Assigns keys in a consistent manner and rebalances using hash functions 
and slicing the key-space, which is defined over the range of [0, 2^32].
"""
class HashShardLoadBalancer(LoadBalancer):
    def __init__(self):
        super().__init__()
        # Feel free to add things here

    # Adds a shard to the system and rebalance as necessary
    def add_shard(self, shard_name):
        super().add_shard(shard_name)
        # TODO rebalance
        raise NotImplementedError

    # Remove a shard to the system and rebalance as necessary
    def remove_shard(self, shard_name):
        kvstore = super().remove_shard(shard_name)
        # TODO rebalance
        raise NotImplementedError

    # Puts a key in a certain shard, incrementing the access count
    def put(self, k):
        # TODO Figure out where to put it
        raise NotImplementedError
