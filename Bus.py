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

TOPPEST = 0

class Bus:

  def __init__(self):
    self.bus_name       = ""     #bus_name  ex: PBUS
    self.bus_port_dist  = {}    #Port dist of this bus
    ### bus_port_arbitor ###
    self.bus_port_arbitor  = {}
    
  def construct(self, line_value):
    conf_regex    = GlobalVar.conf_regex
    name_in_node  = re.search("([" + conf_regex + "]*)@[" + conf_regex + "]*", line_value).group(1)
    self.bus_name = name_in_node
    return self.bus_name

  def pre_cycle(self):
    for key, value in self.bus_port_dist.items():
      if( len(value.port_NB_reqs) > 0):
        ### handle the toppest one only ###
        cur_transaction = value.port_NB_reqs[TOPPEST]
        del value.port_NB_reqs[TOPPEST]
        assert (not cur_transaction.destination_list == None ), ("not cur_transaction.destination_list == None")
        cur_transaction.duration_list.append(self)
        ### classify the transaction to right destination in bus_port_arbitor ###
        for i_destination in cur_transaction.destination_list:
          self.bus_port_arbitor[i_destination.node_name].append(cur_transaction)
          

  def cur_cycle(self):
    pass

  def pos_cycle(self):
    pass
    
    
    
    
    
    
    
    