# Consistent Hashing Lab Overview
What is load balancing? Load balancing is the act of distributing workloads in a way that is balanced across various resources. Consistent Hashing is a method for load balancing that utilizes a hash function to distribute workloads in a consistent manner and reduces the amount of key movement during configuration changes. This lab will (hopefully) help you build intuition for how consistent hashing works and why it is used. 

In this lab, you will be writing various load balancers to handle a workload consisting of a sequence of puts, shard additions, and shard removals. 

## Some terminology
Terminology is everything. It will make or break your understanding of papers, presentations, or conversations, so we will try to define some terms you may not have heard of before. We'll also define some other terminology that may or may not be used in the lab, but will be good to know if you continue to take systems-related courses. 
* Servers process (serve) requests from clients. 
* Nodes are communication endpoints, e.g. if you have a client and a server, you have two nodes. 
* Sharding is a way to partition data into shards, which are faster to utilize and easier to distribute. 
* Bandwidth is how much data can be sent from one point to another in a given amount of time.
* Latency is how long it takes to do something after you requested it to be done.
* Throughput is how much stuff can be processed in a given amount of time.

## Motivation
Why does this matter? Load balancing is important in distributed systems. When we talk about load balancing, we usually talk about balancing some load in terms of storage or computational workload. What if we didn't do any load balancing? 

Imagine if you have 30 servers and your application only runs and serves on a single server. You'd have 29 idle machines that are just sitting there, which isn't great in terms of resource utilization. Then if the workload was larger than a single server could handle, the application may just flop. The latency and throughput would be miserable and you might lose customers or their confidence in you drops and they go with some competitor. A way to fix this would be to distribute the work somehow, i.e. to shard or partition the work such that the workload isn't too great on any given server. 

A load is like a strain on the system, so load balancing is a way to balance this strain so that the system isn't overwhelmed. There's many types of loads we can balance, like memory, compute, or network load. In a memory-constrained environment, we might want to partition the data so that it's stored in different places. In a compute-constrained environment, we might want to distribute the jobs to servers evenly. In a network-constrained environment, we might want to balance according to the bandwidth available to a given server. 

Some applications include: 
- Splitting work to efficiently analyze giant social graphs on Facebook or Twitter
- Redirecting work based on server outages
- Deciding which thread should run next in a multi-threaded program

There are many other applications and there are many places in which it shows up, so it's good to have some knowledge about some basic load balancing schemes. In our load balancing schemes, we want to distribute the workload as evenly as possible. One way we might want to do this is through hashing, which has probabilistic guarantees of uniformity; so why don't we just hash all the work and assign it to some corresponding server? The number of servers we have may change, so the assignment of work has to change whenever the numbers of servers changes, which may incur some cost in terms of maintaining the state stored related to the data. 

## Problem setup
In this lab, you will be implementing basic load balancers for a sharded key-value store (kvstore), mapping keys to shards and keys to the number of times that the key has appeared within the workload, which can be thought of as the number of times that the key has been accessed. Working through the workload, shards will be added and deleted so you'll have to balance the keys in a consistent manner such that you can access them again later. 

### Realism
Is this a realistic problem setup (or is everything just a simulation)? Oftentimes, servers need to be shut down for repairs or updates and then be brought back up, so the work handled by/data residing in those servers need to be redirected to servers that will be alive during the update. Or maybe new servers will be introduced to help further balance the load. Then a mapping to the number of times the key has been accessed may be helpful information for load balancing based on popular keys/shards.

Servers may hold one or more shards at a time, but in our simple example, we'll only work with one shard at a time. In this lab, you are acting as the central manager for the shards, so you can decide what keys belong to which shard and move them around. In reality, clients sending requests to the servers would also need to be able to figure out who to send their information to or have their requests forwarded to them.

# Framework
## Prerequisites
- python3

