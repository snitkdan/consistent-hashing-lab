class Server:
    def __init__(self, name):
        self.name = name
        self.kvstore = {}
        self.access_tracking = {}

    def name(self):
        return self.name

    def put(self, k, v):
        self.kvstore[k] = v
        if k not in self.access_tracking:
            self.access_tracking[k] = 0
        self.access_tracking[k] += 1
        return self.kvstore[k]

    def get(self, k):
        if k not in self.access_tracking:
            self.access_tracking[k] += 1
        return self.kvstore[k]

    def remove(self, k):
        if k not in self.access_tracking:
            self.access_tracking[k] += 1