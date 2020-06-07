from .load_balancer import LoadBalancer
from utils import hash_fn
from collections import defaultdict

"""
Table Indirection to deal with varying key popularity
"""
class TableIndirection(LoadBalancer):
    
    def __init__(self):
        super().__init__()
        self.num_buckets = 100
        self.currAccess = 0
        self.updateInterval = 5
        self.minDeviationFactor = 4
        self.serverToBuckets = defaultdict(lambda: [])
        self.serverToHeat = defaultdict(lambda: 0)
        self.bucketToServer = [None] * self.num_buckets
        self.bucketToHeat = [0] * self.num_buckets

    def add_shard(self, shard_name):
        # add new shard to overall system
        super().add_shard(shard_name)
        if len(self.shard_list) == 1:
            # initial system -> give all buckets to the only shard
            self.init_shard_metadata(shard_name)
        else:
            # take an arbitrary bucket from a server with multiple buckets
            chosenBucket = self.find_arbitrary_bucket()
            # give this new shard ownership of that bucket + rebalance as necessary (if possible)
            self.moveBucket(chosenBucket, shard_name)
            self.rebalance()

    def remove_shard(self, shard_name):
        # move all buckets to an arbitrary server
        buckets = list(self.serverToBuckets[shard_name])
        for bucket in buckets:
            dest_shard = self.find_arbitrary_shard_noteq(shard_name)
            self.moveBucket(bucket, dest_shard)
        # remove metadata about this shard
        del self.serverToHeat[shard_name]
        del self.serverToBuckets[shard_name]
        # rebalance as necessary
        self.rebalance() 
        # remove shard from the system
        super().remove_shard(shard_name)

    def put(self, key):
        # Get the bucket/server responsible for key
        bucket = self.getBucket(key)
        server = self.bucketToServer[bucket]
        # Incr the heat for the bucket + owner
        self.bucketToHeat[bucket] += 1
        self.serverToHeat[server] += 1
        # Put the key on the appropriate shard kvstore
        shard = self.shards[server]
        shard.put(key, 1)
        # Rebalance as necessary
        self.currAccess += 1
        if self.currAccess % self.updateInterval == 0:
            self.rebalance()

    ### UTILS

    ## Ensures that the maximum load on a given server is not more than twice the average (moving shards as necessary)
    def rebalance(self):
        # Local helper functions
        ## Getting the overloaded/idle server
        optHeatServer = lambda func: func(self.serverToHeat.keys(), key=(lambda k: self.serverToHeat[k]))
        maxHeatServer, minHeatServer = lambda: optHeatServer(max), lambda: optHeatServer(min)
        avgServerHeat = lambda: sum(self.serverToHeat.values()) / len(self.serverToHeat)
        ## Getting the heaviest bucket for overloaded server
        def maxHeatBucketForServer(server):
            bucketsSortedByHeat = sorted(range(len(self.bucketToHeat)), key=(lambda i: self.bucketToHeat[i]), reverse=True)
            bucketsSortedByHeatForServer = filter(lambda bucket: bucket in self.serverToBuckets[server], bucketsSortedByHeat)
            return list(bucketsSortedByHeatForServer)[0]
        # Get the server with the most cumulative bucket heat (overloaded server)
        maxHS = maxHeatServer()
        while self.serverToHeat[maxHS] > self.minDeviationFactor * avgServerHeat():
            maxHS_buckets = self.serverToBuckets[maxHS]
            if len(maxHS_buckets) == 1: # make sure we can spare buckets from maxHS
                return
            # Get the server with the least cumulative bucket heat (idle server)
            minHS = minHeatServer()
            # Move the heaviest bucket from the overloaded server to idle server
            chosenBucket = maxHeatBucketForServer(maxHS)
            self.moveBucket(chosenBucket, minHS)
            maxHS = maxHeatServer()

    ## Moves `bucket` from whoever owns it to `dst`
    def moveBucket(self, bucket, dst):
        # 1. move all keys owned by the old owner that belong to bucket to dst
        oldDst = self.bucketToServer[bucket]
        kvstore = self.shards[oldDst].kvstore
        for key in list(kvstore.keys()):
            currBucket = self.getBucket(key)
            if bucket == currBucket:
                targetShard = self.shards[dst]
                targetShard.put(key, kvstore.pop(key))
        # 2. update metadata reflecting new bucket ownership
        ## remove this bucket from old owner
        self.serverToHeat[oldDst] -= self.bucketToHeat[bucket]
        self.serverToBuckets[oldDst].remove(bucket)
        # add in this bucket to dst  
        self.serverToHeat[dst] += self.bucketToHeat[bucket]
        self.bucketToServer[bucket] = dst
        self.serverToBuckets[dst].append(bucket)

    ## Initializes shard metadata when adding the first shard
    def init_shard_metadata(self, shard_name):
        self.bucketToServer = [shard_name] * self.num_buckets
        self.serverToHeat[shard_name] = sum(self.bucketToHeat)
        self.serverToBuckets[shard_name] = list(range(self.num_buckets))

    ## Finds an arbitrary spare bucket (i.e. one in which the owner has other buckets)
    def find_arbitrary_bucket(self):
        for s in self.serverToBuckets:
            buckets = self.serverToBuckets[s]
            if len(buckets) > 1:
                return buckets[0]
        return None
    
    ## Returns first shard in shard_list not equal to `shard_name`
    def find_arbitrary_shard_noteq(self, shard_name):
        for s in self.shard_list:
            if s != shard_name:
                return s
        
    ## Returns the bucket for a given `key`
    def getBucket(self, key):
        return hash_fn(key) % self.num_buckets
