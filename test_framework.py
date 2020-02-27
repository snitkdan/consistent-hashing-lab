from state_monitor import StateMonitor
from errors import Error
import argparse
from LoadBalancers.load_balancer_broken import BrokenLoadBalancer
from LoadBalancers.load_balancer_useless import UselessLoadBalancer
from LoadBalancersSoln.load_balancer_simple import SimpleLoadBalancer
from LoadBalancersSoln.load_balancer_hash_key import HashKeyLoadBalancer
from LoadBalancersSoln.load_balancer_hash_shard_once import HashShardLoadBalancer
from LoadBalancersSoln.load_balancer_hash_shard_mult import ConsistentHashingLoadBalancer

def run_test(load_balancer, workload, debug):
    sm = StateMonitor()
    create_count = 0
    remove_count = 0
    f = open(workload, "r")
    for line in f:
        command, arg = line.split()
        # print(command, arg)
        if command == 'create':
            try:
                check_valid(sm, load_balancer.shards, debug)
                load_balancer.add_shard(arg)
                check_valid(sm, load_balancer.shards, debug)
            except Error as e:
                print(e, 'in create {}'.format(create_count))
                return None, sm.failed
            create_count += 1
        elif command == 'remove':
            try:
                check_valid(sm, load_balancer.shards, debug)
                load_balancer.remove_shard(arg)
                check_valid(sm, load_balancer.shards, debug)
            except Error as e:
                print(e, 'in create {}'.format(create_count))
                return None, sm.failed
                
            remove_count += 1
        elif command == 'put':
            # try:
                # check_valid(sm, load_balancer.shards, debug)
                # load_balancer.put(arg)
                # sm.put(arg)
                # check_valid(sm, load_balancer.shards, debug)
            # except Error as e:
            #     print(e, 'in create {}'.format(create_count))
            #     break
            load_balancer.put(arg)
            sm.put(arg)
    try:
        check_valid(sm, load_balancer.shards, debug)
    except Error as e:
        print(e, 'by the end')
        return None, sm.failed
    stats = sm.get_stats(load_balancer.shards, debug)
    return stats, sm.failed

def check_valid(sm, shards, debug):
    sm.check_valid(shards, debug)

def part0(workload, debug, max_score=0):
    # load_balancer = UselessLoadBalancer()
    print('------------------------- testing part 0 -----------------------------------')
    load_balancer = BrokenLoadBalancer()
    stats, fail = run_test(load_balancer, workload, debug)
    score = eval_results(stats, fail, max_score, 0, debug)
    return score

def part1(workload, debug, max_score=5):
    print('------------------------- testing part 1 -----------------------------------')
    load_balancer = SimpleLoadBalancer()
    stats, fail = run_test(load_balancer, workload, debug)
    score = eval_results(stats, fail, max_score, 1, debug)
    return score

def part2(workload, debug, max_score=10):
    print('------------------------- testing part 2 -----------------------------------')
    load_balancer = HashKeyLoadBalancer()
    stats, fail = run_test(load_balancer, workload, debug)
    score = eval_results(stats, fail, max_score, 2, debug)
    return score

def part3(workload, debug, max_score=15):
    print('------------------------- testing part 3 -----------------------------------')
    load_balancer = HashShardLoadBalancer()
    stats, fail = run_test(load_balancer, workload, debug)
    score = eval_results(stats, fail, max_score, 3, debug)
    return score

def part4(workload, debug, max_score=20):
    print('------------------------- testing part 4 -----------------------------------')
    load_balancer = ConsistentHashingLoadBalancer()
    stats, fail = run_test(load_balancer, workload, debug)
    score = eval_results(stats, fail, max_score, 4, debug)
    return score

def eval_results(stats, fail, max_score, part, debug):
    if fail or stats is None:
        return 0
    score = max_score

    # TODO: Probably case depending on how well each performs, I might calculate some bounds later
    if score < 0:
        score = 0
    return score

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='parsing options for running tests')
    parser.add_argument('-p', metavar='part', type=str, 
                        help='part in the lab [0..4]')
    parser.add_argument('-w', metavar='workload', type=str, 
                        help='workload to test this on [simple or default]', default='default')
    parser.add_argument('--debug', help='prints checks on create and remove', action='store_true')

    # parser.print_help()
    workloads = {"default": "Workloads/test_workload.txt", "simple": "Workloads/simple_workload.txt"}
    out = parser.parse_args()
    parts = out.p.split(',') if out.p else None
    workload = out.w
    debug = out.debug
    # print(part, workload, debug)
    if parts != None and (set(parts) - set(['0','1','2','3','4'])):
        print('There are only parts 0 to 4 inclusive')
        exit()
    if workload not in ['default', 'simple']:
        print('There are only two valid workloads \'simple\' or \'default\'') 
        exit()

    if parts == None:
        workload = 'default'

    workload = workloads[workload]
    total = 0
    current = 0

    # Run all tests
    # part == None runs all tests

    if parts != None and '0' in parts:
        part0(workload, debug)

    # TODO: Keep track of overall score
    if parts == None or '1' in parts:
        try:
            total += 5
            current += part1(workload, debug, 5)
        except NotImplementedError:
            print('part1 was not implemented')

    if parts == None or '2' in parts:
        try:
            total += 10
            current += part2(workload, debug, 10)
        except NotImplementedError:
            print('part2 was not implemented')

    if parts == None or '3' in parts:
        try:
            total += 15
            current += part3(workload, debug, 15)
        except NotImplementedError:
            print('part3 was not implemented')

    if parts == None or '4' in parts:
        try:
            total += 20
            current += part4(workload, debug, 20)
        except NotImplementedError:
            print('part4 was not implemented')

    print('---------------------------------------')
    print('total score: {}/{} ({})'.format(current, total, str(round(current/total * 100, 2))))
