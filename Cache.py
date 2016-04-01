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
from datetime import datetime
from GlobalVar import GlobalVar


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
                      , "prefetch"   ]

  attributelist     = [ "misscount"
                      , "accesscount"
                      , "prefetchcount"
                      , "hitcount" ]

  replacement       = { "RR"     : 0
                      , "LRU"    : 1
                      , "RANDOM" : 2
                      }

  config = {}

  @staticmethod
  def isCachereState(inputState):
    if inputState in Cache.stateCachere:
      return inputState
    else:
      print("Error: %s is not in stateCachere list" % inputState)
      exit(1)

  @staticmethod
  def getCfgByName(input_name):
    return Cache.config[input_name]
  @staticmethod
  def setCfgByName(input_name, input_var):
    print("Warning: you should not use \"setCfgByName\"!")
    Cache.config[input_name] = input_var
  @staticmethod
  def parseConfig():
    input_str = GlobalVar.allcontents_conf
    input_cache = re.search("Cache_start([\w\s\n\*]*)Cache_end", input_str).group(1)
    # print(input_cache)
    for icfg in Cache.configlist:
      if( not icfg == "blocknum" and not icfg == "subblocknum" ):
        pattern = icfg + "[\s]*([\w\*]*)"
        # print(iconfig, re.search(pattern, input_str).group(1))
        try:
          Cache.config[icfg] = int(re.search(pattern, input_cache).group(1))
        except ValueError:
          tempstr = re.search(pattern, input_cache).group(1)
          Cache.config[icfg] = int(int(re.search("([\d]*)[\s]*[Xx]", tempstr).group(1)) * int(re.search("[Xx][\s]*([\d]*)", tempstr).group(1)))
        except:
          print("ConfigError\n")
          exit(-1)

    # user specify
    for icfg in Cache.configlist:
      user_cfg_str = "user_" + icfg
      if( not icfg == "blocknum" and not icfg == "subblocknum" ):
        if (not GlobalVar.options.__dict__[user_cfg_str] == None):

          try:
            Cache.config[icfg] = int(GlobalVar.options.__dict__[user_cfg_str])
          except ValueError:
            tempstr = str(GlobalVar.options.__dict__[user_cfg_str])
            Cache.config[icfg] = int(int(re.search("([\d]*)[\s]*[Xx]", tempstr).group(1)) * int(re.search("[Xx][\s]*([\d]*)", tempstr).group(1)))
          except:
            print("VLC user_ConfigError\n")
            exit(-1)

        # print(tempstr, re.search("(\d)*\*", tempstr).group(1)), int(re.search("\*(\d)*", tempstr).group(1))
        # print(self.config[iconfig])
  @staticmethod
  def checkConfig():
    Cache.config["subblocknum"] = int(Cache.getCfgByName("blocksize") / Cache.getCfgByName("subblocksize"))
    Cache.config["blocknum"]    = int(Cache.getCfgByName("cachesize") / (Cache.getCfgByName("blocksize") * Cache.getCfgByName("assoc")))

    if (Cache.getCfgByName("blocknum") == 0):
      print("ICache Error: blocknum = 0")
      exit(-1)
    if (Cache.getCfgByName("subblocknum") == 0):
      print("ICache Error: subblocknum = 0")
      exit(-1)
    # for iconfig in Cache.configlist:
    #   print("%-20s"%(iconfig + ":"), end="")
    #   print(Cache.getCfgByName(iconfig))

  #*************awefasdfasasd****************

  def getAtrByName(self, input_name):
    return self.attribute[input_name]

  def incAtrByName(self, input_name):
    self.attribute[input_name] += 1

  def initAttribute(self):
    for iattri in self.attributelist:
      self.attribute[iattri] = 0
      # print(iattri, self.getAtrByName(iattri))

  def initialize(self):
    self.initAttribute()
    # create association of cache
    for iassoc in range(0, Cache.getCfgByName("assoc")):
      self.cacheAssoc.append(CacheAssoc())
      self.cacheAssoc[iassoc].initializeAssoc(iassoc)

    if (Cache.getCfgByName("replacement") == self.replacement["LRU"]):
      for iassoc in range(0, Cache.getCfgByName("assoc")):
        self.LRUlist.append(iassoc)
    elif (Cache.getCfgByName("replacement") == self.replacement["RR"]):
      self.RRptr = 0

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
      for iblock in range(0, Cache.getCfgByName("blocknum")):
        for iassoc in range(0, Cache.getCfgByName("assoc")):
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
    myblock    = (subblock_address >> int(math.log(Cache.getCfgByName("subblocknum"), 2)) ) % Cache.getCfgByName("blocknum")
    for iassoc in self.cacheAssoc:
      if (iassoc.getCacheblock(myblock).getblockValid() == 0):
        return iassoc.getCacheblock(myblock)

    if (Cache.getCfgByName("replacement")   == self.replacement["RR"]):
      self.RRptr += 1
      self.RRptr %= Cache.getCfgByName("assoc")
      return self.cacheAssoc[self.RRptr].getCacheblock(myblock)
    elif (Cache.getCfgByName("replacement") == self.replacement["LRU"]):
      return self.cacheAssoc[self.LRUlist[-1]].getCacheblock(myblock)
    elif (Cache.getCfgByName("replacement") == self.replacement["RANDOM"]):
      random.seed(datetime.now())
      return self.cacheAssoc[random.randint(0,Cache.getCfgByName("assoc")-1)].getCacheblock(myblock)
    else:
      print("Error: replacement config error!")
      exit(-1)

  def findCache(self, subblock_address):
    mysubblock = subblock_address % Cache.getCfgByName("subblocknum")
    myblock    = (subblock_address >> int(math.log(Cache.getCfgByName("subblocknum"), 2)) ) % Cache.getCfgByName("blocknum")
    mytag      = (subblock_address >> int(math.log(Cache.getCfgByName("subblocknum") * Cache.getCfgByName("blocknum"), 2)) )
    # print(myblock, mysubblock)
    for iassoc in self.cacheAssoc:
      if (iassoc.getCacheblock(myblock).getblockTag() == mytag):
        if (Cache.getCfgByName("replacement") == self.replacement["LRU"]):
          self.LRUlist.remove(iassoc.assoc_ID)
          self.LRUlist.insert(0, iassoc.assoc_ID)
        return iassoc.getCacheblock(myblock)
    return None

  def prefetchCache(self, subblock_address):
    self.incAtrByName("prefetchcount")
    self.accessCache(subblock_address)

  def accessCache(self, subblock_address):
    mytag   = (subblock_address >> int(math.log(Cache.getCfgByName("subblocknum") * Cache.getCfgByName("blocknum"), 2)) )
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

  def __init__(self):
    self.attribute  = {}
    self.cacheAssoc = []
    self.RRptr      = 0  #RR pointer for replacement
    self.LRUlist    = [] #LRU list for replacement

  def initial_cycle(self):
    pass


  def pre_cycle(self):
    pass

  def cur_cycle(self):
    pass

  def pos_cycle(self):
    pass

