import random
import sys
import argparse
import collections
import statistics

random.seed(0)

# Get the workload we're trying to generate
parser = argparse.ArgumentParser(description='parsing options for running tests')
parser.add_argument('-d', metavar='dataset', type=str, 
                    help='dataset e.g. amazon0302.txt', default='com-dblp.ungraph.txt')
parser.add_argument('-s', metavar='skew', type=bool, 
                    help='True (only counts as False if omitted)', default=False)
out = parser.parse_args()
in_file = out.d

out_file = "test_skewed_workload" if out.s else "test_workload"
out_file += ".txt" if in_file == 'com-dblp.ungraph.txt' else "_{}".format(in_file)

# Set input/output files
f = open(in_file)
w = open(out_file, 'w')

print('generating ' + out_file)

# Creates 90 servers 
workload = ['create server{}\n'.format(server_num) for server_num in range(10,100)]
# Removes 9 servers
workload.extend(['remove server{}\n'.format(server_num) for server_num in range(9)])

# To track key popularity
keys = collections.defaultdict(lambda: 0)

# Parse file to create load
for line in f:
    if line[0] == '#': continue
    a, b = line.split()
    puts = ['put {}\n'.format(a)] * (10 if out.s else 1)
    workload.extend(puts)
    keys[a] += len(puts)

f.close()

# shuffles the workload
random.shuffle(workload)

# Creates 10 servers to begin with
for server_num in range(10):
    w.write('create server{}\n'.format(server_num))

# Records the workload
for line in workload:
    w.write(line)

# Finds where creates and removes are located
creates = [i for i in range(10)]
removes = []
for i in range(len(workload)):
    line = workload[i]
    if line.startswith('create'): creates.append(i + 10)
    if line.startswith('remove'): removes.append(i + 10)

from pprint import pprint
print('{} creates'.format(len(creates)))
pprint(creates, compact=True)
print('{} removes'.format(len(removes)))
pprint(removes)

# Key Statistics
print('{} keys in total'.format(len(keys)))
sorted_popularity = sorted(keys.values(), reverse=True)
top5 = sorted_popularity[:5]
bottom5 = sorted_popularity[-5:]
mean = statistics.mean(sorted_popularity)
variance = statistics.variance(sorted_popularity, mean)
print("mean key popularity = {}; variance of key popularity = {}".format(mean, variance))
print("top5 = {}".format(top5))
print("bottom5 = {}".format(bottom5))

# Finish writing the file
w.close()