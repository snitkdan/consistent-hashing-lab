from shard import Shard 

class LoadBalancer:
    def __init__(self):
        self.num_shards = 0
        self.shards = {}
        self.shard_list = []

    def add_shard(self, shard_name):
        self.num_shards += 1
        self.shards[shard_name] = Shard(shard_name)
        self.shard_list.append(shard_name)

    def remove_shard(self, shard_name):
        s = self.shards.pop(shard_name, None)
        if s:
            self.shard_list.remove(shard_name)
            return s.kvstore
        return None

    def put(self, key, value=0):
        raise NotImplementedError