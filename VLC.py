__author__ = 'MTK07896'

#!/usr/local/bin/python
import sys
import os
import re
import optparse
import operator
import inspect
import math
import random
from queue import Queue
from Cache import *
from Inst import *
from Request import *
from GlobalVar import GlobalVar
from PCTracer import *

#--------------------------------------------
# class VLC
#--------------------------------------------
class VLC:

  #*************staticmethod*****************


  stateVLCre        = [ "VLC_NOT_NEXT_INST"
                      , "VLC_NEXT_INST_HIT"
                      , "VLC_NEXT_INST_PARTIAL_MISS"
                      , "VLC_NEXT_INST_WHOLE_MISS" ]
  configlist        = [ "depth"
                      , "entrysize"
                      , "outsdng" ]
  attributelist     = [ "misscount"
                      , "accesscount"
                      , "hitcount"
                      , "VLC_FIFO_EMPTY"
                      , "VLC_FIFO_EMPTY_AVG" ]
  config = {}

  @staticmethod
  def isVLCreState(inputState):
    assert (inputState in VLC.stateVLCre), ("Error: %s is not in VLC stateVLCre list" % inputState)
    return inputState

  @staticmethod
  def getCfgByName(input_name):
    return VLC.config[input_name]

  @staticmethod
  def setCfgByName(input_name, input_var):
    print("Warning: you should not use \"setCfgByName\"!")
    VLC.config[input_name] = input_var

  @staticmethod
  def parseConfig():
    input_str = GlobalVar.allcontents_conf
    input_VLC = re.search("VLC_start([\w\s\n\*]*)VLC_end", input_str).group(1)
    # print(input_VLC)
    for iconfig in VLC.configlist:
      pattern = iconfig + "[\s]*([\w\*]*)"
      # print("pattern", pattern)
      # print(iconfig, re.search(pattern, input_str).group(1))
      try:
        VLC.config[iconfig] = int(re.search(pattern, input_str).group(1))
      except ValueError:
        tempstr = re.search(pattern, input_str).group(1)
        VLC.config[iconfig] = int(re.search("([\d]*)\*", tempstr).group(1)) * int(re.search("\*([\d]*)", tempstr).group(1))
      except:
        print("ConfigError\n")
        exit(-1)
    # user specify
    for icfg in VLC.configlist:
      user_cfg_str = "user_" + icfg
      if (not GlobalVar.options.__dict__[user_cfg_str] == None):
        try:
          VLC.config[icfg] = int(GlobalVar.options.__dict__[user_cfg_str])
        except ValueError:
          VLC.config[icfg] = str(GlobalVar.options.__dict__[user_cfg_str])
        except:
          print("VLC user_ConfigError\n")
          exit(-1)

  @staticmethod
  def checkConfig():
    # CheckConfig the relation between VLC and VLC
    if (not int((VLC.getCfgByName("entrysize") == Cache.getCfgByName("subblocksize")))):
      print("ICache Error: entrysize != subblocksize")
      exit(-1)

  @staticmethod
  def convertByteAddrToSubblockAddr(byte_addr):
    return int(byte_addr/Cache.getCfgByName("subblocksize"))

  def getAtrByName(self, input_name):
    return self.attribute[input_name]

  def incAtrByName(self, input_name):
    self.attribute[input_name] += 1

  def initAttribute(self):
    for iattri in self.attributelist:
      self.attribute[iattri] = 0

  def printVLCInfo(self):
    print("========VLC Report=======")
    print("#Access              =  %8d"% (self.getAtrByName("accesscount")))
    print("#Hit                 =  %8d  (%f %%)"% (self.getAtrByName("hitcount")
                                                ,  int(self.getAtrByName("hitcount"))/int(self.getAtrByName("accesscount")) * 100.0 ))
    print("#Miss                =  %8d  (%f %%)"% (self.getAtrByName("misscount")
                                                 , int(self.getAtrByName("misscount"))/int(self.getAtrByName("accesscount")) * 100.0))

  def initInstList(self, input_asm):
    # print(input_asm)
    start_point = input_asm.replace(re.search("([\w\s\.\-\:\[\]\n]*)start:", input_asm).group(1), "")
    # print(start_point)


    # instlist create
    asmlistall = start_point.split("\n")
    instnum    = 0
    addrlen    = 0
    nowtag     = ""
    tagnum     = 0
    nowaddr    = 0
    nowasm     = ""
    for inlist in asmlistall:
      if (not re.search("[\w\d\.\_]*:", inlist) == None):
        nowtag       = re.search("([\w\d\.\_]*):", inlist).group(1)

        # print("%s:" %(nowtag))
      elif (not re.search("^[\da-z]+", inlist) == None):

        nowaddr_16   = re.search("(^[\da-z]+)", inlist).group(1)
        nowaddr      = int(nowaddr_16, 16)
        machine_code = re.search("^[\da-z]+[\s]+([\w ]+)   ", inlist).group(1)
        nowasm       = re.search("^[\da-z]+[\s]+[\w ]+   ([\w\d\.\-\:\[\]\| \t\-\,\_]*)", inlist).group(1)
        addrlen      = int(machine_code.count(' ') + 1)
        subaddr      = self.convertByteAddrToSubblockAddr(nowaddr)

        self.instbyteaddr2listindex[nowaddr] = instnum
        self.instList.append((Inst(instnum, addrlen, nowaddr, machine_code, nowtag, tagnum, nowasm, subaddr)))

        tagnum       += 1
        instnum      += 1
        # print("%s   %21s   %s" %(nowaddr, machine_code, nowasm))

    # subblocklist handle
    subblock = 0
    subblocksize = Cache.getCfgByName("subblocksize")
    iinst = 0
    while (iinst < len(self.instList)):
      while (subblocksize > 0 and iinst < len(self.instList)):
        subblocksize -= self.instList[iinst].length
        self.instList[iinst].subblocklist.append(subblock)
        # if subblocksize >= 0:
        #   self.instList[iinst].subblocklist.append(self.instList[iinst].length)
        # else:
        #   self.instList[iinst].subblocklist.append(self.instList[iinst].length + subblocksize)
        iinst += 1
      subblock += 1
      if (subblocksize < 0):
        self.instList[iinst-1].subblocklist.append(subblock)
        # self.instList[iinst-1].subblocklist.append(int(subblocksize*-1))
        subblocksize = Cache.getCfgByName("subblocksize") +  subblocksize
      else:
        subblocksize = Cache.getCfgByName("subblocksize")

  def compareNextInst(self, input_nextinst):
    re = ""
    # happened in the beginning
    if (self.instptr == -1):
      re = "VLC_NOT_NEXT_INST"
    # print("self.instptr", self.instptr, "=", self.instList[self.instptr])

    predictnextinst = self.instList[self.instptr]
    realnextinst    = self.instList[self.instbyteaddr2listindex[input_nextinst]]

    # VLC predict miss
    if (not predictnextinst == realnextinst):
      re = "VLC_NOT_NEXT_INST"
    # VLC predict hit in the inst head
    # check the total inst len
    else:
      inst_total_part = len(predictnextinst.subblocklist)
      inst_found_part = 0
      for iinstsubblock in predictnextinst.subblocklist:
        if (iinstsubblock in self.vlcEntry):
          inst_found_part += 1
      # print(inst_total_part, inst_found_part, predictnextinst.subblocklist, self.vlcEntry)

      if (not inst_found_part == inst_total_part):
        # print("There are some part of NextInst is not in VLC = ", self.instptr, ":", iinstpart)
        if (not inst_total_part == 1 and not inst_found_part == 0):
          re = "VLC_NEXT_INST_PARTIAL_MISS"
        else:
          re = "VLC_NEXT_INST_WHOLE_MISS"
      else:
        re = "VLC_NEXT_INST_HIT"
    return re

  def consumeNextInst(self):
    
    self.findFreeEntryandFill(self.instptr)

  def resetEntryBySubblock(self, input_subblock):
    for ientry in range(0, len(self.vlcEntry)):
      if (self.vlcEntry[ientry] == input_subblock):
        self.vlcEntry[ientry] = -1

  def consumeEntryAndInstptr(self):
    # print("consumeEntry")
    if (self.instptr < len(self.instList) - 1):
      if (not self.instList[self.instptr].subblockaddr == self.instList[self.instptr+1].subblockaddr):
        self.resetEntryBySubblock(self.instList[self.instptr].subblockaddr)
      self.instptr      += 1

  def findFreeEntryandFill(self):
    # find free Entry if non return
    free_Entry = -1
    for ientry in range(0, VLC.getCfgByName("depth")):
      if(self.vlcEntry[ientry] == -1):
        free_Entry = ientry
        break
    if(free_Entry == -1):
      return

    # find free outsdng if non return
    free_outsdng = -1
    for ioutsdnglist in range(0, VLC.getCfgByName("outsdng")):
      # find a free outsdng
      if(self.outsdnglist[ioutsdnglist].state == Request.isRequestState("INITIAL")):
        free_outsdng = ioutsdnglist
        break
    if(free_outsdng == -1):return

    if(not self.subblock_queue.qsize() == 0):
      item_subblock = self.subblock_queue.get()
      self.vlcEntry[free_Entry]                   = -2
      self.outsdnglist[free_outsdng].resetAttribute()
      self.outsdnglist[free_outsdng].ID           = free_Entry
      self.outsdnglist[free_outsdng].state        = Request.isRequestState("WAIT")
      self.outsdnglist[free_outsdng].subblockaddr = item_subblock


  def fillVLC(self, input_addr):
    pass

  def resetvlcEntry(self):
    for ientry in range(0, len(self.vlcEntry)):
      self.vlcEntry[ientry] = -1

  def flushVLC(self, input_addr):
    next_wanted_insthead  = self.instList[self.instbyteaddr2listindex[input_addr]].subblockaddr
    self.instptr          = self.instList[self.instbyteaddr2listindex[input_addr]].ID

    # reset VLC fifo
    self.resetvlcEntry()

    for ioutsdnglist in range(VLC.getCfgByName("outsdng")):
      if( not self.outsdnglist[ioutsdnglist].state == Request.isRequestState("INITIAL")):
        self.outsdnglist[ioutsdnglist].flushed = True
    
    self.subblock_queue.put(next_wanted_insthead)
    return

  def calStallTime(self):
    myPCTracer = self.PCTracer_ptr
    try_abstime, try_clock, try_PC = myPCTracer.nextPC()
    return (int(try_clock) - int(self.cur_clock) - 1)

    
  def initialize(self):
    input_asm = GlobalVar.allcontents_asm
    self.initAttribute()
    self.initInstList(input_asm)
    # create association of VLC
    for ientry in range(VLC.getCfgByName("depth")):
      self.vlcEntry.append(-1)
    
    for ioutsdnglist in range(VLC.getCfgByName("outsdng")):
      self.outsdnglist.append(Request())

    self.subblock_queue   = Queue()
    
    input_VLC_instance = re.search(self.node_ptr.node_name + "_start([\w\s\n\*]*)" + self.node_ptr.node_name + "_end", GlobalVar.allcontents_conf).group(1)
    Trace_idx = re.search("Trace_idx[\s]*([\d]*)", input_VLC_instance).group(1)
    # for every VLC there is a PCTracker
    self.PCTracer_ptr = PCTracer()
    self.PCTracer_ptr.initialize(int(Trace_idx))

  def __init__(self):
    self.node_ptr = None

    self.PCTracer_ptr = None
    self.attribute = {}

    # inst list
    self.instList = []                #inst list
    self.instptr = -1                 #inst list pointer
    self.instbyteaddr2listindex = {}  # ?
    # entry list
    self.vlcEntry = []                # store the sub-block addr, represent it is in the VLC
    # outstanding list
    self.outsdnglist = []             #outsdng list, req that has been issue
    self.subblock_queue   = None           #outsdng list, req that is waiting for issue
    
    # for self.PCTracer_ptr.nextPC(), may be is useless?
    self.cur_abstime = 0
    self.cur_clock = 0
    self.cur_PC = 0
    
    self.VLC_state = 0
    # self.VLC_nextState = 0

  def initial_cycle(self):
    myPCTracer = self.PCTracer_ptr
    myPCTracer.transPCTracerNextState("PCTracer_ASSIGN_PC")

  def pre_cycle(self):
    myPCTracer = self.PCTracer_ptr
    # for VLC input PClist check
    if (myPCTracer.PCpointer >= len(myPCTracer.PClist)):
      return

  def cur_cycle(self):
    myPCTracer = self.PCTracer_ptr
    # for VLC input PClist check
    if (myPCTracer.PCpointer >= len(myPCTracer.PClist)):
      return
      
    #PCTracer_state state machine transmit
    myPCTracer.PCTracer_state = myPCTracer.PCTracer_nextState

    self.cur_abstime, self.cur_clock, self.cur_PC = myPCTracer.nextPC()
    self.VLC_state = VLC.isVLCreState(self.compareNextInst(self.cur_PC))
    
    
    PCTracerNextState = ""
    if (myPCTracer.PCTracer_state == PCTracer.isPCTracer_state("PCTracer_CORE_STALL")):
      if (self.PCTracer_counter == 0):
        PCTracerNextState = ("PCTracer_ASSIGN_PC")
      else:
        self.PCTracer_counter -= 1
        PCTracerNextState = ("PCTracer_CORE_STALL")

    elif (myPCTracer.PCTracer_state == PCTracer.isPCTracer_state("PCTracer_PENDING_BY_VLC")):

      if (self.VLC_state == VLC.isVLCreState("VLC_NEXT_INST_HIT")):
        self.consumeEntryAndInstptr()
        self.incAtrByName("hitcount")# #####################################
        if (not myPCTracer.consumePC() == "PCend"):
          self.PCTracer_counter = self.calStallTime()
          if (self.PCTracer_counter > 0):
            PCTracerNextState = ("PCTracer_CORE_STALL")
          else:
            PCTracerNextState = ("PCTracer_ASSIGN_PC")
      else:
        PCTracerNextState = ("PCTracer_PENDING_BY_VLC")
    
    elif (myPCTracer.PCTracer_state == PCTracer.isPCTracer_state("PCTracer_ASSIGN_PC")):
      self.incAtrByName("accesscount")# #####################################
      if   (self.VLC_state == VLC.isVLCreState("VLC_NEXT_INST_HIT")):
        self.consumeEntryAndInstptr()
        self.incAtrByName("hitcount")# #####################################
        if (not myPCTracer.consumePC() == "PCend"):
          self.PCTracer_counter = self.calStallTime()
          if (self.PCTracer_counter > 0):
            PCTracerNextState = ("PCTracer_CORE_STALL")
          else:
            PCTracerNextState = ("PCTracer_ASSIGN_PC")
      elif (self.VLC_state == VLC.isVLCreState("VLC_NOT_NEXT_INST")):
        self.flushVLC(self.cur_PC)
        PCTracerNextState = ("PCTracer_PENDING_BY_VLC")
        self.incAtrByName("misscount")  # #####################################
      elif (self.VLC_state == VLC.isVLCreState("VLC_NEXT_INST_PARTIAL_MISS")):
        PCTracerNextState = ("PCTracer_PENDING_BY_VLC")
        self.incAtrByName("misscount")  # #####################################
      elif (self.VLC_state == VLC.isVLCreState("VLC_NEXT_INST_WHOLE_MISS")):
        PCTracerNextState = ("PCTracer_PENDING_BY_VLC")
        self.incAtrByName("misscount")  # #####################################
    
    myPCTracer.transPCTracerNextState(PCTracerNextState)
    self.findFreeEntryandFill()

    # reset "COMMITTED" req
    for ireq in self.outsdnglist:
      if (ireq.state == Request.isRequestState("COMMITTED")):
        ireq.resetAttribute()

  def pos_cycle(self):
    myPCTracer = self.PCTracer_ptr
    # for VLC input PClist check
    if (myPCTracer.PCpointer >= len(myPCTracer.PClist)):
      return

    for ioutsdnglist in range(VLC.getCfgByName("outsdng")):
      if(ioutsdnglist.state == Request.isRequestState("WAIT")):
        pass
      
      
      
      
