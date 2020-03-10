# Consistent Hashing Lab Overview
What is load balancing? Load balancing is the act of distributing workloads in a way that is balanced across various resources. Consistent Hashing is a method for load balancing that utilizes a hash function to distribute workloads in a consistent manner. This lab will (hopefully) help you build intuition for how consistent hashing works and why it is used. 

In this lab, you will be writing various load balancers to handle a workload consisting of a sequence of puts, shard additions, and shard removals. 

## Some terminology
Terminology is everything. It will make or break your understanding of papers, presentations, or conversations, so we will try to define some terms you may not have heard of before. We'll also define some other terminology that won't be used in the lab, but will be good to know if you continue to take systems-related courses. 
* Servers process requests from clients. 
* Nodes are communication endpoints, e.g. if you have a client and a server, you have two nodes. 
* Sharding is a way to partition data into shards, which are faster to utilize and easier to distribute. 
* Bandwidth is how much data can be sent from one point to another in a given amount of time.
* Latency is how long it takes to do something after you requested it to be done.
* Throughput is how much stuff can be processed in a given amount of time.

## Motivation
Why does this matter? Load balancing is important in distributed systems. When we talk about load balancing, we usually talk about balancing some load in terms of storage or computational workload. What if we didn't do any load balancing? Imagine if you have 30 server and your application only runs and serves on a single server. You'd have 29 idle machines that are just sitting there, which isn't great in terms of resource utilization. Then if the workload was larger than a single server could handle, the application may just flop. The latency and throughput would be miserable and you might lose customers or their confidence in you drops and they go with some competitor. A way to fix this would be distribute the work somehow, i.e. to shard or partition the work such that the workload isn't too great on any given server. 

A load is like a strain on the system, so load balancing is a way to balance this strain so that the system isn't overwhelmed. There's many types of loads we can balance, like memory, compute, or network load. In a memory-constrained environment, we might want to partition the data so that it's stored in different places. In a compute-constrained environment, we might want to distribute the jobs to servers evenly. In a network-constrained environment, we might want to balance according to the bandwidth available to a given server. 

Some applications include: 
- Splitting work to efficiently analyze giant social graphs on Facebook or Twitter
- Redirecting work based on server outages
- Deciding which thread should run next in a multi-threaded program

There are many other applications and there are many places in which it shows up, so it's good to have some knowledge about some basic load balancing schemes. In our load balancing schemes, we want to distribute the workload as even as possible. One way we might want to do this is through hashing, which has probabilistic guarantees of uniformity; so why don't we just hash all the work and assign it to some corresponding server? The number of servers we have may change, so the assignment of work has to change whenever the numbers of servers changes, which may incur some cost in terms of maintaining the state stored related to the data. 

## Problem setup
In this lab, you will be implementing basic load balancers for a sharded key-value store, mapping keys to shards and keys to the number of times that the key has appeared within the workload. Working through the workload, shards will be added and deleted so you'll have to balance the keys in a consistent manner so that you can update them again later. 

### Realism
Is this a realistic problem setup (or is everything just a simulation)? Oftentimes, servers need to be shut down for repairs or updates and then brought back up, so the work handled by/data residing in those servers need to be redirected to servers that will be alive during the update. Or maybe new servers will be introduced to help further balance the load. Servers may hold one or more shards at a time, but in our simple example, we'll only work with one shard at a time. 

# Framework
## Prerequisites
- python3

