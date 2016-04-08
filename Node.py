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



class Node:

  def __init__(self):
    self.node_name       = ""     #node_name  ex: SIC
    self.node_class      = None   #node_class ex: Cache.py Cache

    self.node_ptr        = None   #pointer to instance of Cache
    self.node_port_dist  = {}     #Port dist of this Node
  def construct(self, root):
    name_in_node  = root.attrib["name"]
    class_in_node = root.attrib["class"]

    self.node_name  = name_in_node
    self.node_class = class_in_node

    # if(class_in_node == "VLC"):
    #   tmp_function = getattr(sys.modules[__name__], class_in_node)()
    # elif(class_in_node == "Cache"):
    #   tmp_function = getattr(sys.modules[__name__], class_in_node)()

    # instance obj tmp_function by Class "class_in_node"
    tmp_function = getattr(sys.modules[__name__], class_in_node)()
    # point tmp_function to Node
    tmp_function.node_ptr = self
    tmp_function.initialize()


    self.node_ptr   = tmp_function
    return self.node_name