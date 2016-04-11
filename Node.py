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
from TCM import *
from VLC import *
from PCTracer import *
from Simulator import *
from GlobalVar import GlobalVar

class Node:
  def __init__(self):
    self.node_name       = ""     #node_name  ex: SIC
    self.node_class      = None   #node_class ex: Cache.py Cache
    
    self.node_higher_bus = None   #higher level bus
    self.node_lower_bus  = None   #lower level bus
    
    self.node_lower_node  = None   #lower level node

    self.node_ptr        = None   #pointer to instance of Cache
    self.node_port_dist  = {}     #Port dist of this Node
  def construct(self, root):
    self.node_name       = root.attrib["name"]
    self.node_class      = root.attrib["class"]
    self.node_higher_bus = root.attrib["node_higher_bus"]
    self.node_lower_bus  = root.attrib["node_lower_bus"]
    self.node_lower_node = root.attrib["node_lower_node"]

    # instance obj tmp_function by Class "class_in_node"
    tmp_function = getattr(sys.modules[__name__], self.node_class)()
    # point tmp_function to Node
    tmp_function.node_ptr = self
    tmp_function.initialize()


    self.node_ptr   = tmp_function
    return self.node_name
    
    