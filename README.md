**Load Balancing Algorithms Simulation**

**Author**: Gilad Bitton
**RedID**: 130621085


Overview

This project implements and tests three load balancing strategies:

 - Round Robin
 - Weighted Round Robin
 - Consistent Hashing (with virtual nodes / replicas)

The system simulates routing 10,000+ requests across multiple servers and evaluates:

1. Evenness of distribution
2. Stability during scaling
3. Resilience during failure
4. Effect of replica count on load balance

Project Structure:

LoadBalancer/
├── load_balancer.py
├── server.py
├── consistent_hash.py
├── simulation.py
├── analysis.md
├── README.md
└── tests/
    ├── __init__.py
    └── test_lb.py


File Descriptions:

`server.py`: Defines the Server class with ID, weight, and request counter.

`load_balancer.py`: Implements Round Robin, Weighted Round Robin, and Consistent Hashing strategies.

`consistent_hash.py`: Implements a consistent hashing ring using MD5 and virtual nodes.

`simulation.py`: Runs large-scale simulations to visualize distribution and stability.

`tests/test_lb.py`: Contains 21 unit tests covering correctness, stability, distribution, and edge cases.

`analysis.md`: Explains resilience, stability, and replica behavior.

How to Run
1. Run Unit Tests
    - python3 -m unittest discover tests
    - Expected output:
        Ran 21 tests in <time>
        OK

2. Run Simulation
    - python3 simulation.py
    - This runs:
        - Round Robin simulation
        - Weighted Round Robin simulation
        - Consistent Hashing simulation
        - Replica comparison test
        - Resilience test


Implemented Strategies:

**Round Robin**:
Cycles through servers sequentially.
Ensures perfectly even distribution when servers have equal capacity.

**Weighted Round Robin**:
Distributes requests proportionally based on server weight.
Example:
    Weight 3 server → 3/(N total weights) traffic
    Weight 1 server → 1/(N total weights) traffic

**Consistent Hashing**:
Uses MD5 hashing
Uses virtual nodes (replicas)
Minimizes key movement during scaling
Provides resilience to server removal


Technical Requirements:
 - Python 3.12+
 - Standard library only (hashlib, bisect, unittest, etc.)
 - No external dependencies

Results Summary:
 - All 21 unit tests pass.
 - Replica count significantly improves load balance.
 - Server addition/removal preserves majority of key mappings.
 - Consistent hashing minimizes data movement compared to modulo hashing.

