from .load_balancer import LoadBalancer
from utils import hash_fn

class SimpleLoadBalancer(LoadBalancer):
    def __init__(self):
        super().__init__()

    def add_shard(self, shard_name):
        super().add_shard(shard_name)
        raise NotImplementedError

    def remove_shard(self, shard_name):
        kvstore = super().remove_shard(shard_name)
        raise NotImplementedError

    def put(self, k):
        # Figure out where to put it
        raise NotImplementedError