## Data
The workload will be based on the [dblp collaboration network](https://snap.stanford.edu/data/com-DBLP.html). A simpler sample workload will also be provided for you to test/debug things separately. Each load balancer you write will become increasingly more complex until you eventually implement Consistent Hashing. 

### Generating the workload
1. To download the data, navigate to the Workloads folder, run  
`wget https://snap.stanford.edu/data/bigdata/communities/com-dblp.ungraph.txt.gz` 
2. unzip it, run `gunzip com-dblp.ungraph.txt.gz`. 
3. Then run `python3 generate_workload.py`.

### The Workload
There will be `put`, `create`, and `remove` commands in the workload and they will correspond to the `put`, `add_shard`, and `remove_shard` commands that will be described in more detail in a moment. 

More detail about how the workload is generated can be found in the (Framework Information)[#framework-information] section.

## Testing
To run the testing framework, you'll run something along the lines of `python3 test_framework.py`. This will run all four parts for you to implement and tell you the score you get for each part. There are 4 parts in this lab for you to implement. You can run `python3 test_framework.py -h` to get a list of options you can use. Some parts may rely on the other parts for correctness, e.g. comparisons between the variance in parts 3 and 4 for correctness. We suggest using `-w simple` when debugging and editing the `simple_workload.txt` file. 

More detail about how the framework can be found in the (Framework Information)[#framework-information] section.

## What you'll be implementing
All load balancers are a subclass of LoadBalancer and must implement the following methods:
- `add_shard(shard_name)`: Add a new shard into the system and rebalance accordingly.
- `remove_shard(shard_name)`: Remove a shard from the system and rebalance accordingly.
- `put(key)`: Assigns a specific key to a shard based on some scheme. 

**Note**: `add_shard` and `remove_shard` should first call the parent `add_shard` and `remove_shard` functions. The parent `remove_shard` function returns the keys that the shard held, which you will need to redistribute. You may want to look at LoadBalancer's `add_shard`, `remove_shard`, and the data it keeps track of. 

## Part 0: What if I just put it in one place?
You don't need to load balance if everything's in one place! `LoadBalancers/load_balancer_useless.py` shows how to put things in shards within the framework. This is a not-so-great load balancer because all the work is distributed to the first node. If the server containing this shard dies, then all the information is lost unless someone backed it up (look up State Machine Replication/CSE 452 if interested). Or if there's a lot of traffic, then the latency and throughput might not be so great. This is already implemented for you, so just check it out to see how it works.

## Part 1: Simple Load Balancer
We'll start off simple. We'll take something about the key and balance according to that. A naive way to load balance would be to assign everything based on the first character of the key. If we do this, how would we make sure that the key can be assigned to one of the servers? 

Implement `LoadBalancers/load_balancer_simple.py`. 

**Q1**: What does the distribution look like? 

**Q2**: What might be a problem with this type of load balancing scheme?

## Part 2: The Key is Hashing
We'll fix some of the problems we saw in the previous part. We do this by introducing hashes into the mix. Hash functions take some data and transform it in a pseudorandom manner. There are some bounds and guarantees that come with hashing, but we'll leave that to an algorithms or statistics course. This time, we will hash the key. Hashing will produce a generally uniform distribution of load, but there are some problems with it.

Implement `LoadBalancers/load_balancer_hash_key.py`.

**Q3**: What happened to the keys when you add or remove shards? 

**Q4**: What might be a problem with this load balancing scheme?

## Part 3: Lost in Keyspace
Redistribution comes at a cost, especially when the keys get assigned to the same location. Now, we will try to avoid redistributing keys unnecessarily by introducing the idea of a keyspace or hash ring. The keyspace is the range of possible hash values. In our case, we will let the keyspace be [0, 2^32]. 

We want to make sure that when we add or remove a server, we only redistribute keys that are affected by the change. To do this, you may want to divide up the keyspace to regions controlled by individual servers based on some attribute of the servers somehow. What can you do to divide up the keyspace so that, in expectation, the keyspace is divided evenly among the servers?

The hash function we will be using will be python's hash function but with a mask so that hashes are in the range(0, 2^32), which we call `hash_fn`. 

Implement `LoadBalancers/load_balancer_hash_shard_once.py`.

**Q5**: What might be a problem with this load balancing scheme? 

**Hint 1**: Pay close attention to when the solution wraps around 0. 

**Hint 2**: You might want to look into the bisect library.

## Part 4: Consistent Hashing
You're almost there! What if the way we partitioned the keyspace made it so that the partitions were close together? We'll remedy this by doing what we did for the previous scheme multiple times. We recommend going through the possible cases for dividing the keyspace. 

Implement `LoadBalancers/load_balancer_hash_shard_mult.py`.

**Hint**: Try to simplify the problem into dealing with specific slices. 

**Q6**: If the number of times we hashed to create slices goes towards infinity, what would we expect to see in the distribution of keys among servers? 

**Q7**: What are some potential problems with this load balancing scheme?

## Reflection questions
**Q8**: What are some benefits/drawbacks when increasing the number of times that you hash the server name?

**Q9**: How might you balance the workload on a distribution in which some keys were a lot more popular than other keys?

**Q10**: How might you balance the workload if it was changing over time question? That is, some keys are popular at some times and others at other times.  

## Grading
Since the testing framework is provided to you, we will just download the files related to the load balancers you implement and run them on a clean copy of the testing framework. If you need to implement any helper functions for the labs, either implement them in the load balancer or inside utils.py. 
What we're looking for:
Generally: 
- All keys exist on some shard by the end of the workload. 
- Keys get assigned consistently. 

Then the tests only test the following if the relevant parts are present:

**Part 1 (5pts)**: General cases.

**Part 2 (10pts)**: General cases + Relatively uniform distribution of work\*.

**Part 3 (15pts)**: General cases + Lower number of key movements than Part 2. 

**Part 4 (20pts)**: General cases + Lower number of key movements than Part 2 + lower variance than Part 3. 

**Short Response (30pts total/3pts each)**: Please write your responses in WRITEUP.md, along with your name and UWNetID. Responses are expected to be between 1-3 sentences long. 

Note that these trends may not hold for smaller workloads, since there is generally more variance in smaller workloads than larger ones; so we recommend only using smaller workloads to debug the correctness of your implementation. 

If it doesn't pass the general case, it will be given 0 credit. If it fails additional checks, 50% will be marked off for each thing failed. 

\* = we give a margin of half of the mean.

## Notes
 - It can be assumed that there will always be at least one shard in the system. 
 - Python's `hash(...)` function by default uses a random seed, so you might want to set `export PYTHONHASHSEED=0` when debugging your code. To unset it, just do `unset PYTHONHASHSEED`.
 - We recommend using the `hash_fn` provided instead of python's `hash` function because the number of bits returned by the Python hash function is not consistent. 
 - Feel free to use any standard python3 library.
 - If you're interested in how to load balance according to the distribution of work, consider looking up Slicer or Elastic Load Balancer.
 - There may be some weird issues with getting stuck in `tqdm` in test_framework.py. If that happens, you can replace 
 `for line in tqdm.tqdm(f, total=get_num_lines(workload)):`
 with
 `for line in f:`

---

# Framework information

## Classes

### StateMonitor - Has no direct access to shards, monitors state before and after removes and adds
* Keeps track of states between checks, the number of times that keys have been updated, and the number of times that keys have been moved
* `check_valid` checks for state violations:
  * Make sure that the same key wasn't assigned to different shards
    * Validated by going through each key in a shard and mapping each key to a shard and making sure that each key is only assigned once
  * Make sure that the information stored in the kv pair match what we expect them to be, i.e. counts of the number of times the key has been processed 
    * Validated by keeping an internal count as well to make sure that no information is lost
  * Make sure all keys actually exist on a shard
    * Validated by taking a set difference between known keys and seen keys during the check
* Throws an error if an error comes up and stops the test.
* Keeps track of a history of shard movements, but this may not be very useful to you because we hash things and it's hard to follow hashed values.
* Calculates and outputs the statistics 
  * Statistics include mean, variance, maximum, minimum, and the number of times that keys have been moved

### Shard - Wrapper for a dictionary, but you should really only be calling put
* Contains a name and a key-value store, the name is mostly there to hash server names
* `put` puts the key there and increments the count by the value passed in
* `remove` removes a key and returns a kv pair if it exists
* `get` returns the value if it exists, otherwise returns None

### LoadBalancer - Parent class to be inherited from for other load balancers
* Contains shards
* Contains a function to remove a shard
  * Removing a shard removes the shard and returns the key-value store for that shard, which needs to be redistributed to the remaining shards. Removing a shard may lead to needing to move keys around on the remaining shards.
* Contains a function to add a shard
  * Adding a shard requires redistributing keys
* Contains a function to put keys into the shard
  * Not implemented, but ideally implemented in child classes
* Child classes should call the super method to add/remove shards [already there for you]

## Errors
- `KeyPresentInMultipleShardsError`: At least one key is present in multiple shards
- `ValueLostInTransitionError`: The value maintained by the key is not consistent after an add or remove 
- `KeyLostInTransitionError`: The key is no longer present in any shard after an add or remove

## Workload generation
Currently, we first append 90 `create [server name]` commands, and 9 `remove [server name]` commands, and use the data and make a `put [key]` from the first entry for every line. I'm using random.seed(0). Note that since the data is given in an increasing order of nodes, it didn't really make sense to put everything in that order, so I used random.shuffle() afterwards and then added 10 servers at the start so that puts weren't being put into empty servers. random.shuffle() shuffles 9 removes, 90 creates, and all the put commands. We have to make sure that the servers removed actually exist when we remove them, so we only remove from the first 10 servers that we added to the front for simplicity. 

The low number of `create [server name]` and `remove [server name]` commands makes the somewhat expensive correctness checks for create and remove operations a little bit better. We go through the file and see where they are located so that we can tell if this is a reasonable distribution of work. 

---

# Appendix

## Target audience for the course project 
If the class is being geared towards CSE 3xx students. The population will be mostly sophomores, juniors, and a few seniors who have finished CSE 351 and CSE 332.

## Scope of the project
The project was centered around consistent hashing, so I think the parts build up to it relatively well. Each part built upon the last by at least a little bit. 

## Do we think we met the outcomes we put forth?
- Students should try out different load balancing schemes and observe differences

They will definitely try out different load balancing schemes, but differences may be a little hard to recognize besides the statistics at the end, so it might be better if there was something that could help them see differences in what's happening as time goes on. A visualization of some sort would probably work best.

- Give students intuition for why it's useful/an important problem

Probably not besides the motivation part. "Students often don't know what matters until you tell them." In my experience, students sometimes still have a hard time understanding why something matters even if you tell them why it matters, which I guess motivates the idea of explaining things in a lot of different ways. 

## Is the assignment reasonable?
Yeah, it seems reasonable. It took me around 4-8 hours to finish and I designed/implemented it; which might make it seem a bit long, but I was also tired and editing stuff to make debugging easier along the way, so it's a little hard to guage how long it'll take. I think it'll definitely be doable within a 4-day(ish) period for the target audience while accounting for other classes/homework for a typical student. 

Each of the sections don't ask for too much in terms of implementation. Most parts are a slight extension of the previous part, so it kind of holds their hand through the assignment; which is definitely more reasonable than just being like, "Do consistent hashing! Have fun!". I don't think I explicitly mention what consistent hashing is, so maybe there is some room for improvement in terms of being clear. I do believe it's a reasonable assignment as long as someone has at least explained what consistent hashing is on a high level; since otherwise while motivation/why they're doing something is there, what they're actually supposed to be doing might not be clear.

One could argue that if I tell them too much, it's sort of like hand-holding them through the assignment; or if I tell them too little, it makes the assignment underspecified. So I guess it's a little hard to judge, but if they look up consistent hashing, there's a bunch of good resources. Also, it might be interesting to test out the assignment and see what people think of it in terms of whether it's overspecified or underspecified. 

There may be too many short answer questions. I think 5 is a good number, but it's 10 right now because I have a hard time choosing the best questions. 

## What makes a good assignment?
I think a good assignment is an assignment that leaves the student with the feeling that they've learned something useful and has actually taught the student something useful. They may also feel a sense of pride and accomplishment for completing it, but the main goal is that they finish the assignment with a better understanding of the topic/how it works. Sometimes this means that they should struggle with it for a while and if they aren't able to finish it right away, feel like they are capable of finishing it. 

Familiarizing them with the testing framework or telling them a specific way to do something should not be the goal of the assignment and we should aim to help them develop ideas of how to approach this type of problem. This might mean making the framework simpler/easier to use or leaving things somewhat ambiguous on purpose so that they can determine whether they actually know something or whether they're able to regurgitate something. 

## Was this a good assignment?
Meta-wise, it was an okay course project, but it would've been interesting to do research as well. I can't actually answer if this would make for a good assignment or not because I'd be somewhat biased. I think it is a reasonable assignment and it doesn't fall far from the scope of what people should be capable of after finishing CSE 351 and CSE 332. I think it's actually more straightforward than a lot of the assignments given in CSE 351 or CSE 332. It may have been a bit short, but consistent hashing isn't too complex of a topic, so doing more would sort of drag it out.

## How was the grading determined?
**Part 1**: Pretty much anything should pass.

**Part 2**: Choosing half the mean as the error bound was somewhat arbitrary, but the reasoning is as follows: as the number of keys increased, since the hash should uniformly distribute the keys, the variance should go towards 0, which means that the deviations should get smaller and the probability that any shard holding keys exceeding a difference half the mean should be smaller as well. 

**Part 3**: It just had to have less key movements than part 2, since that's sort of the point of using a keyspace/hash ring.

**Part 4**: It should have lower variance than Part 3 because it uses the same hash function and it's the same workload, so it should achieve lower variance if the key-space was finer-grained. 

## Future work
- Implement everything in Rust and let people do it in either.
- Come up with more/better ways to test correctness or more tests in general.
- Rewrite the README to succinctly describe what Consistent Hashing is. 
- Give this to students and test it out.
- Make it easier to debug the assignment. 
- ~~Finish the slides for the presentation.~~
- ~~Linking of sections in the README.md.~~
- Pictures might be nice.
- Being more concise because currently it's seems like a massive wall of text.
- A visualization tool.

## Conclusion
It was the first time I made an educational project, so I think I'm okay with how it turned out. I accomplished what I set out to do, which was create an educational assignment about consistent hashing. Although I'm not sure I can evaluate the outcomes without actually having seen any outcomes, since no one's done it besides me; but I do believe it to be reasonable.

## Course ideas
### Project ideas
- Implement a small version of Kafka
  - Kafka is used for data processing in a lot of pipelines nowadays and I don't think the publisher/subscriber design patterns is talked about in any classes I've taken.
  - Although doing something like writing a smaller version of Kafka can be applied to pretty much any open-sourced framework and they can see how much work was put into it and get a better understanding of how to use it.
    - They can even benchmark their implementations!
- Quarter-long project that involves building something that simulates a datacenter-hosted application, including networking, queueing, distributing work, setting up APIs, stuff like that.

## Unrelated, but I want to see these things
### Things that would be cool to talk about in a course
- How hashing and different types of hashing are used in systems
  - Hashing applications aren't talked about besides in the context of hash tables or hashmaps in CSE 332, so it might be interesting to see how it's used outside of just those things, like with consistent hashing.
- Teach people how to use Docker/Kubernetes. I know that some course at UWB does that, but my friends told me that they didn't really learn how it worked by the end of it.
- Dissecting technology stacks, so it's sort of about how things are put together, maintained, and upgraded. Maybe something about the lifecycle of software/hardware. 
- How to create packages and stuff for people to use.
- How to read papers and get something out of it. 

### Courses I want to see
- A course that is literally only about implementing open-source software and talking about how they work, with a final project that lets students choose an open-source framework to try to reimplement. 
- A course just about implementing and applying algorithms to build something with a final project that lets students choose what they want to make. 
- A course about using open-source frameworks where every week they try a new framework and finish a small assignment in that framework. Sort of like CSE 391, but with frameworks instead of Linux tools. 
- A CS education course that lets people make educational projects based on some topic they're interested in. It kind of encroaches on the Education space, but CS education seems like it has a slightly different focus than normal education courses.
- A seminar focused on dealing with stress and anxiety in CSE, topics like gender imbalance, how to deal with imposter syndrome, how to tackle problems, and how to learn.
- A seminar for professors to just talk about what they're interested in/their research and it's a different professor every week.

## Acknowledgements 
The sections are based on this [video](https://cs.brown.edu/video/392/?quality=hires) by Doug Woos. 

This was a project for CSE599c: Data Center Systems, offered in Winter 2020. Hi, Tom. 

Contact nowei\[at\]cs.washington.edu if there's any problems.
