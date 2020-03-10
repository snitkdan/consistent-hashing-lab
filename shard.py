"""Wrapper for a dictionary"""
class Shard:
    def __init__(self, server_name):
        self.server_name = server_name # Name of the server
        self.kvstore = {}              # internal kvstore

    # Increments count of key k by value v 
    def put(self, k, v):
        self.kvstore[k] = self.kvstore.get(k, 0) + v
        return self.kvstore[k]

    # Returns the count associated with k
    def get(self, k):
        if k in self.kvstore:
            return self.kvstore[k]
        else:
            return None

    # Removes a key from the kvstore if it exists
    def remove(self, k):
        if k in self.kvstore:
            k,v = k, self.kvstore[k]
            del self.kvstore[k]
            return (k, v)
        else:
            return None