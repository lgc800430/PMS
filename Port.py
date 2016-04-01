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
    
    self.port_NB_list  = [] #Node to BUS list
    self.port_BN_list  = [] #BUS to Node list
    
  def construct(self, line_value):
    conf_regex = GlobalVar.conf_regex
    name_in_port        = re.search("([" + conf_regex + "]*)@[" + conf_regex + "]*", line_value).group(1)
    source_in_link      = re.search("[" + conf_regex + "]*@([" + conf_regex + "]*)<=>[" + conf_regex + "]*", line_value).group(1)
    destination_in_link = re.search("[" + conf_regex + "]*@[" + conf_regex + "]*<=>([" + conf_regex + "]*)", line_value).group(1)


    # print(GlobalVar.topology_ptr)
    link_node = GlobalVar.topology_ptr.node_dist[source_in_link]
    link_bus  = GlobalVar.topology_ptr.bus_dist[destination_in_link]

    self.port_name            = name_in_port
    # tmp_port.port_ptr             = tmp_port
    self.port_belong_node_ptr = link_node
    self.port_belong_bus_ptr  = link_bus

    link_node.node_port_dist[name_in_port] = self
    link_bus.bus_port_dist[name_in_port]   = self
    return self.port_name
    
    
    
    
    