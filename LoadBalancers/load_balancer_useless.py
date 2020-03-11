from .load_balancer import LoadBalancer
from utils import hash_fn

"""
Useless Load Balancer
Doesn't rebalance shards, it puts everything in the first shard
"""
class UselessLoadBalancer(LoadBalancer):
    # Initialize data structures
    def __init__(self):
        super().__init__()

    # Adds a shard to the system and rebalances the system
    def add_shard(self, shard_name):
        super().add_shard(shard_name)

    # Removes a shard from the system and rebalances the system
    def remove_shard(self, shard_name):
        kvstore = super().remove_shard(shard_name)
        shard = self.shard_list[0]
        for key in kvstore:
            self.shards[shard].put(key, kvstore[key])

    # Store the given key in a shard
    def put(self, k):
        shard = self.shard_list[0]
        self.shards[shard].put(k, 1)