## Data
The workload will be based on the [dblp collaboration network](https://snap.stanford.edu/data/com-DBLP.html). A simpler, sample workload will also be provided for you to test things separately. Each load balancer you write will become increasingly more complex until you eventually implement Consistent Hashing. 

### Getting the data
1. To download the data, navigate to the Workloads folder, run  
`wget https://snap.stanford.edu/data/bigdata/communities/com-dblp.ungraph.txt.gz` 
2. unzip it, run `gunzip com-dblp.ungraph.txt.gz`. 
3. Then run `python3 generate_workload.py`.

## Testing
To run the testing framework, you'll run something along the lines of `python3 test_framework.py`. This will run all four parts for you to implement and tell you the score you get for each part. There are 4 parts in this lab for you to implement. You can run `python3 test_framework.py -h` to get a list of options you can use. Some parts may rely on the other parts for correctness, e.g. comparisons between the variance in parts 3 and 4 for correctness. 

More detail about how the testing framework can be found in the Appendix.

## What you'll be implementing
All load balancers are a subclass of LoadBalancer and must implement the following methods:
- `add_shard(shard_name)`: Add a new shard into the system and rebalance accordingly.
- `remove_shard(shard_name)`: Remove a shard from the system and rebalance accordingly.
- `put(key)`: Assigns a specific key to a shard based on some scheme. 

**Note**: `add_shard` and `remove_shard` should first call the parent `add_shard` and `remove_shard` functions. You may want to look at LoadBalancer's `add_shard`, `remove_shard`, and the data it keeps track of. 

## Part 0: How do I put something in a shard?
You can't load balance if you don't have a load to balance. `LoadBalancers/load_balancer_useless.py` shows how to put things in shards within the framework. This is a useless load balancer because all the work is distributed to the first node. If this server dies, then all the information is lost unless someone backed it up (look up State Machine Replication if interested). Or if there's a lot of traffic, then the latency and throughput might not be so great. 

## Part 1: Simple Load Balancer
A naive way to load balance would be to assign everything based on the first character of the key and modding by the number of shards. Implement `LoadBalancers/load_balancer_simple.py`. 

What did the distribution of keys look like? TODO: Talk about variance

## Part 2: Hash the key
If you did the last part, hopefully you saw that there was an uneven distribution of keys. We will fix this by introducing hashes into the mix. (TODO: Talk about hashing.) This time, we will hash the key and then mod by the number of shards. Implement `LoadBalancers/load_balancer_hash_key.py`.

What happened when you add and remove shards? Each time you add or remove a shard, how many keys do you need to move?

## Part 3: Hash the Server Name
TODO: Write some buildup for this part
Moving all the keys each time might not be necessary, especially for the case when the keys get assigned to the same location. Here, we will try to avoid redistributing keys unnecessarily. To do this, you'll want to divide up the key-space somehow. The way we suggest is hashing the server name, since in expectation hashes are roughly uniformly distributed. [TODO: Probably provide resources for why.] 

The hash function we will be using will be python's hash function but with a mask so that hashes are in the range(0, 2^32). This has some implications Pay close attention to when the solution wraps around 0. 

Implement `LoadBalancers/load_balancer_hash_shard_once.py`.

How many keys moved when you added and removed shards? 

**Hint**: You might want to look into the bisect library.

## Part 4: Consistent Hashing
TODO: Write some buildup for this part
Now we hash the server name multiple times. We recommend going through the possible cases for hashing, since this is harder than the previous section. 

Implement `LoadBalancers/load_balancer_hash_shard_mult.py`.

**Hint**: Try to simplify the problem into dealing with specific slices. 

## Grading
Since the testing framework is provided to you, we will just download the files related to the load balancers you implement and run them on a clean copy of the testing framework. If you need to implement any helper functions for the labs, either implement them in the load balancer or inside utils.py. 
What we're looking for:
Generally: 
- All keys exist on some shard by the end of the workload. 
- Keys get assigned consistently. 
Then the tests only process test the following if the relevant parts are present:
**Part 1**: Not much. 
**Part 2**: Relatively uniform distribution of work. 
**Part 3**: Lower number of key movements than Part 2. 
**Part 4**: Lower number of key movements than Part 2, lower variance than Part 3. 
Note that these trends may not hold for smaller workloads, since there is generally more variance in smaller workloads than larger ones; so we recommend only using smaller workloads to debug the correctness of your implementation. 

## Reflection questions
1. What happens when you increase the number of times you hash the server name in the consistent hashing scheme? 
2. What are some benefits/drawbacks when increasing the number of times that you hash the server name?
3. How might you balance the workload on a distribution in which some keys were a lot more popular than other keys?
4. Workload changing over time question TODO

## Notes
 - It can be assumed that there will always be at least one shard in the system. 
 - Python's hash(...) function by default uses a random seed, so you might want to set `export PYTHONHASHSEED=0` when debugging your code. To unset it, just do `unset PYTHONHASHSEED`.
 - We recommend using the `hash_fn` provided instead of python's `hash` function because the number of bits returned by the Python hash function is not consistent. 
 - Feel free to use any standard python3 library.
 - If you're interested in how to load balance according to the distribution of work, consider looking up Slicer or Elastic Load Balancer.
 - There may be some weird issues with tqdm, you can replace it with 
 ...........................................................................

# Appendix

## Classes

### StateMonitor - Has no direct access to shards, monitors state before and after removes and adds
* Keeps track of states between checks, the number of times that keys have been updated, and the number of times that keys have been moved
* `check_valid` checks for state violations:
  * Make sure that the same key wasn’t assigned to different shards
    * Validated by going through each key in a shard and mapping each key to a shard and making sure that each key is only assigned once
  * Make sure that the information stored in the kv pair match what we expect them to be, counts of the number of times the key has been processed 
    * Validated by keeping an internal count as well to make sure that no information is lost
  * Make sure all keys actually exist on a shard
    * Validated by taking a set difference between known keys and seen keys during the check
* Returns whether any errors occurred between checks
* Calculates and outputs the statistics 
  * Statistics include mean, variance, maximum, minimum, and the number of times that keys have been moved

### Shard - Wrapper for a dictionary, but you should really only be calling put
* Contains a name and a key-value store, this is mostly there to hash server names
* `put` puts the key there and increments the count by the value passed in
* `remove` removes a key and returns a kv pair if it exists
* `get` returns the value if it exists, otherwise returns None

### LoadBalancer - Parent class to be inherited from for other load balancers
* Contains shards
* Contains a function to remove a shard
  * Removing a shard removes the shard and returns the kvstore for that shard, which needs to be redistributed to the remaining shards. Removing a shard also leads to needing to move keys around on the remaining shards.
* Contains a function to add a shard
  * Adding a shard requires redistributing keys
* Contains a function to put keys into the shard
  * Not implemented, but ideally implemented in child classes
* Child classes should call the super method to add/remove shards [already there for you]

## Future work:
- Implement everything in Rust and let people do it in either
- 

## Acknowledgements 
The sections are based on this [video](https://cs.brown.edu/video/392/?quality=hires) by Doug Woos. 

This was a project for CSE599c: Data Center Systems offered in Winter 2020. 

Contact nowei@cs.washington.edu if there's any problems.
