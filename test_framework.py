from state_monitor import StateMonitor
from load_balancer_useless import UselessLoadBalancer
from load_balancer_broken import BrokenLoadBalancer

if __name__ == '__main__':
    sm = StateMonitor()
    # lb = UselessLoadBalancer()
    lb = BrokenLoadBalancer()
    f = open("simple_workload.txt", "r")
    for line in f:
        command, arg = line.split()
        if command == 'create':
            sm.check_valid(lb.shards)
            lb.add_shard(arg)
            sm.check_valid(lb.shards)
        elif command == 'remove':
            sm.check_valid(lb.shards)
            lb.remove_shard(arg)
            sm.check_valid(lb.shards)
        elif command == 'put':
            lb.put(arg)
            sm.put(arg)
            # sm.check_valid(lb.shards)
    sm.check_valid(lb.shards)
    sm.get_stats(lb.shards)