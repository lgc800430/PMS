__author__ = 'MTK07896'

import sys
import os
import re
import optparse
import operator
import inspect
import math
import random
from datetime import datetime



from Cache import *
from VLC import *
from PCTracer import *
from Simulator import *
from GlobalVar import GlobalVar


class Port:

  def __init__(self):
    self.port_name         = ""

    # self.port_ptr             = None
    self.port_belong_node_ptr = None
    self.port_belong_bus_ptr  = None
    
    self.port_NB_trans  = [] #Node to BUS list
    self.port_BN_trans  = [] #BUS to Node list

  ### target = node_higher_bus, node_lower_bus  ###
  def construct(self, root, target):
    # if(target == "node_higher_bus" and not root.attrib["node_higher_bus"] == "None"):
    name_in_port = root.attrib["name"] + "_" + root.attrib[target]
    node_in_port = root.attrib["name"]
    bus_in_port  = root.attrib[target]

    link_node = GlobalVar.topology_ptr.node_dist[node_in_port]
    link_bus  = GlobalVar.topology_ptr.bus_dist[bus_in_port]

    self.port_name            = name_in_port
    self.port_belong_node_ptr = link_node
    self.port_belong_bus_ptr  = link_bus

    link_node.node_port_dist[name_in_port] = self
    link_bus.bus_port_dist[name_in_port]   = self
    return name_in_port
    # elif(target == "node_lower_bus" and not root.attrib["node_lower_bus"] == "None"):
      # name_in_port = root.attrib["name"] + "_" + root.attrib["node_lower_bus"]
      # node_in_port = root.attrib["name"]
      # bus_in_port  = root.attrib["node_lower_bus"]

      # link_node = GlobalVar.topology_ptr.node_dist[node_in_port]
      # link_bus  = GlobalVar.topology_ptr.bus_dist[bus_in_port]

      # self.port_name            = name_in_port
      # self.port_belong_node_ptr = link_node
      # self.port_belong_bus_ptr  = link_bus

      # link_node.node_port_dist[name_in_port] = self
      # link_bus.bus_port_dist[name_in_port]   = self
      # return name_in_port
    
    
    
    
    