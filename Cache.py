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
# class CacheTop
#--------------------------------------------
class Cache:
    #*************staticmethod*****************

  stateCachere      = [ "CACHE_HIT"
                      , "CACHE_MISS" ]

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
    
    print(self.config)
            
        # print(tempstr, re.search("(\d)*\*", tempstr).group(1)), int(re.search("\*(\d)*", tempstr).group(1))
        # print(self.config[iconfig])
  # def checkConfig(self):
    # self.config["subblocknum"] = int(self.getCfgByName("blocksize") / self.getCfgByName("subblocksize"))
    # self.config["blocknum"]    = int(self.getCfgByName("cachesize") / (self.getCfgByName("blocksize") * self.getCfgByName("assoc")))

    # if (self.getCfgByName("blocknum") == 0):
      # print("ICache Error: blocknum = 0")
      # exit(-1)
    # if (self.getCfgByName("subblocknum") == 0):
      # print("ICache Error: subblocknum = 0")
      # exit(-1)
    # # for iconfig in Cache.configlist:
    # #   print("%-20s"%(iconfig + ":"), end="")
    # #   print(self.getCfgByName(iconfig))

  #*************awefasdfasasd****************

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

    ### outstanding list #outsdng list, req that has "been" issue ###
    self.cache_outsdng = []

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
        ### set all transaction in bus_port_arbitor counter to exact value ###
        cur_transaction.duration_list.append(self.node_ptr)
        cur_transaction.counter = 0
        cur_transaction.state = Transaction.isTransactionState("WAIT")
        assert (not cur_transaction.destination_list == None ), ("not cur_transaction.destination_list == None")
        self.cache_outsdng.append(cur_transaction)

  def cur_cycle(self):
    for i_cache_outsdng in self.cache_outsdng:
      ### count down the counter for each transaction in cache_outsdng ###
      if(i_cache_outsdng.state == Transaction.isTransactionState("WAIT") and i_cache_outsdng.counter > 0):
        i_cache_outsdng.counter -= 1
      if(i_cache_outsdng.state == Transaction.isTransactionState("WAIT") and i_cache_outsdng.counter == 0):
        my_req = i_cache_outsdng.source_req
        cache_re = self.findCache(my_req.subblockaddr)
        ### cache HIT ### 
        if (not cache_re == None):
          ### OUTSTANDING meaning for need to send to back ###
          i_cache_outsdng.state = Transaction.isTransactionState("COMMITTED") 
        ### cache MISS ###
        elif (cache_re == None):
          ### COMMITTED meaning for need to sendback to front ###
          i_cache_outsdng.state = Transaction.isTransactionState("OUTSTANDING")
    
  def pos_cycle(self):
    for i_cache_outsdng in self.cache_outsdng:
      ### cache HIT ###
      ### COMMITTED meaning for need to sendback to front ###
      if(i_cache_outsdng.state == Transaction.isTransactionState("COMMITTED")):
        my_req = i_cache_outsdng.source_req
        
        tmp_transaction = Transaction()
        tmp_transaction.source_node = self.node_ptr
        tmp_transaction.destination_list.append(i_cache_outsdng.source_node)
        tmp_transaction.duration_list.append(self.node_ptr)
        tmp_transaction.source_req = my_req
        
        self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_higher_bus].port_NB_trans.append(tmp_transaction)
        del self.cache_outsdng[self.cache_outsdng.index(i_cache_outsdng)]
      ### cache MISS ###
      ### COMMITTED meaning for need to sendback to front ###
      elif (i_cache_outsdng.state == Transaction.isTransactionState("OUTSTANDING")):
        if(not self.node_ptr.node_lower_node == "None"):
          my_req = i_cache_outsdng.source_req
          
          tmp_transaction = Transaction()
          tmp_transaction.source_node = self.node_ptr
          tmp_transaction.destination_list.append(GlobalVar.topology_ptr.node_dist[self.node_ptr.node_lower_node])
          tmp_transaction.duration_list.append(self.node_ptr)
          tmp_transaction.source_req = my_req
          
          self.node_ptr.node_port_dist[self.node_ptr.node_name + "_" + self.node_ptr.node_lower_bus].port_NB_trans.append(tmp_transaction)
          del self.cache_outsdng[self.cache_outsdng.index(i_cache_outsdng)]        

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

  def checkblockvalid(self):
    for i_subblock in self.cacheSubBlock:
      if(i_subblock.subblock_valid == 0):
        return False
    self.valid = 1
    return True
      
  def getblockValid(self):
    return self.valid

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



