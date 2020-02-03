class Shard:
    def __init__(self, name):
        self.name = name
        self.kvstore = {}

    def put(self, k, v):
        self.kvstore[k] = self.kvstore.get(k, 0) + v
        return self.kvstore[k]

    def get(self, k):
        if k in self.kvstore:
            return self.kvstore[k]
        else:
            return None

    def remove(self, k):
        if k in self.kvstore:
            k,v = k, self.kvstore[k]
            del self.kvstore[k]
            return (k, v)
        else:
            return None