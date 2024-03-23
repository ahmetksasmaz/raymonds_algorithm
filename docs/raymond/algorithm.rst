.. include:: substitutions.rst

|DistAlgName|
=========================================

Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In distributed systems, mutual exclusion is crucial for preventing race conditions, ensuring that only one process can access a critical section at any given time. Unlike single computer systems where shared variables can facilitate mutual exclusion, distributed systems lack shared memory and a common clock, necessitating different solutions.

Requirements for a mutual exclusion algorithm in distributed systems include:

    1. **No Deadlock:** Ensure processes don't indefinitely wait for messages.
    2. **No Starvation:** Every process should have a chance to execute its critical section in finite time.
    3. **Fairness:** Requests to execute critical sections should be executed in the order they arrive.
    4. **Fault Tolerance:** The system should recognize failures and continue functioning without disruption.

Solutions include:

    1. **Token Based Algorithm:** Uses a unique token shared among sites, allowing possession of the token to enter the critical section. Examples include the Suzuki-Kasami Algorithm [SuzukiKasamiAlgorithm]_ and Raymond's Algorithm [RaymondsAlgorithm]_ explained in this document.
    2. **Non-token based approach:** Sites communicate to determine which should execute the critical section next, using timestamps to order requests. Examples include the Ricart-Agrawala Algorithm [RicartAgrawalaAlgorithm]_.
    3. **Quorum based approach:** Sites request permission from a subset called a quorum, ensuring mutual exclusion through common subsets. Examples include Maekawa’s Algorithm [MaekawasAlgorithm]_.

These approaches address the challenges of distributed systems, ensuring safe and efficient access to critical sections while meeting system requirements.

Distributed Algorithm: |DistAlgName| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Raymond's Algorithm:**

    .. code-block:: RST
        :linenos:
        :caption: Raymond's Algorithm [RaymondsAlgorithm]_.
        
        integer list channels, list of ids of connected channels to self node
        integer parent_index, element index that represents parent channel in channels
        integer queue fifo_queue, internal fifo queue that orders token requests
        bool using_critical_section, a boolean represents whether node is using critical section or not
        bool has_token, a boolean represents whether node has privilege to use critical section

        If p wants to use critical section
            if using_critical_section = false then
                if has_token = true then
                    using_critical_section ← true;
                else then
                    if fifo_queue is empty then
                        send request message into the channel channels[parent_index];
                    end if
                    push ⟨-1⟩ into fifo_queue;
                end if
            end if

        If p ends using critical section
            using_critical_section ← false;
            if fifo_queue is not empty then
                pop from fifo_queue into ⟨i⟩
                parent_index ← find_index(channels, i);
                send token message into the channel channels[parent_index];
            end if

        If p receives a request message through a channel i
            if using_critical_section = false then
                if has_token = true then
                    parent_index ← find_index(channels, i);
                    send token message into the channel channels[parent_index];
                else then
                    if fifo_queue is empty then
                        send request message into the channel channels[parent_index];
                    end if
                    push ⟨i⟩ into fifo_queue;
                end if
            else then
                push ⟨i⟩ into fifo_queue;
            end if
        
        If p receives a token message through a channel i
            pop from fifo_queue into ⟨j⟩
            if j = -1 then
                has_token ← true;
                using_critical_section ← true;
            else then
                parent_index ← find_index(channels, j);
                send token message into the channel channels[parent_index];
                if fifo_queue is not empty then
                    send request message into the channel channels[parent_index];
                end if
            end if

Lines[41-51] describes what happens when self node wants to use critical section. If the self node is already using the critical section, nothing happens. If not, then token ownership is checked. If the self node has token, it can use critical section without any problem. If the self node doesn't have token, then pushes itself to the internal fifo queue and send request to parent if the only requester is itself. There is no need to send request if there are previous requesters because a request have already sent, it guarantees that token will pass through self node.

Lines[53-59] describes what happens when self node has privilege and using critical section and finishes its job. When the job is done, if there are waiting nodes in queue, then send the token the first one and set it as parent.

Lines[61-73] describes what happens when self node receives a request message from a connected channel. If we have the token and currently using critical section, then we just add the requester to the queue. The token will eventually have sent to that node. If we have the token but not using it. Then we can just pass to requester channel. If we don't have token, then we should add it to the queue to forward token when time comes. If our fifo queue is empty. Then we should send a request to notify our parent about that we need the token. If we have elements in our queue, that means a request has already sent before, and it guarantees that the token will eventually pass through self node.

Lines[76-87] describes what happens when self node receives a token message from a connected channel. If we get the token message, then that means we have unsatisfied requests in our queue. We pop the first element. If the first element is the self node itself, we can take the token and start using critical section. If the first one is not the self node we should forward the token to the requester. We send the token and set the requester as parent. After then, if we don't send a request again to our new parent, the token will never come back because our parent doesn't have current node in its queue. That means our node and its children will not be able to use critical section anymore. In order to prevent this, we send a request.

**Example**
~~~~~~~~

.. image:: figures/RaymondAlgorithmExample1.png
  :width: 600
  :alt: Raymond's Algorithm Example 1

.. image:: figures/RaymondAlgorithmExample2.png
  :width: 750
  :alt: Raymond's Algorithm Example 2

**Correctness**
~~~~~~~~~~~

Present Correctness, safety, liveness and fairness proofs.

**Complexity **
~~~~~~~~~~

1. **Memory Complexity:** Raymond's algorithm ensures that each critical section entry takes O(log n) time when processors are arranged in a K-ary tree, and each processor only needs to store O(log n) bits to track its O(1) neighbors.
2. **Message Complexity:** In the worst scenario, the algorithm needs twice the length of the longest path in the tree for each critical section entry, which is N-1 for nodes arranged in a line, totaling 2*(N-1) message invocations. Yet, if all nodes generate an equal number of request messages, it will require roughly 2*N/3 messages per critical section entry.

.. [SuzukiKasamiAlgorithm] Gerard Tel, Introduction to Distributed Algorithms, CAMBRIDGE UNIVERSITY PRESS, 2001
.. [RaymondsAlgorithm] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [RicartAgrawalaAlgorithm] Leslie Lamport, K. Mani Chandy: Distributed Snapshots: Determining Global States of a Distributed System. In: ACM Transactions on Computer Systems 3. Nr. 1, Februar 1985.
.. [MaekawasAlgorithm] Leslie Lamport, K. Mani Chandy: Distributed Snapshots: Determining Global States of a Distributed System. In: ACM Transactions on Computer Systems 3. Nr. 1, Februar 1985.