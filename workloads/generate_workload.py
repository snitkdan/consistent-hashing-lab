import random

random.seed(0)

f = open('com-dblp.ungraph.txt')
w = open('test_workload.txt', 'w')

print('generating test_workload.txt')

workload = ['create server{}\n'.format(server_num) for server_num in range(10,100)]
workload.extend(['remove server{}\n'.format(server_num) for server_num in range(9)])
for line in f:
    if line[0] == '#': continue
    a, b = line.split()
    workload.append('put {}\n'.format(a))
random.shuffle(workload)
f.close()

for server_num in range(10):
    w.write('create server{}\n'.format(server_num))

for line in workload:
    w.write(line)

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

w.close()