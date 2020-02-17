# Consistent Hashing
What is load balancing? Load balancing is the act of distributing workloads in a way that is balanced across various resources. Consistent Hashing is a method for load balancing that utilizes a hash function to distribute workloads in a consistent manner. This lab will (hopefully) help you build intuition for why consistent hashing is used. 

In this lab, you will be writing various load balancers to handle a workload consisting of a sequence of puts, shard additions, and shard removals. The workload will be based on the [twitter social graph](http://an.kaist.ac.kr/traces/WWW2010.html). A simpler, sample workload will also be provided for you to test things separately. Each load balancer you write will become increasingly more complex until you eventually implement Consistent Hashing. (TODO: a workload with words.) 

## Prerequisites
- python3 or rust, both will probably be supported at some point in time

## Framework
To run the testing framework, you'll run something along the lines of `python3 test_framework.py`. This will run all four parts for you to implement and tell you the score you get for each part. There are 4 parts in this lab for you to implement. You can run `python3 test_framework.py -h` to get a list of options you can run this with. 

## Some terminology
Terminology is everything. It will make or break your understanding of papers, presentations, or conversations, so we will try to define some terms you may not have heard of before. We'll also define some other terminology that won't be used in the lab, but will be good to know if you continue to take systems-related courses. 
* Servers process requests from clients. 
* Nodes are communication endpoints, e.g. if you have a client and a server, you have two nodes. 
* Sharding is a way to partition data into shards, which are faster to utilize and easier to manage. 
* Latency is how long it takes to do something after you requested it to be done.
* Throughput is how much stuff can be processed in a given amount of time.

## Classes

### StateMonitor - Has no direct access to shards, monitors state during remove and add
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

## Grading
\[TBD\], hopefully something reasonable. Since the testing framework is provided to you, we will just download the files related to the load balancers you implement and run them on a clean copy of the testing framework. If you need to implement any helper functions for the labs, either implement them in the load balancer or inside utils.py. 

## Realism
Is this a realistic problem setup (or is everything just a simulation)? Oftentimes, servers need to be shut down for updates and then brought back up, so the work handled by those servers need to be redirected to servers that will be alive during the update. (TODO: Write some more stuff here, probably.)

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
Moving all the keys each time might not be necessary, especially for the case when the keys get assigned to the same location. Here, we will try to avoid redistributing keys unnecessarily. Implement `LoadBalancers/load_balancer_hash_shard_once.py`.

How many keys moved when you added and removed shards? 

## Part 4: Consistent Hashing
TODO: Write some buildup for this part
Now we hash the server name multiple times. Implement `LoadBalancers/load_balancer_hash_shard_mult.py`.

## Reflection questions
1. What happens when you increase the number of times you hash the server name in the consistent hashing scheme? 
2. What are some benefits/drawbacks when increasing the number of times that you hash the server name?
3. How might you balance the workload on a distribution in which some keys were a lot more popular than other keys?

## Acknowledgements 
The sections are based on this [video](https://cs.brown.edu/video/392/?quality=hires) by Doug Woos. This was a project for CSE599c: Data Center Systems offered in Winter 2020. 
Contact nowei@cs.washington.edu if there's any problems.
