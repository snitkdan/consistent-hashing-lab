from shard import Shard 
import errors

class StateMonitor:
    def __init__(self):
        self.previous = None
        self.key_tracking = {}
        self.failed = False
        self.moveCounter = {} 
        self.key_history = {}
        self.num_shards = 0

    def put(self, key):
        self.key_tracking[key] = self.key_tracking.get(key, 0) + 1
        if key not in self.key_history:
            self.key_history[key] = []

    def check_valid(self, shards, debug=False):
        # process shards
        tracking = {}
        seen = set()
        for shard in shards:
            kv = shards[shard].kvstore
            for key in kv:
                if key in tracking:
                    self.failed = True
                    if debug:
                        for shard in shards:
                            print(shard, shards[shard].kvstore)
                    self.key_history[key].append((self.previous[key], self.key_tracking[key] - kv[key]))
                    self.key_history[key].append((shard, kv[key]))
                    raise errors.KeyPresentInMultipleShardsError("Found key '{}' in {} with count {} when already in {} with count {}\nhistory: {}".format(key, shard, kv[key], tracking[key], self.key_tracking[key] - kv[key], self.key_history[key]))
                tracking[key] = shard
        for shard in shards:
            kv = shards[shard].kvstore
            for key in kv:
                if kv[key] != self.key_tracking[key]:
                    self.failed = True
                    if debug:
                        for shard in shards:
                            print(shard, shards[shard].kvstore)
                    self.key_history[key].append((self.previous[key], self.key_tracking[key]))
                    self.key_history[key].append((tracking[key], kv[key]))
                    raise errors.ValueLostInTransitionError("The count was lost when moving key '{}' from {} to {}. Expected count {}, got count {}.\nhistory: {}".format(key, self.previous[key], shard, self.key_tracking[key], kv[key], self.key_history[key]))
                seen.add(key)
        if self.previous is not None:
            moved = 0
            for key in self.previous:
                if key in tracking and tracking[key] != self.previous[key]:
                    self.key_history[key].append((self.previous[key], self.key_tracking[key]))
                    self.moveCounter[key] = self.moveCounter.get(key, 0) + 1
                    moved += 1
            added = len(tracking) - len(self.previous)
            if (debug): print("Since previous check, moved {} keys and added {} keys".format(moved, added))
        self.previous = tracking
        
        diff = set(self.key_tracking.keys()) - seen
        if diff:
            self.failed = True
            if debug:
                for shard in shards:
                    print(shard, shards[shard].kvstore)
            raise errors.KeyLostInTransitionError("keys {} not found on any shard".format(diff))
        self.num_shards = len(shards)

    def get_stats(self, shards, debug=False):
        minimum = float('inf')
        maximum = 0
        total = len(self.key_tracking)
        nums = []
        print('\n--------------- stats ---------------')
        if self.failed:
            print("FAIL: Failed to complete workload without errors")
        
        status = {}
        for shard in shards:
            curr = len(shards[shard].kvstore)
            if curr < minimum:
                minimum = curr
            if curr > maximum:
                maximum = curr
            nums.append(curr)
            if (debug): print("{} has {} keys".format(shard, curr))

        total_moved = 0
        for key in self.moveCounter:
            if (debug): print('moved \'{}\' {} times'.format(key, self.moveCounter[key]))
            total_moved += self.moveCounter[key]
        print("moved {} keys out of {} keys a total of {} times".format(len(self.moveCounter), len(self.key_tracking), total_moved))

        mean = total / len(shards)
        variance = sum((i - mean) ** 2 for i in nums) / len(nums)
        print("minimum: {} \nmaximum: {} \nmean: {} \nvariance: {}".format(minimum, maximum, mean, variance))
        return {"num_keys": total, 
                "key_movement": total_moved, 
                "minimum": minimum, 
                "maximum": maximum, 
                "mean": mean, 
                "variance": variance, 
                "num_shards": self.num_shards} 
                