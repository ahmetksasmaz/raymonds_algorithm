.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To implement the algorithm, we utilized an event-driven node from the adhoccomputing library. These nodes operate with an internal event queue.

Communication between nodes occurs via channels, which essentially represent the connections between them.

The algorithm comprises four main types of events:

1. Requesting privilege
2. Releasing privilege
3. Sending request messages
4. Sending reply messages

For a deeper understanding and formal declarations regarding the algorithm, refer to the documentation.

To evaluate the algorithm, we first establish an appropriate network topology. For Raymond's algorithm, a K-ary tree structure is utilized.

Constructing a K-ary topology involves determining the number of nodes and the minimum and maximum number of children for each node.

Starting from the root, nodes are added with a random count of children within the specified range.

Ultimately, our randomized K-ary tree, adhering to the given constraints, is ready for use.

Key Notes:

1. When both the minimum and maximum number of nodes are set to 1, the topology behaves like a linked list.

2. Setting both values to 2 results in a binary tree-like behavior.

After setting up the topology, all nodes are activated.

Subsequently, randomly selected nodes initiate requests for privilege, with timing following a Poisson distribution.

The testing process waits for all nodes to no longer require privilege.

Finally, data from all nodes is collected and analyzed to derive benchmark results, including:

1. Total privilege requests
2. Instances of duplicated privilege requests
3. Total critical section usage
4. Total critical section releases
5. Count of received request messages
6. Count of received token messages
7. Count of sent request messages
8. Count of sent token messages

The correlation between the total privilege requests and the combined count of request and token messages indicates the message complexity.

Furthermore, the relationship between total privilege requests and total critical section releases serves as practical evidence of absence of starvation and fairness within the system.

Results
~~~~~~~~

Present your AHCv2 run results, plot figures.


This is probably the most variable part of any research paper, and depends upon the results and aims of the experiment. For quantitative research, it is a presentation of the numerical results and data, whereas for qualitative research it should be a broader discussion of trends, without going into too much detail. For research generating a lot of results, then it is better to include tables or graphs of the analyzed data and leave the raw data in the appendix, so that a researcher can follow up and check your calculations. A commentary is essential to linking the results together, rather than displaying isolated and unconnected charts, figures and findings. It can be quite difficulty to find a good balance between the results and the discussion section, because some findings, especially in a quantitative or descriptive experiment, will fall into a grey area. As long as you not repeat yourself to often, then there should be no major problem. It is best to try to find a middle course, where you give a general overview of the data and then expand upon it in the discussion - you should try to keep your own opinions and interpretations out of the results section, saving that for the discussion [Shuttleworth2016]_.


.. .. image:: figures/CDFInterferecePowerFromKthNode2.png
..   :width: 400
..   :alt: Impact of interference power


.. list-table:: Title
   :widths: 25 25 50
   :header-rows: 1

   * - Heading row 1, column 1
     - Heading row 1, column 2
     - Heading row 1, column 3
   * - Row 1, column 1
     -
     - Row 1, column 3
   * - Row 2, column 1
     - Row 2, column 2
     - Row 2, column 3

Discussion
~~~~~~~~~~

Present and discuss main learning points.




.. [Shuttleworth2016] M. Shuttleworth. (2016) Writing methodology. `Online <https://explorable.com/writing-methodology>`_.