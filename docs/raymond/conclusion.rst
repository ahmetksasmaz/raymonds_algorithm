.. include:: substitutions.rst

Conclusion
==========

In summary, the algorithm efficiently manages message transmission in the topology, with message volume typically approximating logK(N). Each node can store up to K requests, optimizing message and memory usage. However, node failures can disrupt privilege distribution, impacting nodes below the failed one. Particularly, if the root node fails, only nodes within its branch retain privileges. Moreover, larger K values increase the number of affected nodes during failures, while decreasing K enlarges the average message count per privilege request due to increased node distance.