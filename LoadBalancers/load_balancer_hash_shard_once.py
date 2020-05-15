from .load_balancer import LoadBalancer
from utils import hash_fn
from bisect import bisect_left

"""
Hash Shard Load Balancer
Assigns keys in a consistent manner and rebalances using hash functions 
and slicing the key-space, which is defined over the range of [0, 2^32].
"""
class HashShardLoadBalancer(LoadBalancer):
    
    def __init__(self):
        super().__init__()
        self.key_space = []
        self.key_space_to_shard = {}

    # Adds a shard to the system and rebalance as necessary
    def add_shard(self, shard_name):
        super().add_shard(shard_name)
        self.add_shard_metadata(shard_name)
        self.rebalance()

   # Remove a shard to the system and rebalance as necessary
    def remove_shard(self, shard_name):
        kvstore = super().remove_shard(shard_name)
        self.remove_shard_metadata(shard_name)
        self.rebalance() # all keys need to be re-mapped
        self.rekey(kvstore, shard_name) # re-assigns keys in removed shard

    # Puts a key in a certain shard, incrementing the access count
    def put(self, k):
        shard = self.shards[self.getShardNameForKey(k)] 
        shard.put(k, 1)

    """ Metadata Utils """

    def add_shard_metadata(self, shard_name):
        val = hash_fn(shard_name)
        idx = bisect_left(self.key_space, val)
        self.key_space.insert(idx, val)
        self.key_space_to_shard[val] = shard_name

    def remove_shard_metadata(self, shard_name):
        val = hash_fn(shard_name)
        self.key_space.remove(val)
        del self.key_space_to_shard[val]

    """ Rebalance Utils """

    # Gets the shard assigned to this key
    def getShardNameForKey(self, key):
        val = hash_fn(key)
        key_slot = bisect_left(self.key_space, val) % len(self.key_space)
        shard_keyspace = self.key_space[key_slot]
        shard_name = self.key_space_to_shard[shard_keyspace]
        return shard_name
       
    # Re-assigns all of the keys in the current configuration
    def rebalance(self):
        for (shard_name, shard) in self.shards.items():
            self.rekey(shard.kvstore, shard_name)

    # Re-Assigns the keys in the passed in kvstore
    def rekey(self, kvstore, shard_name):
        for key in list(kvstore.keys()):
            targetShardName = self.getShardNameForKey(key)
            if targetShardName != shard_name: # have to move this key
                val = kvstore.pop(key)
                targetShard = self.shards[targetShardName]
                targetShard.put(key, val)