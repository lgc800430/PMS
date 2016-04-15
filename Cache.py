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
from queue import Queue

dbg_cache_outsdng_req = Queue()
__author__ = 'MTK07896'

TOPPEST = 0
#--------------------------------------------
# class CacheTop
#--------------------------------------------
class Cache:
    #*************staticmethod*****************

  stateCachere      = [ "CACHE_WAIT"
                      , "CACHE_HIT" 
                      , "CACHE_MISS" 
                      , "CACHE_ONGO_MISS"
                      , "CACHE_ONGO_HIT"
                      , "CACHE_WRITE_BACK"
                      ]


  configlist        = [ "cachesize"
                      , "assoc"
                      , "blocknum"
                      , "blocksize"
                      , "subblocksize"
                      , "subblocknum"
                      , "hitdelay"
                      , "misspenalty"
                      , "replacement"
                      , "prefetch"
                      # , "outsdng"
                      ]

  attributelist     = [ "MissCount"
                      , "AccessCount"
                      , "PrefetchCount"
                      , "HitCount"
                      , "OngoMissCount"
                      , "OngoHitCount"                      ]

  replacement       = { "RR"     : 0
                      , "LRU"    : 1
                      , "RANDOM" : 2
                      }

  @staticmethod
  def isCachereState(inputState):
    if inputState in Cache.stateCachere:
      return inputState
    else:
      print("Error: %s is not in stateCachere list" % inputState)
      exit(1)

  def getCfgByName(self, input_name):
    return self.config[input_name]
  def setCfgByName(self, input_name, input_var):
    print("Warning: you should not use \"setCfgByName\"!")
    self.config[input_name] = input_var
  def parseConfig(self):
    for Cache_root in GlobalVar.allcontents_conf.iter('Cache'):
      for defult_tag in Cache_root.iter('defult'):
        for sub_tag in defult_tag:

          assert(sub_tag.tag in Cache.configlist), ("%s is not in Cache.configlist " % sub_tag.tag)

          try:
            self.config[sub_tag.tag] = int(sub_tag.attrib["value"])
          except ValueError:
            tempstr = sub_tag.attrib["value"]
            # print(tempstr)
            self.config[sub_tag.tag] = int(int(re.search("([\d]*)[\s]*[Xx]", tempstr).group(1)) * int(re.search("[Xx][\s]*([\d]*)", tempstr).group(1)))
          except:
            print("Cache parseConfig Error\n")
            exit(-1)

    # user specify
    for icfg in Cache.configlist:
      user_cfg_str = "user_" + icfg
      if( not icfg == "blocknum" and not icfg == "subblocknum" ):
        if (not GlobalVar.options.__dict__[user_cfg_str] == None):

          try:
            self.config[icfg] = int(GlobalVar.options.__dict__[user_cfg_str])
          except ValueError:
            tempstr = str(GlobalVar.options.__dict__[user_cfg_str])
            self.config[icfg] = int(int(re.search("([\d]*)[\s]*[Xx]", tempstr).group(1)) * int(re.search("[Xx][\s]*([\d]*)", tempstr).group(1)))
          except:
            print("VLC user_ConfigError\n")
            exit(-1)

    self.config["blocknum"]    = int((self.getCfgByName("cachesize")/self.getCfgByName("blocksize"))/self.getCfgByName("assoc"))
    self.config["subblocknum"] = int(self.getCfgByName("blocksize")/self.getCfgByName("subblocksize"))

  def getAtrByName(self, input_name):
    return self.attribute[input_name]

  def incAtrByName(self, input_name):
    self.attribute[input_name] += 1

  def initAttribute(self):
    for iattri in self.attributelist:
      self.attribute[iattri] = 0
      # print(iattri, self.getAtrByName(iattri))

  def printInfo(self, input_assoc):
    if (input_assoc < 0):
      for iassoc in self.cacheAssoc:
        for iblock in iassoc.cacheblock:
          print(iblock.tag, end=", ")
        print()
      print()
    else:
      for iblock in self.cacheAssoc[input_assoc].cacheblock:
        print(iblock.tag, end=", ")
      print()

  def printCacheContentInfo(self, input_assoc):
    self.printCacheInfo()
    print("======== [ %s ] Cache Content =======" %self.node_ptr.node_name)
    if (input_assoc < 0):
      for iblock in range(0, self.getCfgByName("blocknum")):
        print("Idx", iblock, end="   ")
        for iassoc in range(0, self.getCfgByName("assoc")):
          print("    ", end="")
          print("v:%s" %self.cacheAssoc[iassoc].cacheblock[iblock].valid, end=" ")
          print("o:%s" %self.cacheAssoc[iassoc].cacheblock[iblock].ongoing, end=" ")
          print("t:%4s" %self.cacheAssoc[iassoc].cacheblock[iblock].tag, end=" ")
          print("[", end="")
          for isubblock in range(0, self.getCfgByName("subblocknum")):
            print("%4s"%(self.cacheAssoc[iassoc].cacheblock[iblock].cacheSubBlock[isubblock].subblock_addr), end="")
          print("]", end="   ")
        print()
      print()
    else:
      for iblock in self.cacheAssoc[input_assoc].cacheblock:
        print(iblock.tag, end=", ")
      print()

  def printCacheInfo(self):
    print("======== [ %s ] Cache Report =======" %self.node_ptr.node_name)
    print("#Access              =  %8d"% (self.getAtrByName("AccessCount")))
    print("#Hit                 =  %8d  (%f %%)"% (self.getAtrByName("HitCount")
                                                ,  int(self.getAtrByName("HitCount"))/int(self.getAtrByName("AccessCount")) * 100.0 ))
    print("#Miss                =  %8d  (%f %%)"% (self.getAtrByName("MissCount")
                                                 , int(self.getAtrByName("MissCount"))/int(self.getAtrByName("AccessCount")) * 100.0))
    print("#PrefetchAccess      =  %8d"% (self.getAtrByName("PrefetchCount")))
    

  def findCacheblockToRpl(self, subblock_address):
    myblock    = (subblock_address >> int(math.log(self.getCfgByName("subblocknum"), 2)) ) % self.getCfgByName("blocknum")
    for iassoc in self.cacheAssoc:
      if (iassoc.getCacheblock(myblock).getblockValid() == 0 and iassoc.getCacheblock(myblock).getblockOngoing() == 0):
        return iassoc.getCacheblock(myblock)

    if (self.getCfgByName("replacement")   == self.replacement["RR"]):
      self.RRptr += 1
      self.RRptr %= self.getCfgByName("assoc")
      return self.cacheAssoc[self.RRptr].getCacheblock(myblock)
    elif (self.getCfgByName("replacement") == self.replacement["LRU"]):
      return self.cacheAssoc[self.LRUlist[-1]].getCacheblock(myblock)
    elif (self.getCfgByName("replacement") == self.replacement["RANDOM"]):
      random.seed(datetime.now())
      return self.cacheAssoc[random.randint(0,self.getCfgByName("assoc")-1)].getCacheblock(myblock)
    else:
      print("Error: replacement config error!")
      exit(-1)

  def findCache(self, subblock_address):
    mysubblock = subblock_address % self.getCfgByName("subblocknum")
    myblock    = (subblock_address >> int(math.log(self.getCfgByName("subblocknum"), 2)) ) % self.getCfgByName("blocknum")
    mytag      = (subblock_address >> int(math.log(self.getCfgByName("subblocknum") * self.getCfgByName("blocknum"), 2)) )
    # print(myblock, mysubblock)
    return_value = None
    for iassoc in self.cacheAssoc:
      if (iassoc.getCacheblock(myblock).getblockTag() == mytag):
        # assert(iassoc.getCacheblock(myblock).getblockValid() == 1 and iassoc.getCacheblock(myblock).getblockOngoing() == 0), ("blockValid() == 1 and Ongoing == 0 ")
        if (iassoc.getCacheblock(myblock).getblockValid() == 1):
          return_value = Cache.isCachereState("CACHE_HIT")
        elif (iassoc.getCacheblock(myblock).getblockOngoing() == 1 and iassoc.getCacheblock(myblock).cacheSubBlock[mysubblock].subblock_valid == 1):
          return_value = Cache.isCachereState("CACHE_ONGO_HIT")
        elif (iassoc.getCacheblock(myblock).getblockOngoing() == 1 and iassoc.getCacheblock(myblock).cacheSubBlock[mysubblock].subblock_valid == 0):
          return_value = Cache.isCachereState("CACHE_ONGO_MISS")
        else:
          assert(False), ("False")
    if (return_value == None):
      return_value = Cache.isCachereState("CACHE_MISS")
          # if (self.getCfgByName("replacement") == self.replacement["LRU"]):
            # self.LRUlist.remove(iassoc.assoc_ID)
            # self.LRUlist.insert(0, iassoc.assoc_ID)
    return return_value

  def prefetchCache(self, subblock_address):
    self.incAtrByName("PrefetchCount")
    self.accessCache(subblock_address)

  def accessCache(self, subblock_address):
    mytag   = (subblock_address >> int(math.log(self.getCfgByName("subblocknum") * self.getCfgByName("blocknum"), 2)) )
    myblock = (subblock_address >> int(math.log(self.getCfgByName("subblocknum"), 2)) ) % self.getCfgByName("blocknum")
    find_re = self.findCache(subblock_address)
    self.incAtrByName("AccessCount")
    #cache hit
    if (find_re == Cache.isCachereState("CACHE_HIT")):
      self.incAtrByName("HitCount")
    elif (find_re == Cache.isCachereState("CACHE_ONGO_MISS")):
      self.incAtrByName("OngoMissCount")
    elif (find_re == Cache.isCachereState("CACHE_ONGO_HIT")):
      self.incAtrByName("OngoHitCount")
    elif (find_re == Cache.isCachereState("CACHE_MISS")):
      self.incAtrByName("MissCount")
      rplblock = self.findCacheblockToRpl(subblock_address)
      rplblock.invalidblock()
      rplblock.setblockOngoing()
      rplblock.setblockTag(mytag)
    return find_re
    
  def accessSubblockCache(self, subblock_address):
    mysubblock = subblock_address % self.getCfgByName("subblocknum")
    mytag   = (subblock_address >> int(math.log(self.getCfgByName("subblocknum") * self.getCfgByName("blocknum"), 2)) )
    myblock = (subblock_address >> int(math.log(self.getCfgByName("subblocknum"), 2)) ) % self.getCfgByName("blocknum")
    find_re = self.findCache(subblock_address)
    
    # print("subblock_address", subblock_address)
    # print("mysubblock", mysubblock)
    # print("mytag", mytag)
    # print("myblock", myblock)
    # print("cache_outsdng_req", self.cache_outsdng_req)
    # print("find_re", find_re)
    # self.printCacheContentInfo(-1)
    # assert (find_re == Cache.isCachereState("CACHE_ONGO_MISS")), ("Error find_re != CACHE_ONGO_MISS", find_re)
    
    for iassoc in self.cacheAssoc:
      if (iassoc.getCacheblock(myblock).getblockOngoing() == 1 and iassoc.getCacheblock(myblock).getblockTag() == mytag):
        iassoc.getCacheblock(myblock).validSubblock(subblock_address%self.getCfgByName("subblocknum"))
        iassoc.getCacheblock(myblock).cacheSubBlock[mysubblock].subblock_addr = subblock_address
        return iassoc.getCacheblock(myblock).checkAndsetBlockfinish()
    
    # assert (False), ("Error accessSubblockCache")

  def initialize(self):
    ### parseConfig xml ###
    self.parseConfig()
    self.initAttribute()
    # create association of cache
    for iassoc in range(0, self.getCfgByName("assoc")):
      self.cacheAssoc.append(CacheAssoc())
      self.cacheAssoc[iassoc].cache_ptr = self
      self.cacheAssoc[iassoc].initializeAssoc(iassoc)

    if (self.getCfgByName("replacement") == self.replacement["LRU"]):
      for iassoc in range(0, self.getCfgByName("assoc")):
        self.LRUlist.append(iassoc)
    elif (self.getCfgByName("replacement") == self.replacement["RR"]):
      self.RRptr = 0

  def __init__(self):
    self.config = {}

    self.attribute  = {}
    self.cacheAssoc = []
    self.RRptr      = 0  #RR pointer for replacement
    self.LRUlist    = [] #LRU list for replacement

    ### outstanding list in Cache from high (Transaction) ###
    self.cache_higher_outsdng_trans = []
    ### outstanding list in Cache from low (Transaction) ###
    self.cache_lower_outsdng_trans = []
    ### outstanding list in Cache (record request from VLC) ###
    self.cache_outsdng_req = []
    ### prefectch list in Cache (subblock) ###
    self.cache_prefectch_subblock_queue = Queue()

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
        cur_transaction.state = Cache.isCachereState("CACHE_WAIT")
        assert (not cur_transaction.destination_list == None ), ("not cur_transaction.destination_list == None")

        if( value.port_belong_bus_ptr.bus_name == self.node_ptr.node_higher_bus):
          self.cache_higher_outsdng_trans.append(cur_transaction)
        elif( value.port_belong_bus_ptr.bus_name == self.node_ptr.node_lower_bus):
          self.cache_lower_outsdng_trans.append(cur_transaction)

  def cur_cycle(self):
    ### from higher ###
    for i_cache_higher_outsdng_trans in self.cache_higher_outsdng_trans:
      ### count down the counter for each transaction in cache_higher_outsdng_trans ###
      if(i_cache_higher_outsdng_trans.state == Cache.isCachereState("CACHE_WAIT") and i_cache_higher_outsdng_trans.counter > 0):
        i_cache_higher_outsdng_trans.counter -= 1
      if(i_cache_higher_outsdng_trans.state == Cache.isCachereState("CACHE_WAIT") and i_cache_higher_outsdng_trans.counter == 0):
        my_subblockaddr = i_cache_higher_outsdng_trans.subblockaddr
        ### Cache access ###
        i_cache_higher_outsdng_trans.state = self.accessCache(my_subblockaddr)
        ### Cache prefetch check access ###
        this_block_head_subblock = my_subblockaddr - (my_subblockaddr%self.getCfgByName("subblocknum"))
        # print(this_block_head_subblock, end=":")
        for i_prefetch in range(1, self.getCfgByName("prefetch") + 1):
          prefetch_block_head_subblock = this_block_head_subblock + i_prefetch*self.getCfgByName("subblocknum")
          # print(prefetch_block_head_subblock, end=";")
          if(self.findCache(prefetch_block_head_subblock) == Cache.isCachereState("CACHE_MISS")):
            self.cache_prefectch_subblock_queue.put(prefetch_block_head_subblock)
        # print(self.cache_prefectch_subblock_queue.queue)
        
        # self.cache_prefectch_subblock_queue

    ### from lower ###
    for i_cache_lower_outsdng_trans in self.cache_lower_outsdng_trans:
      ### count down the counter for each transaction in cache_lower_outsdng_trans ###
      if(i_cache_lower_outsdng_trans.state == Cache.isCachereState("CACHE_WAIT") and i_cache_lower_outsdng_trans.counter > 0):
        i_cache_lower_outsdng_trans.counter -= 1
      if(i_cache_lower_outsdng_trans.state == Cache.isCachereState("CACHE_WAIT") and i_cache_lower_outsdng_trans.counter == 0):
        cache_re = self.accessSubblockCache(i_cache_lower_outsdng_trans.subblockaddr)
        i_cache_lower_outsdng_trans.state = Cache.isCachereState("CACHE_WRITE_BACK")

  def pos_cycle(self):
    ### trigger cache_prefectch_subblock_queue ###
    if(len(self.cache_higher_outsdng_trans) == 0):
      while(not self.cache_prefectch_subblock_queue.qsize() == 0):
        i_cache_prefectch_subblock_queue = self.cache_prefectch_subblock_queue.get()
        if(self.findCache(i_cache_prefectch_subblock_queue) == Cache.isCachereState("CACHE_MISS")):
          self.incAtrByName("PrefetchCount")
          re = self.accessCache(i_cache_prefectch_subblock_queue)
          assert(re == Cache.isCachereState("CACHE_MISS")), ("accessCache = CACHE_MISS")
          ### send wrap mode transaction to lower node ###
          mod_num = self.getCfgByName("subblocknum") - (i_cache_prefectch_subblock_queue%self.getCfgByName("subblocknum"))
          for i_subblocknum in range(self.getCfgByName("subblocknum")):
            if(i_subblocknum >= mod_num):
              subblockaddr_wrap = (i_cache_prefectch_subblock_queue + i_subblocknum - self.getCfgByName("subblocknum"))
            else:
              subblockaddr_wrap = (i_cache_prefectch_subblock_queue + i_subblocknum)

            tmp_transaction = Transaction()
            tmp_transaction.source_node = self.node_ptr
            tmp_transaction.destination_list.append(GlobalVar.topology_ptr.node_dist[self.node_ptr.node_lower_node])
            tmp_transaction.duration_list.append(self.node_ptr)
            # tmp_transaction.source_req = my_req
            tmp_transaction.subblockaddr = subblockaddr_wrap

            self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_lower_bus].port_NB_trans.append(tmp_transaction)
          break
  
    ### cache_higher_outsdng_trans ###
    for i_cache_higher_outsdng_trans in self.cache_higher_outsdng_trans:
      ### cache HIT ###
      ### COMMITTED meaning for need to sendback to front ###
      my_req = i_cache_higher_outsdng_trans.source_req
      my_subblockaddr = i_cache_higher_outsdng_trans.subblockaddr
      del self.cache_higher_outsdng_trans[self.cache_higher_outsdng_trans.index(i_cache_higher_outsdng_trans)]
      
      if(i_cache_higher_outsdng_trans.state == Cache.isCachereState("CACHE_HIT")):
        tmp_transaction = Transaction()
        tmp_transaction.source_node = self.node_ptr
        tmp_transaction.destination_list.append(i_cache_higher_outsdng_trans.source_node)
        tmp_transaction.duration_list.append(self.node_ptr)
        tmp_transaction.source_req = my_req
        self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_higher_bus].port_NB_trans.append(tmp_transaction)
      elif(i_cache_higher_outsdng_trans.state == Cache.isCachereState("CACHE_ONGO_HIT")):
        tmp_transaction = Transaction()
        tmp_transaction.source_node = self.node_ptr
        tmp_transaction.destination_list.append(i_cache_higher_outsdng_trans.source_node)
        tmp_transaction.duration_list.append(self.node_ptr)
        tmp_transaction.source_req = my_req
        self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_higher_bus].port_NB_trans.append(tmp_transaction)
      ### cache MISS ###
      ### OUTSTANDING meaning for need to send to node_lower_node ###
      elif (i_cache_higher_outsdng_trans.state == Cache.isCachereState("CACHE_MISS")):
        assert (not self.node_ptr.node_lower_node == "None"), ("not self.node_ptr.node_lower_node in cache == None")
        ### record "#subblocknum" OUTSTANDING address ###
        self.cache_outsdng_req.append(my_req)
        dbg_cache_outsdng_req.put(my_subblockaddr)
        ### send wrap mode transaction to lower node ###
        mod_num = self.getCfgByName("subblocknum") - (my_subblockaddr%self.getCfgByName("subblocknum"))
        for i_subblocknum in range(self.getCfgByName("subblocknum")):
          if(i_subblocknum >= mod_num):
            subblockaddr_wrap = (my_subblockaddr + i_subblocknum - self.getCfgByName("subblocknum"))
          else:
            subblockaddr_wrap = (my_subblockaddr + i_subblocknum)

          tmp_transaction = Transaction() 
          tmp_transaction.source_node = self.node_ptr
          tmp_transaction.destination_list.append(GlobalVar.topology_ptr.node_dist[self.node_ptr.node_lower_node])
          tmp_transaction.duration_list.append(self.node_ptr)
          # tmp_transaction.source_req = my_req
          tmp_transaction.subblockaddr = subblockaddr_wrap

          self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_lower_bus].port_NB_trans.append(tmp_transaction)
      elif (i_cache_higher_outsdng_trans.state == Cache.isCachereState("CACHE_ONGO_MISS")):
        self.cache_outsdng_req.append(my_req)
        dbg_cache_outsdng_req.put(my_subblockaddr)
      else:
        assert(False), ("i_cache_higher_outsdng_trans.state must in Cache list", i_cache_higher_outsdng_trans.state)

    ### cache_lower_outsdng_trans ###
    for i_cache_lower_outsdng_trans in self.cache_lower_outsdng_trans:
      ### cache WRITE BACK ###
      ### meaning for need to sendback to front ###
      if(i_cache_lower_outsdng_trans.state == Cache.isCachereState("CACHE_WRITE_BACK")):
        ### reply cache_outsdng_req ###
        commit_cache_outsdng_req = []
        for i_cache_outsdng_req in self.cache_outsdng_req:
          if(i_cache_outsdng_req.subblockaddr == i_cache_lower_outsdng_trans.subblockaddr):
            tmp_transaction = Transaction()
            tmp_transaction.source_node = self.node_ptr
            tmp_transaction.destination_list.append(i_cache_outsdng_req.source_node)
            tmp_transaction.duration_list.append(self.node_ptr)
            tmp_transaction.source_req = i_cache_outsdng_req
            self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_higher_bus].port_NB_trans.append(tmp_transaction)
            commit_cache_outsdng_req.append(i_cache_outsdng_req)
        ### del committed cache_outsdng_req ###
        for i_commit_cache_outsdng_req in commit_cache_outsdng_req:
          self.cache_outsdng_req.remove(i_commit_cache_outsdng_req)
        
        # del self.cache_outsdng_req[self.cache_outsdng_req.index(i_cache_outsdng_req)]
        del self.cache_lower_outsdng_trans[self.cache_lower_outsdng_trans.index(i_cache_lower_outsdng_trans)]

