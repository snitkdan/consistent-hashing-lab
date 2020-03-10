from state_monitor import StateMonitor
from errors import Error
import argparse
from LoadBalancers.load_balancer_broken import BrokenLoadBalancer
from LoadBalancers.load_balancer_useless import UselessLoadBalancer
from LoadBalancers.load_balancer_simple import SimpleLoadBalancer
from LoadBalancers.load_balancer_hash_key import HashKeyLoadBalancer
from LoadBalancers.load_balancer_hash_shard_once import HashShardLoadBalancer
from LoadBalancers.load_balancer_hash_shard_mult import ConsistentHashingLoadBalancer

import inspect
import tqdm

# store builtin print
old_print = print
def new_print(*args, **kwargs):
    # if tqdm.tqdm.write raises error, use builtin print
    try:
        tqdm.tqdm.write(*args, **kwargs)
    except:
        old_print(*args, ** kwargs)
# globaly replace print with new_print
inspect.builtins.print = new_print

# Used for tqdm
import mmap
def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines

# Runs the implemented load_balancer against the workload
def run_test(load_balancer, workload, debug):
    sm = StateMonitor()
    create_count = 0 # Keeps track of how many creates went through
    remove_count = 0 # Keeps track of how many removes went through
    with open(workload) as f:
        # returns (None, sm.failed) if there are any errors
        # otherwise runs through the workload
        for line in tqdm.tqdm(f, total=get_num_lines(workload)):
            
            # Parse command
            command, arg = line.split()

            if command == 'create':

                if debug: print('\n{} {}'.format(command, arg))

                try:
                    check_valid(sm, load_balancer.shards, debug)
                except Error as e:
                    print('\nbefore create {}\n{}'.format(create_count, e))
                    return None, sm.failed

                load_balancer.add_shard(arg)

                try:
                    check_valid(sm, load_balancer.shards, debug)
                except Error as e:
                    print('\nafter create {}\n{}'.format(create_count, e))
                    return None, sm.failed

                create_count += 1

            elif command == 'remove':

                if debug: print('\n{} {}'.format(command, arg))

                try:
                    check_valid(sm, load_balancer.shards, debug)
                except Error as e:
                    print('\nbefore remove {}\n{}'.format(create_count, e))
                    return None, sm.failed

                load_balancer.remove_shard(arg)

                try:
                    check_valid(sm, load_balancer.shards, debug)
                except Error as e:
                    print('\nafter remove {}\n{}'.format(create_count, e))
                    return None, sm.failed

                remove_count += 1

            elif command == 'put':

                load_balancer.put(arg)
                sm.put(arg)

        # Final check 
        try:
            check_valid(sm, load_balancer.shards, debug)
        except Error as e:
            print('\nat the end\n{}'.format(e))
            return None, sm.failed

        stats = sm.get_stats(load_balancer.shards, debug)
        return stats, sm.failed

"""Checks validity using StateManager sm"""
def check_valid(sm, shards, debug):
    sm.check_valid(shards, debug)

def part0(workload, debug, stats, max_score=0):
    print('------------------------- testing part 0 -----------------------------------')
    load_balancer = BrokenLoadBalancer()
    s, fail = run_test(load_balancer, workload, debug)
    stats[0] = s
    score = eval_results(stats, fail, max_score, 0, debug)
    print("score: {}/{}".format(score, max_score))
    return score

def part1(workload, debug, stats, max_score=5):
    print('------------------------- testing part 1 -----------------------------------')
    load_balancer = SimpleLoadBalancer()
    s, fail = run_test(load_balancer, workload, debug)
    stats[1] = s
    score = eval_results(stats, fail, max_score, 1, debug)
    print("score: {}/{}".format(score, max_score))
    return score

def part2(workload, debug, stats, max_score=10):
    print('------------------------- testing part 2 -----------------------------------')
    load_balancer = HashKeyLoadBalancer()
    s, fail = run_test(load_balancer, workload, debug)
    stats[2] = s
    score = eval_results(stats, fail, max_score, 2, debug)
    print("score: {}/{}".format(score, max_score))
    return score

def part3(workload, debug, stats, max_score=15):
    print('------------------------- testing part 3 -----------------------------------')
    load_balancer = HashShardLoadBalancer()
    s, fail = run_test(load_balancer, workload, debug)
    stats[3] = s
    score = eval_results(stats, fail, max_score, 3, debug)
    print("score: {}/{}".format(score, max_score))
    return score

def part4(workload, debug, stats, max_score=20):
    print('------------------------- testing part 4 -----------------------------------')
    load_balancer = ConsistentHashingLoadBalancer()
    s, fail = run_test(load_balancer, workload, debug)
    stats[4] = s
    score = eval_results(stats, fail, max_score, 4, debug)
    print("score: {}/{}".format(score, max_score))
    return score

def eval_results(stats, fail, max_score, part, debug):
    if fail:
        return 0
    score = max_score

    if part == 2:
        # Checks that it doesn't deviate too much from the mean
        mean = stats[part]['mean']
        minimum = stats[part]['minimum']
        maximum = stats[part]['maximum']
        half = mean / 2
        if minimum < half or maximum > mean + half:
            score *= 0.5
    elif part == 3:
        # Check that there's lower key movement than part 2
        if 2 in stats:
            key_move_2 = stats[2]['key_movement']
            key_move_3 = stats[3]['key_movement']
            if key_move_2 < key_move_3:
                score *= 0.5
    elif part == 4:
        # Check that there's lower key movement than part 2
        if 2 in stats:
            key_move_2 = stats[2]['key_movement']
            key_move_3 = stats[3]['key_movement']
            if key_move_2 < key_move_3:
                score *= 0.5
        # Check that there's lower variance than part 3
        if 3 in stats:
            variance_3 = stats[3]['variance']
            variance_4 = stats[4]['variance']
            if variance_3 < variance_4:
                score *= 0.5

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

    if parts == None and workload != 'simple':
        workload = 'default'

    workload = workloads[workload]
    total = 0    # total points
    current = 0  # current points

    # Run all tests
    # part == None runs all tests

    stats = {}

    if parts != None and '0' in parts:
        part0(workload, debug, stats)

    if parts == None or '1' in parts:
        try:
            total += 5
            current += part1(workload, debug, stats, 5)
        except NotImplementedError:
            print('part1 was not implemented')

    if parts == None or '2' in parts:
        try:
            total += 10
            current += part2(workload, debug, stats, 10)
        except NotImplementedError:
            print('part2 was not implemented')

    if parts == None or '3' in parts:
        try:
            total += 15
            current += part3(workload, debug, stats, 15)
        except NotImplementedError:
            print('part3 was not implemented')

    if parts == None or '4' in parts:
        try:
            total += 20
            current += part4(workload, debug, stats, 20)
        except NotImplementedError:
            print('part4 was not implemented')

    print('---------------------------------------')
    if current == total == 0:
        score = 0.0
    else:
        score = round(current/total * 100, 2)
    print('total score: {}/{} ({}%)'.format(current, total, score))
