from shard import Shard 

"""Base LoadBalancer class"""
class LoadBalancer:
    def __init__(self):
        self.num_shards = 0  # Keeps track of the number of shards
        self.shards = {}     # Map from shard_name to Shard
        self.shard_list = [] # Keeps track of a list of shards 

    """Adds a shard using the shard_name"""
    def add_shard(self, shard_name):
        self.num_shards += 1
        self.shards[shard_name] = Shard(shard_name)
        self.shard_list.append(shard_name)

    """Removes a shard using the shard_name and returns the kvstore if there is one"""
    def remove_shard(self, shard_name):
        s = self.shards.pop(shard_name, None)
        if s:
            self.shard_list.remove(shard_name)
            self.num_shards -= 1
            return s.kvstore
        return None

    """Should be implemented in child classes"""
    def put(self, key, value=0):
        raise NotImplementedError