#--------------------------------------------
# class Cache
#--------------------------------------------
class CacheAssoc:

  def getCacheblock(self, input_var):
    return self.cacheblock[input_var]

  def initializeAssoc(self, input_ID):
    self.assoc_ID = input_ID

    mycache = self.cache_ptr
    for iblock in range(0, mycache.getCfgByName("blocknum")):
      self.cacheblock.append(Cacheblock())
      self.cacheblock[iblock].cacheassoc_ptr = self
      self.cacheblock[iblock].initializeblock(iblock)

  def __init__(self):
    self.assoc_ID = -1
    self.cacheblock = []

    self.cache_ptr = -1


#--------------------------------------------
# class Cacheblock
#--------------------------------------------
class Cacheblock:

  def invalidblock(self):
    self.valid = 0
    for i_subblock in self.cacheSubBlock:
      i_subblock.subblock_valid = 0
      i_subblock.subblock_addr = -1

  def validblock(self):
    self.valid = 1
    for i_subblock in self.cacheSubBlock:
      i_subblock.subblock_valid = 1

  def validSubblock(self, index):
    self.cacheSubBlock[index].subblock_valid = 1
      
  def checkAndsetBlockfinish(self):
    for i_subblock in self.cacheSubBlock:
      if(i_subblock.subblock_valid == 0):
        return False
    self.validblock()
    self.resetblockOngoing()
    return True

  def getblockValid(self):
    return self.valid
    
  def getblockOngoing(self):
    return self.ongoing

  def setblockOngoing(self):
    self.ongoing = 1
    
  def resetblockOngoing(self):
    self.ongoing = 0
    
  def setblockTag(self, input_tag):
    self.tag = input_tag

  def getblockTag(self):
    return self.tag

  def initializeblock(self, input_ID):
    self.block_ID = input_ID

    mycache = self.cacheassoc_ptr.cache_ptr
    for isubblock in range(0, mycache.getCfgByName("subblocknum")):
      self.cacheSubBlock.append(CacheSubBlock())
      self.cacheSubBlock[isubblock].cacheblock_ptr = self
      self.cacheSubBlock[isubblock].initializeSubBlock(isubblock)

  def __init__(self):
    self.block_ID = -1
    self.cacheSubBlock = []
    self.rplptr = 0
    self.valid = 0
    self.ongoing = 0
    self.HitCount = 0
    self.MissCount = 0
    self.tag = -1

    self.cacheassoc_ptr = -1


#--------------------------------------------
# class CacheSubBlock
#--------------------------------------------
class CacheSubBlock:

  def initializeSubBlock(self, input_ID):
    self.subblock_ID = input_ID

  def __init__(self):
    self.subblock_ID    = -1
    self.subblock_valid = 0
    self.subblock_addr = -1

    self.cacheblock_ptr = -1



