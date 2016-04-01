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

from Bus import *
from Node import *
from Port import *
from Cache import *
from VLC import *
from PCTracer import *
from Simulator import *
from GlobalVar import GlobalVar



class Topology:

  configlist        = [ "Topology"
                      ]



  def __init__(self):
    self.topology_name   = ""
    self.node_dist       = {}     #node dist
    self.port_dist       = {}     #Port dist
    self.bus_dist        = {}     #bus dist


  def parseConfig(self):
    input_topology = re.search("Topology_start([" + GlobalVar.conf_s_regex + "]*)Topology_end", GlobalVar.allcontents_conf).group(1)
    # print(input_topology)

    input_list = re.findall("[\s]*([" + GlobalVar.conf_s_regex + "]+?)[\s]*\n", input_topology)

    for i_line in input_list:
      conf_regex = GlobalVar.conf_regex
      line_attri = re.search("([" + conf_regex + "]*)[\s]*[" + conf_regex + "]*", i_line).group(1)
      line_value = re.search("[" + conf_regex + "]*[\s]*([" + conf_regex + "]*)", i_line).group(1)

      if(line_attri == "Topology"):
        self.topology_name = line_value
      elif(line_attri == "Node"):
        # tmp_node = Node()
        tmp_node = Node()
        self.node_dist[tmp_node.construct(line_value)] = tmp_node
      elif(line_attri == "Bus"):
        # tmp_bus = Bus()
        tmp_bus = Bus()
        self.bus_dist[tmp_bus.construct(line_value)] = tmp_bus
      elif(line_attri == "Port"):
        # tmp_port = Port()
        tmp_port = Port()
        self.port_dist[tmp_port.construct(line_value)] = tmp_port
      else:
        print("NB: error at config file topology description = ", line_attri, line_value)
        exit(-1)




