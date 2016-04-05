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
from GlobalVar import GlobalVar

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
    self.initSimulate()
    while (not self.isSimEnd()):
      self.run()


  def initSimulate(self):
    # self.transPCSimNextState("ASSIGN_PC")
    # firstPC = 0
    # a, initclock, b = self.u_PCTracer.PClist[firstPC].replace(" ", "").split(",")
    # self.current_CYC = int(initclock)

    u_topology = GlobalVar.topology_ptr

    for key, value in u_topology.node_dist.items():
      value.node_ptr.initial_cycle()
      # print("initial_cycle", key )
    for key, value in u_topology.bus_dist.items():
      value.pre_cycle()
      # print("initial_cycle", key )
    # for key, value in u_topology.port_dist.items():
      # value.pre_cycle()
      # print("initial_cycle", key )

  def run_pre_cycle(self):
    u_topology = GlobalVar.topology_ptr
    for key, value in u_topology.node_dist.items():
      value.node_ptr.pre_cycle()
    #   # print("pre_cycle", key)
    for key, value in u_topology.bus_dist.items():
      value.pre_cycle()
    #   # print("pre_cycle", key)
    # for key, value in u_topology.port_dist.items():
    #   #       value.node_ptr.pre_cycle()
    #   # print("pre_cycle", key)


  def run_cur_cycle(self):
    u_topology = GlobalVar.topology_ptr
    for key, value in u_topology.node_dist.items():
      value.node_ptr.cur_cycle()
    #   # print("pre_cycle", key)
    for key, value in u_topology.bus_dist.items():
      value.cur_cycle()
    #   print("pre_cycle", key)
    # for key, value in u_topology.port_dist.items():
    #   #       value.node_ptr.cur_cycle()
    #   print("pre_cycle", key)

  def run_pos_cycle(self):
    u_topology = GlobalVar.topology_ptr
    for key, value in u_topology.node_dist.items():
      value.node_ptr.pos_cycle()
    #   print("pre_cycle", key)
    for key, value in u_topology.bus_dist.items():
      value.pos_cycle()
    #   print("pre_cycle", key)
    # for key, value in u_topology.port_dist.items():
    #   #       value.node_ptr.pos_cycle()
    #   print("pre_cycle", key)

  def run(self):
    u_topology = GlobalVar.topology_ptr
    self.run_pre_cycle()
    self.run_cur_cycle()
    self.run_pos_cycle()
    print("current_CYC = ", self.current_CYC)
    self.current_CYC += 1


