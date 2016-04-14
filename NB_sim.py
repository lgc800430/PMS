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
from Topology import *

from Cache import *
from VLC import *
from PCTracer import *
from GlobalVar import *

class NB_sim:
  def __init__(self):
    self.current_CYC = 0 #this is the central cycle of all simulator

  def isSimEnd(self):
    u_topology = GlobalVar.topology_ptr
    for key, value in u_topology.node_dist.items():
      if (isinstance((value.node_ptr), VLC)):
        if (value.node_ptr.PCTracer_ptr.PCpointer  < len(value.node_ptr.PCTracer_ptr.PClist)):
          return False

    return True

  def simulate(self):
    # for thread_idx in range(2):
      # self.initSimulate(thread_idx)
    u_topology = GlobalVar.topology_ptr
    self.initSimulate(u_topology)
    while (not self.isSimEnd()):
      self.run(u_topology)
    
    for key, value in u_topology.node_dist.items():
      if(value.node_class == "Cache"):
        value.node_ptr.printCacheContentInfo(-1)
    

  def initSimulate(self, u_topology):
    # self.transPCSimNextState("ASSIGN_PC")
    # firstPC = 0
    # a, initclock, b = self.u_PCTracer.PClist[firstPC].replace(" ", "").split(",")
    # self.current_CYC = int(initclock)

    for key, value in u_topology.node_dist.items():
      value.node_ptr.initial_cycle()

    for key, value in u_topology.bus_dist.items():
      value.initial_cycle()

  def node_pre_cycle(self, u_topology):
    for key, value in u_topology.node_dist.items():
      value.node_ptr.pre_cycle()

  def bus_pre_cycle(self, u_topology):
    for key, value in u_topology.bus_dist.items():
      value.pre_cycle()

  def node_cur_cycle(self, u_topology):
    for key, value in u_topology.node_dist.items():
      value.node_ptr.cur_cycle()

  def bus_cur_cycle(self, u_topology):
    for key, value in u_topology.bus_dist.items():
      value.cur_cycle()

  def node_pos_cycle(self, u_topology):
    for key, value in u_topology.node_dist.items():
      value.node_ptr.pos_cycle()

  def bus_pos_cycle(self, u_topology):
    for key, value in u_topology.bus_dist.items():
      value.pos_cycle()

  def run(self, u_topology):

    ### first step => Bus run  ###
    self.bus_pre_cycle(u_topology)
    self.bus_cur_cycle(u_topology)
    self.bus_pos_cycle(u_topology)
    ### second step => Node run  ###
    self.node_pre_cycle(u_topology)
    self.node_cur_cycle(u_topology)
    self.node_pos_cycle(u_topology)
    
    print("current_CYC = ", self.current_CYC)
    self.current_CYC += 1
    
    


