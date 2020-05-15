from .load_balancer import LoadBalancer
from utils import hash_fn

"""
Hash Key Load Balancer
Assigns keys in a consistent manner and rebalances using hash functions.
"""
class HashKeyLoadBalancer(LoadBalancer):
    def __init__(self):
        super().__init__()
        # Feel free to add things here

    # Adds a shard to the system and rebalance as necessary
    def add_shard(self, shard_name):
        super().add_shard(shard_name)
        self.rebalance() # all keys need to be re-mapped

    # Remove a shard to the system and rebalance as necessary
    def remove_shard(self, shard_name):
        kvstore = super().remove_shard(shard_name)
        self.rebalance() # all keys need to be re-mapped
        self.rekey(kvstore, shard_name) # re-assigns keys in removed shard

    # Re-Assigns the keys in the passed in kvstore
    def rekey(self, kvstore, shard_name):
        for key in list(kvstore.keys()):
            targetShardName = self.getShardNameForKey(key)
            if targetShardName != shard_name: # have to move this key
                val = kvstore.pop(key)
                targetShard = self.shards[targetShardName]
                targetShard.put(key, val)

    # Re-assigns all of the keys in the current configuration
    def rebalance(self):
        for (shard_name, shard) in self.shards.items():
            self.rekey(shard.kvstore, shard_name)

    # Gets the shard assigned to this key
    def getShardNameForKey(self, key):
        shardNum = hash_fn(key) % self.num_shards
        return self.shard_list[shardNum]

    # Puts a key in a certain shard, incrementing the access count
    def put(self, k):
        shard = self.shards[self.getShardNameForKey(k)]
        shard.put(k, 1)
