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


Q4: What might be a problem with this load balancing scheme?


## Part 3: Lost in Key-Space
Q5: What might be a problem with this load balancing scheme? 


## Part 4: Consistent Hashing
Q6: If the number of times we hashed to create slices goes towards infinity, what would we expect to see in the distribution of keys among servers? 


Q7: What are some potential problems with this load balancing scheme?


## Reflection
Q8: What are some benefits/drawbacks when increasing the number of times that you hash the server name or consistent hashing in general? 


Q9: How might you balance the workload on a distribution in which some keys were a lot more popular than other keys?


Q10: How might you balance the workload if it was changing over time question? That is, some keys are popular at some times and others at other times. 

