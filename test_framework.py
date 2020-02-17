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
    errors = []
    create_count = 0
    remove_count = 0
    f = open(workload, "r")
    for line in f:
        command, arg = line.split()
        if command == 'create':
            errors.append(["create_before_{}".format(create_count), sm.check_valid(load_balancer.shards, debug)])
            load_balancer.add_shard(arg)
            errors.append(["create_after_{}".format(create_count), sm.check_valid(load_balancer.shards, debug)])
            create_count += 1
        elif command == 'remove':
            errors.append(["remove_before_{}".format(create_count), sm.check_valid(load_balancer.shards, debug)])
            load_balancer.remove_shard(arg)
            errors.append(["remove_after_{}".format(create_count), sm.check_valid(load_balancer.shards, debug)])
            remove_count += 1
        elif command == 'put':
            load_balancer.put(arg)
            sm.put(arg)
            # sm.check_valid(load_balancer.shards)
    errors.append(['final', sm.check_valid(load_balancer.shards, debug)])
    stats = sm.get_stats(load_balancer.shards, debug)
    return stats, errors


def part0(workload, debug, max_score=0):
    # load_balancer = UselessLoadBalancer()
    load_balancer = BrokenLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    score = eval_results(stats, errors, max_score, 0)
    return score

def part1(workload, debug, max_score=5):
    load_balancer = SimpleLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    score = eval_results(stats, errors, max_score, 1)
    return score

def part2(workload, debug, max_score=10):
    load_balancer = HashKeyLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    score = eval_results(stats, errors, max_score, 2)
    return score

def part3(workload, debug, max_score=15):
    load_balancer = HashShardLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    score = eval_results(stats, errors, max_score, 3)
    return score

def part4(workload, debug, max_score=20):
    load_balancer = ConsistentHashingLoadBalancer()
    stats, errors = run_test(load_balancer, workload, debug)
    score = eval_results(stats, errors, max_score, 4)
    return score

def eval_results(stats, errors, max_score, part):
    score = max_score
    for error in errors:
        print("---{}---".format(error[0]))
        if error[1]:
            for problems in error[1]:
                print(problems)
            score = 0
        else:
            print("None")

    print(stats)
    # TODO: Probably case depending on how well each performs, I might calculate some bounds later
    if score < 0:
        score = 0
    return score

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='parsing options for running tests')
    parser.add_argument('-p', metavar='part', type=int, 
                        help='part in the lab [0..4]')
    parser.add_argument('-w', metavar='workload', type=str, 
                        help='workload to test this on [simple or default]', default='default')
    parser.add_argument('--debug', help='prints checks on create and remove', action='store_true')

    # parser.print_help()
    workloads = {"default": "Workloads/simple_workload.txt", "simple": "workloads/simple_workload.txt"}
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

    # TODO: Keep track of overall score
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