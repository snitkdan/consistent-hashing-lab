from .load_balancer import LoadBalancer
from utils import hash_fn

class BrokenLoadBalancer(LoadBalancer):
    def __init__(self):
        super().__init__()

    def add_shard(self, shard_name):
        super().add_shard(shard_name)
        # TODO rebalance 
        # Also remember to remove the keys from the shards that moved

    def remove_shard(self, shard_name):
        kvstore = super().remove_shard(shard_name)
        # TODO rebalance

    def put(self, k):
        # Figure out where to put it
        shard = self.shard_list[0]
        self.shards[shard].put(k, 1)
