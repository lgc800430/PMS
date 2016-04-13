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
                      , "outsdng"
                      ]

  attributelist     = [ "misscount"
                      , "accesscount"
                      , "prefetchcount"
                      , "hitcount" ]

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
    if (input_assoc < 0):
      for iblock in range(0, self.getCfgByName("blocknum")):
        for iassoc in range(0, self.getCfgByName("assoc")):
          print(self.cacheAssoc[iassoc].cacheblock[iblock].tag, end=", ")
        print()
      print()
    else:
      for iblock in self.cacheAssoc[input_assoc].cacheblock:
        print(iblock.tag, end=", ")
      print()

  def printCacheInfo(self):
    print("========Cache Report=======")
    print("#Access              =  %8d"% (self.getAtrByName("accesscount")))
    print("#Hit                 =  %8d  (%f %%)"% (self.getAtrByName("hitcount")
                                                ,  int(self.getAtrByName("hitcount"))/int(self.getAtrByName("accesscount")) * 100.0 ))
    print("#Miss                =  %8d  (%f %%)"% (self.getAtrByName("misscount")
                                                 , int(self.getAtrByName("misscount"))/int(self.getAtrByName("accesscount")) * 100.0))
    print("#PrefetchAccess      =  %8d"% (self.getAtrByName("prefetchcount")))

  def printCacheConfig(self):
    print("========Cache Report=======")
    print("#Access              =  %8d"% (self.getAtrByName("accesscount")))
    print("#Hit                 =  %8d  (%f %%)"% (self.getAtrByName("hitcount")
                                                ,  int(self.getAtrByName("hitcount"))/int(self.getAtrByName("accesscount")) * 100.0 ))
    print("#Miss                =  %8d  (%f %%)"% (self.getAtrByName("misscount")
                                                 , int(self.getAtrByName("misscount"))/int(self.getAtrByName("accesscount")) * 100.0))

  def findCacheblockToRpl(self, subblock_address):
    myblock    = (subblock_address >> int(math.log(self.getCfgByName("subblocknum"), 2)) ) % self.getCfgByName("blocknum")
    for iassoc in self.cacheAssoc:
      if (iassoc.getCacheblock(myblock).getblockValid() == 0):
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
    for iassoc in self.cacheAssoc:
      if (iassoc.getCacheblock(myblock).getblockTag() == mytag):
        if (iassoc.getCacheblock(myblock).getblockValid() == 1):
          if (self.getCfgByName("replacement") == self.replacement["LRU"]):
            self.LRUlist.remove(iassoc.assoc_ID)
            self.LRUlist.insert(0, iassoc.assoc_ID)
          return iassoc.getCacheblock(myblock)
    return None

  def prefetchCache(self, subblock_address):
    self.incAtrByName("prefetchcount")
    self.accessCache(subblock_address)

  def accessCache(self, subblock_address):
    mytag   = (subblock_address >> int(math.log(self.getCfgByName("subblocknum") * self.getCfgByName("blocknum"), 2)) )
    myblock = (subblock_address >> int(math.log(self.getCfgByName("subblocknum"), 2)) ) % self.getCfgByName("blocknum")
    find_re = self.findCache(subblock_address)
    self.incAtrByName("accesscount")
    #cache hit
    if (not find_re == None):
      self.incAtrByName("hitcount")
      return Cache.isCachereState("CACHE_HIT")
    #cache miss
    else:
      self.incAtrByName("misscount")
      
      for iassoc in self.cacheAssoc:
        if (iassoc.getCacheblock(myblock).getblockOngoing() == 1 and iassoc.getCacheblock(myblock).getblockTag() == mytag):
          return Cache.isCachereState("CACHE_ONGO_MISS")
    
      rplblock = self.findCacheblockToRpl(subblock_address)
      rplblock.invalidblock()
      rplblock.setblockOngoing()
      rplblock.setblockTag(mytag)
      return Cache.isCachereState("CACHE_MISS")

  def accessCache_bak(self, subblock_address):
    mytag   = (subblock_address >> int(math.log(self.getCfgByName("subblocknum") * self.getCfgByName("blocknum"), 2)) )
    find_re = self.findCache(subblock_address)
    self.incAtrByName("accesscount")
    #cache hit
    if (not find_re == None):
      self.incAtrByName("hitcount")
      return Cache.isCachereState("CACHE_HIT")
    #cache miss
    else:
      self.incAtrByName("misscount")
      rplblock = self.findCacheblockToRpl(subblock_address)
      rplblock.validblock()
      rplblock.setblockTag(mytag)
      return Cache.isCachereState("CACHE_MISS")
      
  def accessSubblockCache(self, subblock_address):
    mytag   = (subblock_address >> int(math.log(self.getCfgByName("subblocknum") * self.getCfgByName("blocknum"), 2)) )
    myblock = (subblock_address >> int(math.log(self.getCfgByName("subblocknum"), 2)) ) % self.getCfgByName("blocknum")
    find_re = self.findCache(subblock_address)
    assert (find_re == None), ("Error find_re == None")
    
    for iassoc in self.cacheAssoc:
      if (iassoc.getCacheblock(myblock).getblockOngoing() == 1 and iassoc.getCacheblock(myblock).getblockTag() == mytag):
        iassoc.getCacheblock(myblock).validSubblock(subblock_address%self.getCfgByName("subblocknum"))
        return iassoc.getCacheblock(myblock).checkAndsetBlockfinish()
    
    assert (False), ("Error accessSubblockCache")

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

    ### outstanding list in Cache ###
    self.cache_higher_outsdng = []
    self.cache_lower_outsdng = []

    self.cache_outsdng_req = []

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
          self.cache_higher_outsdng.append(cur_transaction)
        elif( value.port_belong_bus_ptr.bus_name == self.node_ptr.node_lower_bus):
          self.cache_lower_outsdng.append(cur_transaction)

  def cur_cycle(self):
    for i_cache_higher_outsdng in self.cache_higher_outsdng:
      ### count down the counter for each transaction in cache_higher_outsdng ###
      if(i_cache_higher_outsdng.state == Cache.isCachereState("CACHE_WAIT") and i_cache_higher_outsdng.counter > 0):
        i_cache_higher_outsdng.counter -= 1
      if(i_cache_higher_outsdng.state == Cache.isCachereState("CACHE_WAIT") and i_cache_higher_outsdng.counter == 0):
        my_req = i_cache_higher_outsdng.source_req
        i_cache_higher_outsdng.state = self.accessCache(my_req.subblockaddr)
        print("here", i_cache_higher_outsdng.source_node.node_name, i_cache_higher_outsdng.state, my_req.subblockaddr)

    for i_cache_lower_outsdng in self.cache_lower_outsdng:
      ### count down the counter for each transaction in cache_lower_outsdng ###
      if(i_cache_lower_outsdng.state == Cache.isCachereState("CACHE_WAIT") and i_cache_lower_outsdng.counter > 0):
        i_cache_lower_outsdng.counter -= 1
      if(i_cache_lower_outsdng.state == Cache.isCachereState("CACHE_WAIT") and i_cache_lower_outsdng.counter == 0):
        cache_re = self.accessSubblockCache(i_cache_lower_outsdng.subblockaddr)
        i_cache_lower_outsdng.state = Cache.isCachereState("CACHE_WRITE_BACK")

  def pos_cycle(self):
    for i_cache_higher_outsdng in self.cache_higher_outsdng:
      ### cache HIT ###
      ### COMMITTED meaning for need to sendback to front ###
      my_req = i_cache_higher_outsdng.source_req
      del self.cache_higher_outsdng[self.cache_higher_outsdng.index(i_cache_higher_outsdng)]
      
      if(i_cache_higher_outsdng.state == Cache.isCachereState("CACHE_HIT")):
        
        tmp_transaction = Transaction()
        tmp_transaction.source_node = self.node_ptr
        tmp_transaction.destination_list.append(i_cache_higher_outsdng.source_node)
        tmp_transaction.duration_list.append(self.node_ptr)
        tmp_transaction.source_req = my_req

        self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_higher_bus].port_NB_trans.append(tmp_transaction)
      ### cache MISS ###
      ### OUTSTANDING meaning for need to send to node_lower_node ###
      elif (i_cache_higher_outsdng.state == Cache.isCachereState("CACHE_MISS")):
        assert (not self.node_ptr.node_lower_node == "None"), ("not self.node_ptr.node_lower_node in cache == None")
        ### record "#subblocknum" OUTSTANDING address ###
        self.cache_outsdng_req.append(my_req)
        dbg_cache_outsdng_req.put(my_req.subblockaddr)
        mod_num = self.getCfgByName("subblocknum") - (my_req.subblockaddr%self.getCfgByName("subblocknum"))
        for i_subblocknum in range(self.getCfgByName("subblocknum")):
          if(i_subblocknum >= mod_num):
            subblockaddr_wrap = (my_req.subblockaddr + i_subblocknum - self.getCfgByName("subblocknum"))
          else:
            subblockaddr_wrap = (my_req.subblockaddr + i_subblocknum)

          tmp_transaction = Transaction()
          tmp_transaction.source_node = self.node_ptr
          tmp_transaction.destination_list.append(GlobalVar.topology_ptr.node_dist[self.node_ptr.node_lower_node])
          tmp_transaction.duration_list.append(self.node_ptr)
          # tmp_transaction.source_req = my_req
          tmp_transaction.subblockaddr = subblockaddr_wrap

          self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_lower_bus].port_NB_trans.append(tmp_transaction)
      elif (i_cache_higher_outsdng.state == Cache.isCachereState("CACHE_ONGO_MISS")):
        self.cache_outsdng_req.append(my_req)
        dbg_cache_outsdng_req.put(my_req.subblockaddr)

    for i_cache_lower_outsdng in self.cache_lower_outsdng:
      ### cache WRITE BACK ###
      ### meaning for need to sendback to front ###
      if(i_cache_lower_outsdng.state == Cache.isCachereState("CACHE_WRITE_BACK")):
        for i_cache_outsdng_req in self.cache_outsdng_req:
          if(i_cache_outsdng_req.subblockaddr == i_cache_lower_outsdng.subblockaddr):
            tmp_transaction = Transaction()
            tmp_transaction.source_node = self.node_ptr
            tmp_transaction.destination_list.append(i_cache_outsdng_req.source_node)
            tmp_transaction.duration_list.append(self.node_ptr)
            tmp_transaction.source_req = i_cache_outsdng_req
            self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_higher_bus].port_NB_trans.append(tmp_transaction)
          del self.cache_outsdng_req[self.cache_outsdng_req.index(i_cache_outsdng_req)]
        del self.cache_lower_outsdng[self.cache_lower_outsdng.index(i_cache_lower_outsdng)]

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
    self.hitcount = 0
    self.misscount = 0
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

    self.cacheblock_ptr = -1



