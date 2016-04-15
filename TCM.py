#!/usr/local/bin/python
import sys
import os
import re
import optparse
import operator
import inspect
import math
import random
from GlobalVar import *
from Transaction import *


__author__ = 'MTK07896'

TOPPEST = 0
#--------------------------------------------
# class TCMTop
#--------------------------------------------
class TCM:
    #*************staticmethod*****************

  stateTCMre      = [ "TCM_HIT"
                    , "TCM_MISS" ]

  configlist      = [ "TCMdelay"
                    ]

  attributelist   = [ "MissCount"
                    , "AccessCount"
                    , "PrefetchCount"
                    , "HitCount" ]

  @staticmethod
  def isTCMreState(inputState):
    if inputState in TCM.stateTCMre:
      return inputState
    else:
      print("Error: %s is not in stateTCMre list" % inputState)
      exit(1)

  def getCfgByName(self, input_name):
    return self.config[input_name]
  def setCfgByName(self, input_name, input_var):
    print("Warning: you should not use \"setCfgByName\"!")
    self.config[input_name] = input_var
  def parseConfig(self):
    for TCM_root in GlobalVar.allcontents_conf.iter('TCM'):
      for defult_tag in TCM_root.iter('defult'):
        for sub_tag in defult_tag:

          assert(sub_tag.tag in TCM.configlist), ("%s is not in TCM.configlist " % sub_tag.tag)

          try:
            self.config[sub_tag.tag] = int(sub_tag.attrib["value"])
          except ValueError:
            tempstr = sub_tag.attrib["value"]
            # print(tempstr)
            self.config[sub_tag.tag] = int(int(re.search("([\d]*)[\s]*[Xx]", tempstr).group(1)) * int(re.search("[Xx][\s]*([\d]*)", tempstr).group(1)))
          except:
            print("TCM parseConfig Error\n")
            exit(-1)

    # user specify
    for icfg in TCM.configlist:
      user_cfg_str = "user_" + icfg
      if (not GlobalVar.options.__dict__[user_cfg_str] == None):

        try:
          self.config[icfg] = int(GlobalVar.options.__dict__[user_cfg_str])
        except ValueError:
          tempstr = str(GlobalVar.options.__dict__[user_cfg_str])
          self.config[icfg] = int(int(re.search("([\d]*)[\s]*[Xx]", tempstr).group(1)) * int(re.search("[Xx][\s]*([\d]*)", tempstr).group(1)))
        except:
          print("VLC user_ConfigError\n")
          exit(-1)


    # print(self.config)

  def getAtrByName(self, input_name):
    return self.attribute[input_name]

  def incAtrByName(self, input_name):
    self.attribute[input_name] += 1

  def initAttribute(self):
    for iattri in self.attributelist:
      self.attribute[iattri] = 0
      # print(iattri, self.getAtrByName(iattri))

  def initialize(self):
    ### parseConfig xml ###
    self.parseConfig()
    self.initAttribute()


  def __init__(self):
    self.config = {}

    self.attribute  = {}

    ### outstanding list in TCM ###
    self.TCM_outsdng = []

  def initial_cycle(self):
    pass

  def pre_cycle(self):
    for key, value in self.node_ptr.node_port_dist.items():
      if( len(value.port_BN_trans) > 0):
        ### there should be only one item in port_BN_trans of each port ###
        assert (len(value.port_BN_trans) == 1), ("len(value.port_BN_trans) == ", len(value.port_BN_trans))
        ### get the transaction ###
        cur_transaction = value.port_BN_trans[TOPPEST]
        del value.port_BN_trans[TOPPEST]
        cur_transaction.duration_list.append(self.node_ptr)
        ### set all transaction in bus_port_arbitor counter to exact value ###
        cur_transaction.counter = self.node_ptr.node_delay
        assert (cur_transaction.state == Transaction.isTransactionState("INITIAL")), ("cur_transaction.state == INITIAL")
        cur_transaction.state = Transaction.isTransactionState("WAIT")
        assert (not cur_transaction.destination_list == None ), ("not cur_transaction.destination_list == None")
        self.TCM_outsdng.append(cur_transaction)

  def cur_cycle(self):
    for i_TCM_outsdng in self.TCM_outsdng:
      ### count down the counter for each transaction in TCM_outsdng ###
      if(i_TCM_outsdng.state == Transaction.isTransactionState("WAIT") and i_TCM_outsdng.counter > 0):
        i_TCM_outsdng.counter -= 1
      if(i_TCM_outsdng.state == Transaction.isTransactionState("WAIT") and i_TCM_outsdng.counter == 0):
        i_TCM_outsdng.state = Transaction.isTransactionState("COMMITTED")

  def pos_cycle(self):
    for i_TCM_outsdng in self.TCM_outsdng:
      ### TCM HIT ###
      ### COMMITTED meaning for need to sendback to front ###
      if(i_TCM_outsdng.state == Transaction.isTransactionState("COMMITTED")):
        tmp_transaction = Transaction()
        tmp_transaction.source_node = self.node_ptr
        tmp_transaction.destination_list.append(i_TCM_outsdng.source_node)
        tmp_transaction.duration_list.append(self.node_ptr)
        tmp_transaction.subblockaddr = i_TCM_outsdng.subblockaddr

        self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_higher_bus].port_NB_trans.append(tmp_transaction)
        del self.TCM_outsdng[self.TCM_outsdng.index(i_TCM_outsdng)]
