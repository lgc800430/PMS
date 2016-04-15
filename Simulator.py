__author__ = 'mario'

#!/usr/local/bin/python
import sys
import os
import re
import optparse
import operator
import inspect
import math
import random

from Architecture import *
from Cache import *
from VLC import *
from PCTracer import *
from GlobalVar import GlobalVar

class Simulator:

  statePCSim   = ["PCTracer_CORE_STALL"
                , "PCTracer_ASSIGN_PC"
                , "PCTracer_PENDING_BY_VLC"]

  def isPCTracer_state(self, inputState):
    if (inputState in self.statePCSim):
      return inputState
    else:
      print("Error: %s is not in statePCSim list" % inputState)
      exit(1)

  def transPCSimNextState(self, thread_idx, inputState):
    self.PCTracer_nextState[thread_idx] = self.isPCTracer_state(inputState)

  def isPCTraceEnd(self, thread_idx):
    if (self.u_PCTracer[thread_idx].PCpointer >= len(self.u_PCTracer[thread_idx].PClist)):
      return True
    else:
      return False

  def isSimEnd(self):
    for iarch in range(Architecture.getCfgByName("threadnum")):
      if (not self.isPCTraceEnd(iarch)):
        return False

    return True

  def calStallTime(self, thread_idx):
    try_abstime, try_clock, try_PC = self.u_PCTracer[thread_idx].nextPC()
    return (int(try_clock) - int(self.cur_clock[thread_idx]) - 2)

  def printRunInfo(self, thread_idx, prestr, input):
    # print("%s: %15s->%15s [clk:%6s cyc:%6s PC:%6s] %s"%(  prestr
    #                                                     , self.PCTracer_state[thread_idx]
    #                                                     , self.PCTracer_nextState[thread_idx]
    #                                                     , self.cur_clock[thread_idx]
    #                                                     , self.current_CYC[thread_idx]
    #                                                     , hex(self.cur_PC[thread_idx])
    #                                                     , input))
    # realnextinst = self.u_vlc[thread_idx].instList[self.u_vlc[thread_idx].instbyteaddr2listindex[self.cur_PC[thread_idx]]].subblocklist
    # print("real = ", realnextinst)
    # print(self.u_vlc[thread_idx].vlcEntry)

    print(self.PCTracer_state[thread_idx], self.PCTracer_nextState[thread_idx], end=" ")

    for i in self.u_vlc[thread_idx].vlcEntry:
      print(i, end=", ")
    print("; ", end="")

    for i in self.u_vlc[thread_idx].outsdnglist:
      print(self.u_vlc[thread_idx].outsdnglist.index(i), i.ID, i.counter, i.state, i.subblockaddr, i.flushed, end=", ")

    print(self.u_vlc[thread_idx].instList[self.u_vlc[thread_idx].instbyteaddr2listindex[self.cur_PC[thread_idx]]].subblockaddr, end="")
    print()

  def simulate(self):
    # for thread_idx in range(2):
      # self.initSimulate(thread_idx)
    for iarch in range(Architecture.getCfgByName("threadnum")):
      self.initSimulate(iarch)
    while (not self.isSimEnd()):
    # while (not self.isPCTraceEnd(0) or not self.isPCTraceEnd(1)):
    # for i in range(200):
      for iarch in range(Architecture.getCfgByName("threadnum")):
        if not self.isPCTraceEnd(iarch):
          self.run(iarch)
    # self.printSimulateInfo()
    # self.u_cache.printCacheInfo()
    # self.u_vlc[thread_idx].printVLCInfo()
    for iarch in range(Architecture.getCfgByName("threadnum")):
      self.reportOutput(iarch)

  def initSimulate(self, thread_idx):
    self.transPCSimNextState(thread_idx, "PCTracer_ASSIGN_PC")
    firstPC = 0
    a, initclock, b = self.u_PCTracer[thread_idx].PClist[firstPC].replace(" ", "").split(",")
    self.current_CYC[thread_idx] = int(initclock)
    print("thread_idx = %d, initclock = %d" %(thread_idx, int(initclock)))

  def run(self, thread_idx):
    self.PCTracer_pre_behavioral(thread_idx)
    self.PBUS_VLC2CACHE_behavioral(thread_idx)
    self.PCTracer_post_behavioral(thread_idx)
    # self.PBUS_VLC2CACHE_post_behavioral()
    #run end CYC++
    self.current_CYC[thread_idx] += 1

  def PCTracer_pre_behavioral(self, thread_idx):
    # print(self.u_PCTracer[thread_idx].nextPC())
    self.PCTracer_state[thread_idx] = self.PCTracer_nextState[thread_idx]

    # PCTracer behavioral
    if (self.PCTracer_state[thread_idx] == self.isPCTracer_state("PCTracer_CORE_STALL")
     or self.PCTracer_state[thread_idx] == self.isPCTracer_state("PCTracer_PENDING_BY_VLC")):
      pass
    elif (self.PCTracer_state[thread_idx] == self.isPCTracer_state("PCTracer_ASSIGN_PC")):

      self.cur_abstime[thread_idx], self.cur_clock[thread_idx], self.cur_PC[thread_idx] = self.u_PCTracer[thread_idx].nextPC()
      re_VLC = self.u_vlc[thread_idx].compareNextInst(self.cur_PC[thread_idx])

      if   (re_VLC == VLC.isVLCreState("VLC_NEXT_INST_HIT")):
        pass
      elif (re_VLC == VLC.isVLCreState("VLC_NOT_NEXT_INST")):
        self.u_vlc[thread_idx].flushVLC(self.cur_PC[thread_idx])
      elif (re_VLC == VLC.isVLCreState("VLC_NEXT_INST_PARTIAL_MISS")):
        self.u_vlc[thread_idx].fillVLC(self.cur_PC[thread_idx])
      elif (re_VLC == VLC.isVLCreState("VLC_NEXT_INST_WHOLE_MISS")):
        self.u_vlc[thread_idx].fillVLC(self.cur_PC[thread_idx])
      else:
        print("Error: %s is not in VLCreState list" % re_VLC)
        exit(1)

    else:
      print("Error: %s is not in PCTracer_pre" % self.PCTracer_nextState[thread_idx])
      exit(1)

    if GlobalVar.options.Dflag == True:
      self.printRunInfo(thread_idx, "PCSimPre", "")

  def PBUS_VLC2CACHE_behavioral(self, thread_idx):
    subblocknum = Cache.getCfgByName("subblocknum")
    self.VLC_state[thread_idx] = self.VLC_nextState[thread_idx]
    # send the toppest only one request

    findMainReqToAXI = False

    for ireq in self.u_vlc[thread_idx].outsdnglist:
      if (ireq.state == Request.isRequestState("WAIT")):
        findMainReqToAXI = True
        ireq.state = Request.isRequestState("ACCESS_CACHE")
        try_Cache  = self.u_cache.findCache(ireq.subblockaddr)

        if (try_Cache == None):
          ireq.counter = Cache.getCfgByName("misspenalty")
          # print("misspenalty")
        else:
          ireq.counter = Cache.getCfgByName("hitdelay")
          # print("hitdelay")

        # -------------------prefetch---------------------
        for i in range(1, Cache.getCfgByName("prefetch") + 1):
          prefetchsubblock = (int(ireq.subblockaddr/subblocknum)+i)*subblocknum
          try_pre_Cache = self.u_cache.findCache(prefetchsubblock)
          if (try_pre_Cache == None):
            self.u_vlc[thread_idx].addPrefetch(prefetchsubblock)
        # -------------------prefetch---------------------
        break

    if(findMainReqToAXI == False):
      for iprefetch in self.u_vlc[thread_idx].prefetchqueue:
        if (iprefetch.state == Request.isRequestState("WAIT")):
          iprefetch.state = Request.isRequestState("ACCESS_CACHE")
          try_Cache  = self.u_cache.findCache(iprefetch.subblockaddr)
          if (try_Cache == None):
            iprefetch.counter = Cache.getCfgByName("misspenalty")
            # print("misspenalty")
          else:
            iprefetch.counter = Cache.getCfgByName("hitdelay")
            # print("hitdelay")
          break

    # count every req
    for ireq in self.u_vlc[thread_idx].outsdnglist:
      if (ireq.state == Request.isRequestState("ACCESS_CACHE")):
        ireq.counter -= 1
        if (ireq.counter <= 0):
          re_Cache = self.u_cache.accessCache(ireq.subblockaddr)
          ireq.state = Request.isRequestState("EMPTY")
          if (not ireq.flushed == 1):
            self.u_vlc[thread_idx].vlcEntry[ireq.ID] = ireq.subblockaddr

    # count every prefetch req
    # -------------------prefetch---------------------

    for iprefetch in self.u_vlc[thread_idx].prefetchqueue:
      if (iprefetch.state == Request.isRequestState("ACCESS_CACHE")):
        iprefetch.counter -= 1
        if (iprefetch.counter <= 0):
          re_Cache = self.u_cache.prefetchCache(iprefetch.subblockaddr)
          iprefetch.state = Request.isRequestState("EMPTY")

    # -------------------prefetch---------------------

      # reset "EMPTY" req
    for ireq in self.u_vlc[thread_idx].outsdnglist:
      if (ireq.state == Request.isRequestState("EMPTY")):
        ireq.resetAttribute()
    for iprefetch in self.u_vlc[thread_idx].prefetchqueue:
      if (iprefetch.state == Request.isRequestState("EMPTY")):
        self.u_vlc[thread_idx].prefetchqueue.remove(iprefetch)
    # # delete "EMPTY" req
    # for ireq in self.u_vlc[thread_idx].outsdnglist:
    #   if (ireq.state == Request.isRequestState("EMPTY")):
    #     del self.u_vlc[thread_idx].outsdnglist[self.u_vlc[thread_idx].outsdnglist.index(ireq)]

  def PCTracer_post_behavioral(self, thread_idx):
    # print(self.u_PCTracer[thread_idx].nextPC())
    self.PCTracer_state[thread_idx] = self.PCTracer_nextState[thread_idx]
    re_VLC = ""

    # PCTracer behavioral
    if (self.PCTracer_state[thread_idx] == self.isPCTracer_state("PCTracer_CORE_STALL")):
      if (self.PCTracer_counter[thread_idx] == 0):
        self.transPCSimNextState(thread_idx, "PCTracer_ASSIGN_PC")
      else:
        self.PCTracer_counter[thread_idx] -= 1
        self.transPCSimNextState(thread_idx, "PCTracer_CORE_STALL")

    elif (self.PCTracer_state[thread_idx] == self.isPCTracer_state("PCTracer_ASSIGN_PC")):
      self.cur_abstime[thread_idx], self.cur_clock[thread_idx], self.cur_PC[thread_idx] = self.u_PCTracer[thread_idx].nextPC()
      re_VLC = self.u_vlc[thread_idx].consumeNextInst(self.cur_PC[thread_idx])
      # #####################################
      self.u_vlc[thread_idx].incAtrByName("AccessCount")
      # #####################################
      if (re_VLC == VLC.isVLCreState("VLC_NEXT_INST_HIT")):
        # #####################################
        self.u_vlc[thread_idx].incAtrByName("HitCount")
        # #####################################
        if (not self.u_PCTracer[thread_idx].consumePC() == "PCend"):
          if (self.calStallTime(thread_idx) >= 0):
            self.PCTracer_counter[thread_idx] = self.calStallTime(thread_idx)
            self.transPCSimNextState(thread_idx, "PCTracer_CORE_STALL")
          else:
            self.transPCSimNextState(thread_idx, "PCTracer_ASSIGN_PC")

      elif (re_VLC == VLC.isVLCreState("VLC_NOT_NEXT_INST")):
        # #####################################
        self.u_vlc[thread_idx].incAtrByName("MissCount")
        # #####################################
        self.transPCSimNextState(thread_idx, "PCTracer_PENDING_BY_VLC")

      elif (re_VLC == VLC.isVLCreState("VLC_NEXT_INST_PARTIAL_MISS")):
        # #####################################
        self.u_vlc[thread_idx].incAtrByName("MissCount")
        # #####################################
        self.transPCSimNextState(thread_idx, "PCTracer_PENDING_BY_VLC")

      elif (re_VLC == VLC.isVLCreState("VLC_NEXT_INST_WHOLE_MISS")):
        # #####################################
        self.u_vlc[thread_idx].incAtrByName("MissCount")
        # #####################################
        self.transPCSimNextState(thread_idx, "PCTracer_PENDING_BY_VLC")

      else:
        print("Error: %s is not in VLCreState list" % re_VLC)
        exit(1)

    elif (self.PCTracer_state[thread_idx] == self.isPCTracer_state("PCTracer_PENDING_BY_VLC")):
      self.cur_abstime[thread_idx], self.cur_clock[thread_idx], self.cur_PC[thread_idx] = self.u_PCTracer[thread_idx].nextPC()
      re_VLC = self.u_vlc[thread_idx].consumeNextInst(self.cur_PC[thread_idx])

      if (re_VLC == VLC.isVLCreState("VLC_NEXT_INST_HIT")):
        if (not self.u_PCTracer[thread_idx].consumePC() == "PCend"):
          if (self.calStallTime(thread_idx) >= 0):
            self.PCTracer_counter[thread_idx] = self.calStallTime(thread_idx)
            self.transPCSimNextState(thread_idx, "PCTracer_CORE_STALL")
          else:
            self.transPCSimNextState(thread_idx, "PCTracer_ASSIGN_PC")
      else:
          self.transPCSimNextState(thread_idx, "PCTracer_PENDING_BY_VLC")

    else:
      print("Error: %s is not in statePCSim list" % self.PCTracer_nextState[thread_idx])
      exit(1)

    # self.printRunInfo("PCSimPost", re_VLC)

  def reportOutput(self, thread_idx):
    a, lastclock, b = self.u_PCTracer[thread_idx].PClist[len(self.u_PCTracer[thread_idx].PClist)-1].replace(" ", "").split(",")

    GlobalVar.outputptr.write("=====Performance Report====\n")
    GlobalVar.outputptr.write("#Cycle (91_PM)       =  %8d\n"% int(lastclock) )
    GlobalVar.outputptr.write("#Cycle (93_Cache_PM) =  %8d\n"% int(self.current_CYC[thread_idx]) )
    GlobalVar.outputptr.write("#Performance loss    =  %8.2f %%\n"% ((int(self.current_CYC[thread_idx]) - int(lastclock))/int(lastclock) * 100.0  ))

    GlobalVar.outputptr.write("\n========Cache Report=======\n")
    GlobalVar.outputptr.write("#Access              =  %8d\n"% (self.u_cache.getAtrByName("AccessCount")))
    GlobalVar.outputptr.write("#Hit                 =  %8d  (%5.2f %%)\n"% (self.u_cache.getAtrByName("HitCount")
                                                               ,  int(self.u_cache.getAtrByName("HitCount"))/int(self.u_cache.getAtrByName("AccessCount")) * 100.0  ))
    GlobalVar.outputptr.write("#Miss                =  %8d  (%5.2f %%)\n"% (self.u_cache.getAtrByName("MissCount")
                                                               , int(self.u_cache.getAtrByName("MissCount"))/int(self.u_cache.getAtrByName("AccessCount")) * 100.0  ))
    GlobalVar.outputptr.write("#PrefetchAccess      =  %8d\n"% (self.u_cache.getAtrByName("PrefetchCount")))

    GlobalVar.outputptr.write("\n========VLC Report=======\n")
    GlobalVar.outputptr.write("#Access              =  %8d\n"% (self.u_vlc[thread_idx].getAtrByName("AccessCount")))
    GlobalVar.outputptr.write("#Hit                 =  %8d  (%5.2f %%)\n"% (self.u_vlc[thread_idx].getAtrByName("HitCount")
                                                               ,  int(self.u_vlc[thread_idx].getAtrByName("HitCount"))/int(self.u_vlc[thread_idx].getAtrByName("AccessCount")) * 100.0  ))
    GlobalVar.outputptr.write("#Miss                =  %8d  (%5.2f %%)\n"% (self.u_vlc[thread_idx].getAtrByName("MissCount")
                                                               , int(self.u_vlc[thread_idx].getAtrByName("MissCount"))/int(self.u_vlc[thread_idx].getAtrByName("AccessCount")) * 100.0  ))

    GlobalVar.outputptr.write("\n\n\n")

    GlobalVar.outputptr.write("=======Cache config========\n")
    for icfg in Cache.configlist:
      GlobalVar.outputptr.write("%-15s = %15s\n"% (icfg
                                       , Cache.config[icfg]))

    GlobalVar.outputptr.write("\n========VLC config=========\n")
    for icfg in VLC.configlist:
      GlobalVar.outputptr.write("%-15s = %15s\n"% (icfg
                                       , VLC.config[icfg]))

  def printSimulateInfo(self, thread_idx):
    a, lastclock, b = self.u_PCTracer[thread_idx].PClist[len(self.u_PCTracer[thread_idx].PClist)-1].replace(" ", "").split(",")
    print("#Cycle (91_PM)       =  %8d"% int(lastclock) )
    print("#Cycle (93_Cache_PM) =  %8d"% int(self.current_CYC[thread_idx]) )
    print("#Performance loss    =  %f %%"% ((int(self.current_CYC[thread_idx]) - int(lastclock))/int(lastclock) * 100.0 ))




  def __init__(self):

    self.u_cache       = Cache()

    self.u_vlc = []
    ivtile = 0

    for iarch in range(Architecture.getCfgByName("threadnum")):
      self.u_vlc.append(VLC(iarch, ivtile))
      self.u_vlc[iarch].initialize()

    self.u_PCTracer = []
    for iarch in range(Architecture.getCfgByName("threadnum")):
      self.u_PCTracer.append(PCTracer(iarch, ivtile))
      self.u_PCTracer[iarch].initialize(GlobalVar.allcontents_trc[int(Architecture.getCfgByName("threadlist")[iarch])])

    self.u_cache.initialize()

    self.PCTracer_nextState = []
    self.PCTracer_state     = []
    self.PCTracer_counter   = []
    self.VLC_nextState   = []
    self.VLC_state       = []
    # self.VLC_counter     = []
    self.current_CYC     = []
    self.cur_abstime     = []
    self.cur_clock       = []
    self.cur_PC          = []
    for iarch in range(Architecture.getCfgByName("threadnum")):
      self.PCTracer_nextState.append(0)
      self.PCTracer_state.append(0)
      self.PCTracer_counter.append(0)

      self.VLC_nextState.append(0)
      self.VLC_state.append(0)
      # self.VLC_counter.append(0)

      self.current_CYC.append(0)
      self.cur_abstime.append(0)
      self.cur_clock.append(0)
      self.cur_PC.append(0)
