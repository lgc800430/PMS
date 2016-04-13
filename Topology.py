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

  # configlist        = [ "Topology"
                      # ]



  def __init__(self):
    self.topology_name   = ""
    self.node_dist       = {}     #node dist
    self.port_dist       = {}     #Port dist
    self.bus_dist        = {}     #bus dist

  def constructNB(self):
    Topology_root = ""
    
    for Topology_root in GlobalVar.allcontents_conf.iter('Topology'):
      for sub_tag in Topology_root:
        class_type = sub_tag.tag
        if(class_type == "Node"):
          tmp_node = self.node_dist[sub_tag.attrib["name"]]
          tmp_node.construct(sub_tag)
        elif(class_type == "Bus"):
          tmp_bus = self.bus_dist[sub_tag.attrib["name"]]
          tmp_bus.construct(sub_tag)
    
  def parseConfig(self):
    Topology_root = ""
    
    for Topology_root in GlobalVar.allcontents_conf.iter('Topology'):
      # print(Topology_root.tag, Topology_root.attrib, Topology_root.attrib["name"])
      self.topology_name = Topology_root.attrib["name"]
      for sub_tag in Topology_root:

        class_type = sub_tag.tag

        if(class_type == "Node"):
          tmp_node = Node()
          self.node_dist[sub_tag.attrib["name"]] = tmp_node
        elif(class_type == "Bus"):
          tmp_bus = Bus()
          self.bus_dist[sub_tag.attrib["name"]] = tmp_bus
        elif(class_type == "Port"):
          tmp_port = Port()
          self.port_dist[sub_tag.attrib["name"]] = tmp_port
        else:
          print("NB: error at config file topology description = ", class_type, sub_tag)
          exit(-1)
          
        # if(class_type == "Node"):
          # tmp_node = Node()
          # self.node_dist[tmp_node.construct(sub_tag)] = tmp_node
        # elif(class_type == "Bus"):
          # tmp_bus = Bus()
          # self.bus_dist[tmp_bus.construct(sub_tag)] = tmp_bus
        # elif(class_type == "Port"):
          # tmp_port = Port()
          # self.port_dist[tmp_port.construct(sub_tag)] = tmp_port