#--------------------------------------------
# class Cache
#--------------------------------------------
class CacheAssoc:

  def getCacheblock(self, input_var):
    return self.cacheblock[input_var]

  def initializeAssoc(self, input_ID):
    self.assoc_ID = input_ID
    for iblock in range(0, Cache.getCfgByName("blocknum")):
      self.cacheblock.append(Cacheblock())
      self.cacheblock[iblock].initializeblock(iblock)

  def __init__(self):
    self.assoc_ID = -1
    self.cacheblock = []

#--------------------------------------------
# class Cacheblock
#--------------------------------------------
class Cacheblock:

  #*************CombSubBlock******************

  def invalidblock(self):
    self.valid = 0

  def validblock(self):
    self.valid = 1

  def getblockValid(self):
    return self.valid

  def setblockTag(self, input_tag):
    self.tag = input_tag

  def getblockTag(self):
    return self.tag

  #*************User interface****************
  def initializeblock(self, input_ID):
    self.block_ID = input_ID
    for isubblock in range(0, Cache.getCfgByName("subblocknum")):
      self.cacheSubBlock.append(CacheSubBlock())
      self.cacheSubBlock[isubblock].initializeSubBlock(isubblock)

  def __init__(self):
    self.block_ID = -1
    self.cacheSubBlock = []
    self.rplptr = 0
    self.valid = 0
    self.hitcount = 0
    self.misscount = 0
    self.tag = -1
  #*************User end*********************


#--------------------------------------------
# class CacheSubBlock
#--------------------------------------------
class CacheSubBlock:

  def initializeSubBlock(self, input_ID):
    self.subblock_ID = input_ID

  def __init__(self):
    self.subblock_ID = -1

  #*************User interface***************
  #*************User end*********************


