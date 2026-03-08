**Author: Gilad Bitton**
**RedID: 130621085**

**Topic 1: Resilience - What happens when a server is removed?**

When a server is removed in consistent hashing, the only keys that would be affected are the ones mapped to the now gone server. 
The server's replica points are also removed from the ring, and the keys corresponding get reassigned to the next clockwise server.

From my simulation:

--- Resilience Test (Consistent Hashing) ---
1. User-Special-1 assigned to S1
Removing S1...
2. User-Special-1 assigned to S3
SUCCESS: Traffic rerouted correctly.

This is validated in `test_ch_resilience_and_stability`.

This shows:
 - The removed server receives no traffic.
 - Requests get automatically rerouted.
 - unaffected keys stay on the same server

 Unlike modulo hashing (hash(key) % N), which would remap most keys since N (the number of servers) changes.
 Consistent hashing minimizes movement by not having the hashing function depend on N.
 Thus, resulting in only keys who's node got removed to be rehashed upon removal,
preserving stability in a dynamic environment.


 **Topic 2: Stability - What happens when a server is added?**

When a new server is added, only the keys who now have their next closest node ahead be the new server move.
All other keys remain with the same server.

This is validated in `test_ch_stability_on_add`, which measures stability,
aka what percentage of keys remain mapped to the same server after adding a new one.
The test pass due to the retention rate exceeding the required 50%.

Theoretically, adding 1 server to 5 (assuming perfect distribution)
should move about 1/(N+1) = 1/6 = 16-17% of keys.
This means that ~83% should remain unchanged.
The 50% threshold is a generous threshold to pass in comparison.

How close that retention rate is to 83% entirely depends on how well distributed the nodes are.
The higher the amount of replicas, the more likely it is to be well distributed. 

With **3 replicas/server**, arc sizes can be uneven and retention rate slightly lower than 83%.
However, with something like **100 replicas/server**, arc sizes become much more uniform 
and the captured portion should be much closer to the theoretical 1/6.
Making retention more consistent and closer to ~83%.

**Topic 3: Replica Distribution - How do virtual nodes affect load balance?**

Virtual nodes (replicas) improve the load balance by spreading each server across multiple points in the ring.
This makes it so if all the servers are hashed next to each other, balance would still be maintained with sufficient replicas.

From simulation results:

--- Replica Count Comparison (Consistent Hashing) ---
Routing 10000 requests to 5 servers at different replica counts

  Replicas=  1  |  Std Dev:  1795.5  |  S0: 5.9%, S1: 4.1%, S2: 48.1%, S3: 34.5%, S4: 7.4%
  Replicas=  3  |  Std Dev:  1224.4  |  S0: 8.2%, S1: 33.0%, S2: 12.7%, S3: 36.6%, S4: 9.4%
  Replicas= 50  |  Std Dev:   534.1  |  S0: 17.9%, S1: 27.8%, S2: 24.7%, S3: 13.7%, S4: 16.0%
  Replicas=150  |  Std Dev:   117.2  |  S0: 19.9%, S1: 18.9%, S2: 21.9%, S3: 20.5%, S4: 18.8%

With few replicas, some servers own large hash arcs and receive disproportionate traffic.
Causing massive differences in percentages and a high standard deviation. 
Increasing the number of replicas causes a more even distribution, more even arc sizes, and a lower standard deviation.
With 5 servers, the higher the replicas the closer each load should be to 20%.

This is validated in:

 - `test_ch_distribution`
 - `test_replicas_improve_distributions`

In conclusion:
More replicas → smaller arc imbalance → lower standard deviation → better load balance.