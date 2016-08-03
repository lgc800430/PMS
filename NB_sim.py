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
    isSimEnd = 1
    
    for key, value in u_topology.node_dist.items():
      if (isinstance((value.node_ptr), VLC)):
        if (value.node_ptr.PCTracer_ptr.PCpointer  < len(value.node_ptr.PCTracer_ptr.PClist)):
          isSimEnd = 0

    if GlobalVar.options.Dflag == True:
      print("current_CYC = ", self.current_CYC)
      # assert(self.current_CYC<7000)
      for key, value in u_topology.node_dist.items():
        if (isinstance((value.node_ptr), Cache)):
          print(value.node_name + ":", end=" ")
          for i in value.node_ptr.cache_outsdng_req:
            print(i.subblockaddr, i.source_node.node_name, end=", ")
          print("")
          # value.node_ptr.printCacheContentInfo()
          print("prefectch", value.node_ptr.cache_prefectch_subblock_queue)
          value.node_ptr.CacheContentChecker()
          
      for key, value in u_topology.bus_dist.items():
        print(value.bus_name + ":")
        for pkey, pvalue in value.bus_port_dist.items():
          print("port_NB_trans" + pkey + ":", end=" ")
          for i in pvalue.port_NB_trans:
            print(i.subblockaddr,  i.destination_list[0].node_name, end=", ")
          print("")
          print("port_BN_trans" + pkey + ":", end=" ")
          for i in pvalue.port_BN_trans:
            print(i.subblockaddr,  i.destination_list[0].node_name, end=", ")
            # assert(len(i.destination_list)==0)
            for j in i.destination_list:
              print("j", j, end=", ")
            
          print("")
        # for i in value.node_ptr.cache_outsdng_req:
          # print(i.subblockaddr, end=", ")
        print("")
        # value.node_ptr.printCacheContentInfo()
          
      print("####################################################################################################")
      print("####################################################################################################")
      print("####################################################################################################")
          
          
    if(isSimEnd == 0):
      return False
    else:
      return True

  def simulate(self):
    u_topology = GlobalVar.topology_ptr
    self.initSimulate(u_topology)
    while (not self.isSimEnd()):
      self.run(u_topology)
    
    for key, value in u_topology.node_dist.items():
      value.node_ptr.printAttributeInfo()
    print("simulate End current_CYC = ", self.current_CYC)
    
  def initSimulate(self, u_topology):
    # self.transPCSimNextState("ASSIGN_PC")
    # firstPC = 0
    # a, initclock, b = self.u_PCTracer.PClist[firstPC].replace(" ", "").split(",")
    # self.current_CYC = int(initclock)
    for key, value in u_topology.node_dist.items():
      value.node_ptr.initial_cycle()

    for key, value in u_topology.bus_dist.items():
      value.initial_cycle()
  
  # def node_pre_cycle(self, u_topology):
    # order_list = []
    # for key, value in u_topology.node_dist.items():
      # order_list.append(value)
      
    # for value in u_topology.node_dist.items():
      # value.node_ptr.pre_cycle()
  
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
      
  # def print_dbg_info(self, u_topology):
  #   # for key, value in u_topology.bus_dist.items():
  #     # value.pos_cycle()
  # 
  #   for key, value in u_topology.node_dist.items():
  #     value.node_ptr.print_dbg_info()
      
  def run(self, u_topology):
    
    ### first step => Bus run  ###
    self.bus_pre_cycle(u_topology)
    self.bus_cur_cycle(u_topology)
    self.bus_pos_cycle(u_topology)
    ### second step => Node run  ###
    self.node_pre_cycle(u_topology)
    self.node_cur_cycle(u_topology)
    self.node_pos_cycle(u_topology)
    # print("-------------------------------------------")
    # print("")
    # self.print_dbg_info(u_topology)
    # print("running current_CYC = ", self.current_CYC)
    self.current_CYC += 1
    
    


