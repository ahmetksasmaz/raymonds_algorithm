"""
Distributed Computing Systems Mutual Exclusion Algorithms

This module implements Raymond's Algorithm
"""

from enum import Enum
from time import sleep
import random
import queue
import networkx as nx

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import *

class RaymondMessageTypes(Enum):
    """
    Raymond's Algorithm has only two message types.
    One of them is request: it is sent when a node requests for privilege.
    Another of them is token: it is sent when privilege is forwarded to other node.
    """
    REQUEST = "REQUEST"
    TOKEN = "TOKEN"

class RaymondEventTypes(Enum):
    """
    Raymond's Algorithm has four event types.
    First one of them is want privilege: the event is triggered when a node wants to use critical section.
    Second one of them is release privilege: the event is triggered when a node is done with the critical section.
    Third one of them is get request: the event is triggered when a node receives a request message. (see RaymondMessageTypes)
    Fourth one of them is get token: the event is triggered when a node receives a token message. (see RaymondMessageTypes)
    """
    WANT_PRIVILEGE = "WANT_PRIVILEGE"
    RELEASE_PRIVILEGE = "RELEASE_PRIVILEGE"
    GET_REQUEST = "GET_REQUEST"
    GET_TOKEN = "GET_TOKEN"

class RaymondComponentModel(GenericModel):
    """
    This is a class for component represents a node running in a distributed environment that uses Raymond's algorithm to privilege critical section.
    """
    def __init__(self, component_name, component_instance_number, context=None, configuration_parameters=None, num_worker_threads=1, topology=None):
        """
        This is a constructor of the class. It defines the events (see RaymondEventTypes), sets algorithm based member variables, initializes metrics for experiments.
        """
        super().__init__(component_name, component_instance_number, context, configuration_parameters, num_worker_threads, topology)

        self.eventhandlers[RaymondEventTypes.WANT_PRIVILEGE] = self.on_want_privilege
        self.eventhandlers[RaymondEventTypes.RELEASE_PRIVILEGE] = self.on_release_privilege
        self.eventhandlers[RaymondEventTypes.GET_REQUEST] = self.on_get_request
        self.eventhandlers[RaymondEventTypes.GET_TOKEN] = self.on_get_token

        minimum_spanning_tree = nx.minimum_spanning_tree(self.topology.G)
        self.parent_id = None
        if self.componentinstancenumber != 0:
            self.parent_id = nx.shortest_path(minimum_spanning_tree, self.componentinstancenumber, 0)[1]
        self.privilege_queue = queue.Queue()
        self.using_critical_section = False
        self.has_privilege = False
        self.want_privilege = False

        # Metrics for experiments
        self.experiment_sleep_scaler = 1.0
        self.total_want_privilege = 0
        self.total_used_critical_section = 0
        self.total_released_critical_section = 0
        self.total_request_message_received = 0
        self.total_token_message_received = 0
        self.total_request_message_sent = 0
        self.total_token_message_sent = 0

    def on_init(self, eventobj: Event):
        """
        This function is called when init event is triggered.
        Only root(#0) node is affected from this function.
        Algorithm ensures that the privilege is owned by root initially.
        """
        # For root
        if self.componentinstancenumber == 0:
            self.has_privilege = True

    def on_message_from_bottom(self, eventobj: Event):
        """
        This function is called when message is received from bottom.
        Then proper Raymond Event is triggered according to message type.
        """
        header = eventobj.eventcontent.header
        if header.messageto == self.componentinstancenumber:
            if header.messagetype == RaymondMessageTypes.REQUEST:
                eventobj.event = RaymondEventTypes.GET_REQUEST
            elif header.messagetype == RaymondMessageTypes.TOKEN:
                eventobj.event = RaymondEventTypes.GET_TOKEN
            self.send_self(eventobj)

    def on_want_privilege(self, eventobj: Event):
        """
        This function is called when self node wants privilege to use critical section.
        If the self node has already requested for privilege, nothing happens.
        If the self node is currently using critical section, nothing happens.
        Otherwise it is time to request for privilege.
        If we have the privilege (but not using), then we can use it.
        If we don't have the privilege, we should ask it.
        If there are others waiting for the privilege, we just add ourselves to queue and wait.
        If there aren't any other node waiting for the privilege, we request token from our parent for ourselves.
        """
        if self.want_privilege == False: # Prevent duplicate request
            if self.using_critical_section == False: # Prevent on use request
                self.total_want_privilege += 1
                if self.has_privilege == True: # We already have the token, then use it
                    self.using_critical_section = True
                    self.use_critical_section()
                else: # We don't have the token
                    self.want_privilege = True
                    if self.privilege_queue.empty(): # Request token if no one is waiting for it
                        self.privilege_queue.put(self.componentinstancenumber)
                        self.send_down(Event(self, EventTypes.MFRT, self.create_message(RaymondMessageTypes.REQUEST)))
                        self.total_request_message_sent += 1
                    else: # Put yourself into the request queue
                        self.privilege_queue.put(self.componentinstancenumber)

    def on_release_privilege(self, eventobj: Event):
        """
        This function is called when self node is done with the critical section.
        We release the privilege, if there are some nodes that requests privilege in our queue,
        we forward the token to the first one. If still there are others waiting for the privilege, we request the token
        from our new parent.
        """
        self.total_released_critical_section += 1
        self.using_critical_section = False # End using critical section
        self.want_privilege = False
        if not self.privilege_queue.empty(): # If there are others waiting for token
            element = self.privilege_queue.get()
            self.parent_id = element
            self.has_privilege = False
            self.send_down(Event(self, EventTypes.MFRT, self.create_message(RaymondMessageTypes.TOKEN)))
            self.total_token_message_sent += 1
            if not self.privilege_queue.empty(): # Still there are nodes in queue, request token for them
                self.send_down(Event(self, EventTypes.MFRT, self.create_message(RaymondMessageTypes.REQUEST)))
                self.total_request_message_sent += 1

    def on_get_request(self, eventobj: Event):
        """
        This function is called when self node receives a request. If we have the privilege and currently using critical section
        we simply push the new one into the queue. Otherwise, if we have the token then we pass it to our new parent and
        if there are any other waiting for privilege in the queue, we request the privilege from our new parent for them.
        If we don't have the token, if there is no other node in the queue, we request token from our parent. If there are nodes waiting,
        then just push into the queue.
        """
        self.total_request_message_received += 1
        node_id = eventobj.eventcontent.header.messagefrom
        if self.using_critical_section == False: # If we are not using the token
            if self.has_privilege == True: # If we have the token then give it
                self.parent_id = node_id
                self.has_privilege = False
                self.send_down(Event(self, EventTypes.MFRT, self.create_message(RaymondMessageTypes.TOKEN)))
                self.total_token_message_sent += 1
                if not self.privilege_queue.empty(): # Still there are nodes in queue, request token for them
                    self.send_down(Event(self, EventTypes.MFRT, self.create_message(RaymondMessageTypes.REQUEST)))
                    self.total_request_message_sent += 1
            else: # We don't have the token
                if self.privilege_queue.empty(): # There are no other requester, so request it from parent
                    self.privilege_queue.put(node_id)
                    self.send_down(Event(self, EventTypes.MFRT, self.create_message(RaymondMessageTypes.REQUEST)))
                    self.total_request_message_sent += 1
                else: # There are other requesters before this, a request has already been sent before
                    self.privilege_queue.put(node_id)
        else: # If we have the token and using critical section
            self.privilege_queue.put(node_id)
    
    def on_get_token(self, eventobj:Event):
        """
        This function is called when self node receives token message.
        We get the first node from the queue. If it is us, we use it. If not, we pass the token to it,
        and finally if still there is nodes in the queue, we request token again for them.
        """
        self.total_token_message_received += 1
        element = self.privilege_queue.get()
        if element == self.componentinstancenumber: # The waiting one is nobody but us
            self.has_privilege = True
            self.using_critical_section = True
            self.use_critical_section()
        else: # Other one is waiting, forward token to it
            self.parent_id = element
            self.send_down(Event(self, EventTypes.MFRT, self.create_message(RaymondMessageTypes.TOKEN)))
            self.total_token_message_sent += 1
            if not self.privilege_queue.empty(): # Still there are nodes in queue, request token for them
                self.send_down(Event(self, EventTypes.MFRT, self.create_message(RaymondMessageTypes.REQUEST)))
                self.total_request_message_sent += 1

    # External trigger functions
    def trigger_privilege(self):
        print("ME : [",self.componentinstancenumber,"] triggered for privilege")
        self.send_self(Event(self, RaymondEventTypes.WANT_PRIVILEGE, None)) # Trigger want privilege

    # Helper functions
    def create_message(self, message_type):
        """
        This function is a helper function for creating messages.
        """
        header = None
        payload = GenericMessagePayload("")
        next_hop = self.parent_id
        interface_id = f"{self.componentinstancenumber}-{next_hop}"
        header = GenericMessageHeader(message_type, self.componentinstancenumber, self.parent_id, next_hop, interface_id)
        return GenericMessage(header, payload)
    
    def use_critical_section(self):
        """
        This function is a dummy function for simulate using critical section.
        At the end of the sleep, it triggers release privilege event.
        """
        sleep(random.randint(1,3) * self.experiment_sleep_scaler) # Sleep for 1-3 seconds (multiplied by scaler to make faster experiments)
        self.total_used_critical_section += 1
        self.send_self(Event(self, RaymondEventTypes.RELEASE_PRIVILEGE, None)) # Trigger releasing privilege
    
    def set_sleep_scaler(self, scale):
        """
        This function is a setter for sleep scaler for easier experiments.
        """
        self.experiment_sleep_scaler = scale