from state_monitor import StateMonitor
import argparse
from LoadBalancers.load_balancer_broken import BrokenLoadBalancer
from LoadBalancers.load_balancer_useless import UselessLoadBalancer
from LoadBalancers.load_balancer_simple import SimpleLoadBalancer
from LoadBalancers.load_balancer_hash_key import HashKeyLoadBalancer
from LoadBalancers.load_balancer_hash_shard_once import HashShardLoadBalancer
from LoadBalancers.load_balancer_hash_shard_mult import ConsistentHashingLoadBalancer

def run_test(load_balancer, workload, debug):
    sm = StateMonitor()
    errors = {}
    create_count = 0
    remove_count = 0
    f = open(workload, "r")
    for line in f:
        command, arg = line.split()
        if command == 'create':
            if (debug): errors["create_before_{}".format(create_count)] = sm.check_valid(load_balancer.shards)
            load_balancer.add_shard(arg)
            if (debug): errors["create_after_{}".format(create_count)] = sm.check_valid(load_balancer.shards)
            create_count += 1
        elif command == 'remove':
            if (debug): errors["remove_after_{}".format(remove_count)] = sm.check_valid(load_balancer.shards)
            load_balancer.remove_shard(arg)
            if (debug): errors["remove_after_{}".format(remove_count)] = sm.check_valid(load_balancer.shards)
            remove_count += 1
        elif command == 'put':
            load_balancer.put(arg)
            sm.put(arg)
            # sm.check_valid(load_balancer.shards)
    errors['final'] = sm.check_valid(load_balancer.shards)
    stats = sm.get_stats(load_balancer.shards)
    return stats, errors


def part0(workload, debug):
    score = 0
    # load_balancer = UselessLoadBalancer()
    load_balancer = BrokenLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    print(stats, errors)
    return score

def part1(workload, debug):
    score = 0
    load_balancer = SimpleLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    print(stats, errors)
    return score

def part2(workload, debug):
    score = 0
    load_balancer = HashKeyLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    print(stats, errors)
    return score

def part3(workload, debug):
    score = 0
    load_balancer = HashShardLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    print(stats, errors)
    return score
    
def part4(workload, debug):
    score = 0
    load_balancer = ConsistentHashingLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    print(stats, errors)
    return score

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='parsing options for running tests')
    parser.add_argument('-p', metavar='part', type=int, 
                        help='part in the lab [0..4]')
    parser.add_argument('-w', metavar='workload', type=str, 
                        help='workload to test this on [simple or default]', default='default')
    parser.add_argument('--debug', help='prints checks on create and remove', action='store_true')

    # parser.print_help()
    workloads = {"default": "workloads/simple_workload.txt", "simple": "workloads/simple_workload.txt"}
    out = parser.parse_args()
    part = out.p
    workload = out.w
    debug = out.debug
    # print(part, workload, debug)
    if part != None and (part < 0 or part > 5):
        print('There are only parts 0 to 4 inclusive')
        exit()
    if workload not in ['default', 'simple']:
        print('There are only two valid workloads \'simple\' or \'default\'') 
        exit()

    if part == None:
        workload = 'default'

    workload = workloads[workload]

    # Run all tests
    # part == None runs all tests

    if part == 0:
        print('running part0')
        part0(workload, debug)
    if part == None or part == 1:
        print('running part1')
        try:
            part1(workload, debug)
        except NotImplementedError:
            print('part1 was not implemented')
    if part == None or part == 2:
        print('running part2')
        try:
            part2(workload, debug)
        except NotImplementedError:
            print('part2 was not implemented')
    if part == None or part == 3:
        print('running part3')
        try:
            part3(workload, debug)
        except NotImplementedError:
            print('part3 was not implemented')
    if part == None or part == 4:
        print('running part4')
        try:
            part4(workload, debug)
        except NotImplementedError:
            print('part4 was not implemented')

    exit()