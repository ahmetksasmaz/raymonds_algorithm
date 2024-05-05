"""
Distributed Computing Systems Mutual Exclusion Algorithms

This module implements tester for Raymond's Algorithm
"""

# AHC Library
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, ConnectorTypes
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

# Graph
import networkx as nx
import random

# Time
import math
import time

# System Library
import sys
import argparse
sys.path.append('../') # Necessary for importing parent directory

# Distributed Algorithm
from Raymond.Raymond import RaymondComponentModel

# Poisson event generator
def next_poisson_event(rate_parameter):
    """
    This helper function is for creating an event at particular timestamp that is distributed with respect to Poisson distribution.
    """
    return -math.log(1.0 - random.random()) / rate_parameter

def create_kary_tree_topology(n, min_child, max_child):
    """
    Due to Raymond's Algorithm works on a K-ary tree, this function creates a topology for k-ary tree.
    It takes node count, minimum child count for every node and maximum child for every node.
    If min_child == max_child == 2, then the tree is a binary tree.
    If min_child == max_child == 1, then the tree is a linked list.
    """
    G = nx.empty_graph(n-1)
    total_number_of_left_node = n-1
    latest_node = 0
    not_completed_nodes = [0]
    while len(not_completed_nodes) > 0:
        current_node = not_completed_nodes.pop(0)
        if total_number_of_left_node == 0:
            break
        elif total_number_of_left_node <= min_child:
            min_child = total_number_of_left_node
            max_child = total_number_of_left_node
        elif total_number_of_left_node <= max_child:
            max_child = total_number_of_left_node
        child_number = random.randint(min_child, max_child)
        for x in range(child_number):
            latest_node += 1
            G.add_edge(current_node, latest_node)
            not_completed_nodes.append(latest_node)
        total_number_of_left_node -= child_number
    return G

topology = Topology()

def main():
    """
    This is the main function for testing.
    It parses parameters from command line. The parameters are:
    -n --node: Total number of nodes in the test
    -m --min-child: Minimum child number that a node must have [at least 1, at most node-1]
    -M --max-child: Maximum child number that a node can have [at least min-child]
    -p --privilege: Number of privilege request for random node in a test
    -r --rate: Poisson rate to generate privilege trigger for random node
    -s --scale: Using critical section time scale, multiplied by a random integer between [1,3]

    It creates and starts the topology.
    It creates an privilege request event in time w.r.t. Poisson distribution.
    Then, it waits for all nodes to stop wanting the privilege.
    Finally prints the result.
    """
    parser = argparse.ArgumentParser(description='Raymond\'s Algorithm Tester')
    parser.add_argument('-n','--node', help='Total number of nodes in the test', required=True, type=int)
    parser.add_argument('-m','--min-child', help='Minimum child number that a node must have [at least 1, at most node-1]', required=True, type=int)
    parser.add_argument('-M','--max-child', help='Maximum child number that a node can have [at least min-child]', required=True, type=int)
    parser.add_argument('-p','--privilege', help='Number of privilege request for random node in a test', required=True, type=int)
    parser.add_argument('-r','--rate', help='Poisson rate to generate privilege trigger for random node', required=True, type=int)
    parser.add_argument('-s','--scale', help='Using critical section time scale', required=True, type=float)
    args = vars(parser.parse_args())

    if args["min_child"] < 1:
        print("Minimum number of child must be at least 1.")
        return 
    if args["max_child"] < args["min_child"]:
        print("Maximum number of child must be at least minimum number of child.")
        return 
    if args["node"] - 1 < args["min_child"]:
        print("Minimum number of child cannot be greater then total number of node - 1.")
        return 

    G = create_kary_tree_topology(args["node"], args["min_child"], args["max_child"])

    topology.construct_from_graph(G, RaymondComponentModel, GenericChannel)

    for x in range(args["node"]):
        topology.nodes[x].set_sleep_scaler(args["scale"])

    topology.start()

    for x in range(args["privilege"]):
        time.sleep(next_poisson_event(args["rate"]))
        random_node = random.randint(0, args["node"]-1)
        print("Node[",random_node,"] triggered for privilege.")
        topology.nodes[random_node].trigger_privilege()

    still_working = True
    while still_working:
        time.sleep(1)
        still_working = False
        print("####################")
        for x in range(args["node"]):
            if topology.nodes[x].want_privilege == True:
                still_working = True
                print("# Node[",x,"] : ",
                list(topology.nodes[x].privilege_queue.queue), " - ",
                topology.nodes[x].using_critical_section, " - ",
                topology.nodes[x].has_privilege, " - ",
                topology.nodes[x].want_privilege)
                # break
    
    topology.exit()

    # Collect and print data
    total_want_privilege = 0
    total_duplicate_want_privilege = 0
    total_used_critical_section = 0
    total_released_critical_section = 0
    total_request_message_received = 0
    total_token_message_received = 0
    total_request_message_sent = 0
    total_token_message_sent = 0
    for x in range(args["node"]):
        total_want_privilege += topology.nodes[x].total_want_privilege
        total_duplicate_want_privilege += topology.nodes[x].total_duplicate_want_privilege
        total_used_critical_section += topology.nodes[x].total_used_critical_section
        total_released_critical_section += topology.nodes[x].total_released_critical_section
        total_request_message_received += topology.nodes[x].total_request_message_received
        total_token_message_received += topology.nodes[x].total_token_message_received
        total_request_message_sent += topology.nodes[x].total_request_message_sent
        total_token_message_sent += topology.nodes[x].total_token_message_sent

    print("total_want_privilege : ", total_want_privilege)
    print("total_duplicate_want_privilege : ", total_duplicate_want_privilege)
    print("total_used_critical_section : ", total_used_critical_section)
    print("total_released_critical_section : ", total_released_critical_section)
    print("total_request_message_received : ", total_request_message_received)
    print("total_token_message_received : ", total_token_message_received)
    print("total_request_message_sent : ", total_request_message_sent)
    print("total_token_message_sent : ", total_token_message_sent)

if __name__ == "__main__":
    main()