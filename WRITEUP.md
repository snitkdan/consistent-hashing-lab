# Short response
Name: Daniel Snitkovskiy

UWNetID: snitkdan

## Part 1: Simple Load Balancer
Q1: What does the distribution look like? 

> Moved >90% of the keys >5 million times (when I ran the test last). There is a high variance in key movement (~81 million), but with a mean of ~2,000. This looks like on average, not many keys were moved, but
volatility based on the workload was substantial, making this not a 
very stable load balancer. 

Q2: What might be a problem with this type of load balancing scheme?

> One problem with this scheme is that some starting letters are more common than others (depending on the language of the key of-course). 
This will make certain keys more popular than others just based on
the first letter, which could leave servers assigned to common
key prefixes overwhelmed. 


## Part 2: The Key is Hashing
Q3: What happened to the keys when you add or remove shards? 

> Conceptually, the same thing that happened in the previous part: you have to go through each of the shards and possibly move the key to a new shard because the shard assigned to a key is affected by the number of shards (in this case `hash(key) % num_shards` rather than `ord(key[0]) % num_shards`). In this case however, there was a lot less movement because the uniform hashing eliminated some of the skew associated with super common first letters of keys in the previous part (the variance in key movement went down to ~2,000).


Q4: What might be a problem with this load balancing scheme?

> There still might be a lot of cost associated with adding/removing shards, because even if there are evenly distributed keys, adding/removing a key will involve talking with possibly all of the other shards, which could incur network costs if there would be coordination involved. 

## Part 3: Lost in Key-Space
Q5: What might be a problem with this load balancing scheme? 

> There is a chance that we might hash some servers into much wider ranges than others, thereby not spreading the load evenly amongst servers per key-space slice. 

## Part 4: Consistent Hashing
Q6: If the number of times we hashed to create slices goes towards infinity, what would we expect to see in the distribution of keys among servers? 

> The keys would become close to uniform like in the regular hashing. 

Q7: What are some potential problems with this load balancing scheme?

> The problems are of balance: too few rounds of hashing, and you end up with Part3 problems of having uneven key-space slices; too many slices, and you having
potentially a lot of key movement if one server is added/removed. This approach is less one-size-fits-all, and needs careful tuning in order to 
get to a state with acceptable key movement traffic and relatively even key-space distribution. 

## Reflection
Q8: What are some benefits/drawbacks when increasing the number of times that you hash the server name or consistent hashing in general? 

> See discussion in Q7. 

Q9: How might you balance the workload on a distribution in which some keys were a lot more popular than other keys?

> You could assign a "replication factor" to popular keys, so that instead of 1 shard, they get a collection of shards that they may reside on. All those 
shards replicate puts linearizably so that the copied are in sync. When a client request comes in, it'll be routed to an arbitrary shard within this collection
(perhaps `collection[hash(clientId) % num_shards_in_collection]`), which will allow the workload for that key to scale by the number of replicas. 

Q10: How might you balance the workload if it was changing over time question? That is, some keys are popular at some times and others at other times. 

> You could keep track of access frequency of certain keys, and attach to them some replication factor if they're accessed frequently enough. For example, say we have `despacito`, and it gets really popular within the span of some timeout (e.g. 5 mins). After that timeout, we decide to replicate `despacito` across
K servers (K depending on the load), and have an inbound client request pick the server with the least load at that time. (The big question then becomes how to
measure load, and maybe that could be approximated using the RTT of a diagnostic Ping). Table Indirection is a popular algorithm to achieve this as well. 

# Part 5: Skewed Workload

## Reflection
TODO: add this in