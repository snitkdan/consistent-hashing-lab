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
        self.key_space = {}
        self.min_key = -1 # the minimum hash(shard_name)
        self.min_shard = "" # shard_name corresponding to self.min_key

    # Adds a shard to the system and rebalance as necessary
    def add_shard(self, shard_name):
        super().add_shard(shard_name)
        if len(self.key_space) == 0: # don't have any other shards
            self.min_key = hash_fn(shard_name)
            self.min_shard = shard_name
        else: # have other shards
            src = self.getMaxLT(hash_fn(shard_name)) # this is the old destination for our key-range
            if self.min_key > hash_fn(shard_name):
                self.min_key = hash_fn(shard_name)
                self.min_shard = shard_name
            self.move_keys(src, shard_name, False)
        self.key_space[shard_name] = hash_fn(shard_name)
   
   # Remove a shard to the system and rebalance as necessary
    def remove_shard(self, shard_name):
        self.key_space.pop(shard_name)
        if len(self.key_space) > 0:
            dst = self.getMaxLT(hash_fn(shard_name))
            self.move_keys(shard_name, dst, True)
            if self.min_shard == shard_name:
                sorted_dict = sorted(a.items(), key = lambda x: x[1])
                self.min_key = sorted_dict[1]
                self.min_shard = sorted_dict[0]
        super().remove_shard(shard_name)

    # Puts a key in a certain shard, incrementing the access count
    def put(self, k):
        shard = self.shards[self.getMaxLT(k)]
        shard.put(k, 1)
    
    """ UTILS """

    def should_move_to_dst(self, src, dst, key):
        key_val = hash_fn(key)
        # define predicates
        src_hash, dst_hash = hash_fn(src), hash_fn(dst)
        dst_gt_src = dst_hash > src_hash
        key_val_gt_dst = dst_hash < key_val
        key_val_lte_src = src_hash >= key_val
        return (dst_gt_src and key_val_gt_dst) or ((not dst_gt_src) and key_val_lte_src)

    def move_keys(self, src, dst, override):
       keys = list(self.shards[src].kvstore.keys())
       for k in keys:
           if self.should_move_to_dst(src, dst, k) or override:
               val = self.shards[src].kvstore.pop(k)
               self.shards[dst].put(k, val)

    def getMaxLT(self, key):
        key_val = hash_fn(key)
        if key_val <= self.min_key:
            return self.min_shard
        key_partition_val = self.min_key
        key_partition_shard = self.min_shard 
        for (shard_name, shard_partition_val) in self.key_space.items():
            if shard_partition_val > key_partition_val and shard_partition_val < key_val:
                key_partition_val = shard_partition_val
                key_partition_shard = shard_name
        return key_partition_shard
