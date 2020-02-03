from shard import Shard 
import errors

class StateMonitor:
    def __init__(self):
        self.previous = None
        self.key_tracking = {}
        self.failed = False
        pass

    def put(self, key):
        self.key_tracking[key] = self.key_tracking.get(key, 0) + 1

    def check_valid(self, shards):
        errors = []
        # process shards
        tracking = {}
        seen = set()
        for shard in shards:
            kv = shards[shard].kvstore
            for key in kv:
                if key in tracking:
                    errors.append("Found key '{}' in {} when already in {}".format(key, shard, tracking[key]))
                tracking[key] = shard
                if kv[key] != self.key_tracking[key]:
                    errors.append("The count was lost when moving key '{}'".format(key))
                seen.add(key)
        if self.previous is not None:
            moved = 0
            # print(self.previous, tracking)
            for key in self.previous:
                if key in tracking and tracking[key] != self.previous[key]:
                    moved += 1
            added = len(tracking) - len(self.previous)
            print("Since previous check, moved {} keys and added {} keys".format(moved, added))
        self.previous = tracking
        
        diff = set(self.key_tracking.keys()) - seen
        for key in diff:
            errors.append("key '{}' not found on any shard".format(key))

        if errors:
            print("FAIL")
            self.failed = True
            for e in errors:
                print(e)
        else:
            # print("PASS")
            pass

    def get_stats(self, shards):
        minimum = float('inf')
        maximum = 0
        total = len(self.key_tracking)
        # maybe do a variance calculation
        print('\n--------------- stats ---------------')
        if self.failed:
            print("FAIL\nFailed to complete workload without errors")
        status = {}
        for shard in shards:
            curr = len(shards[shard].kvstore)
            if curr < minimum:
                minimum = curr
            if curr > maximum:
                maximum = curr
            print("{} has {} keys".format(shard, curr))
        print("minimum: {} \nmaximum: {} \naverage: {}".format(minimum, maximum, total / len(shards)))
