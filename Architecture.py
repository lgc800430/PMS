
import sys
import os
import re
import optparse
import operator
import inspect
import math
import random
from GlobalVar import GlobalVar

class Architecture:

  configlist        = [ "threadnum"
                      , "threadlist"
                      , "threadpriority"
                      , "vtilenum"
                      ]

  # attributelist     = [ "MissCount"
  #                     , "AccessCount"
  #                     , "PrefetchCount"
  #                     , "HitCount" ]

  config = {}

  def __init__():
    self.attribute  = {}

  @staticmethod
  def getCfgByName(input_name):
    return Architecture.config[input_name]
  @staticmethod
  def setCfgByName(input_name, input_var):
    print("Warning: you should not use \"setCfgByName\"!")
    Architecture.config[input_name] = input_var

  @staticmethod
  def parseConfig():
    input_str = GlobalVar.allcontents_conf
    input_architecture = re.search("Architecture_start([\w\s\n\*,]*)Architecture_end", input_str).group(1)
    # print(input_architecture)
    for icfg in Architecture.configlist:
      # if( not icfg == "blocknum" and not icfg == "subblocknum" ):
      pattern = icfg + "[\s]*([\w\*,]*)"
      # print(iconfig, re.search(pattern, input_str).group(1))
      if( not icfg == "threadlist" and not icfg == "threadpriority" ):
        try:
          Architecture.config[icfg] = int(re.search(pattern, input_architecture).group(1))
        except ValueError:
          tempstr = re.search(pattern, input_architecture).group(1)
          Architecture.config[icfg] = int(int(re.search("([\d]*)[\s]*[Xx]", tempstr).group(1)) * int(re.search("[Xx][\s]*([\d]*)", tempstr).group(1)))
        except:
          print("ConfigError\n")
          exit(-1)
      else:
          try:
            tempstr = re.search(pattern, input_architecture).group(1)
            Architecture.config[icfg] = str(tempstr).split(",")
          except:
            Architecture.config[icfg].append(int(tempstr))


    # user specify
    for icfg in Architecture.configlist:
      user_cfg_str = "user_" + icfg
      if( not icfg == "threadlist" and not icfg == "threadpriority" ):
        if (not GlobalVar.options.__dict__[user_cfg_str] == None):
          try:
            Architecture.config[icfg] = int(GlobalVar.options.__dict__[user_cfg_str])
          except ValueError:
            tempstr = str(GlobalVar.options.__dict__[user_cfg_str])
            Architecture.config[icfg] = int(int(re.search("([\d]*)[\s]*[Xx]", tempstr).group(1)) * int(re.search("[Xx][\s]*([\d]*)", tempstr).group(1)))
            # Architecture.config[icfg] = str(tempstr).split(",")
          except:
            print("Architecture user_ConfigError\n")
            exit(-1)
      else:
        if (not GlobalVar.options.__dict__[user_cfg_str] == None):
          try:
            tempstr = str(GlobalVar.options.__dict__[user_cfg_str])
            Architecture.config[icfg] = str(tempstr).split(",")
          except:
            Architecture.config[icfg].append(int(tempstr))



  @staticmethod
  def checkConfig():
    # CheckConfig the relation between VLC and VLC


    if ( not len(Architecture.getCfgByName("threadlist")) == Architecture.getCfgByName("threadnum") ):
      print("ICache Error: num of threadlist != threadnum")
      exit(-1)
    if ( not len(Architecture.getCfgByName("threadpriority")) == Architecture.getCfgByName("threadnum") ):
      print("ICache Error: num of threadpriority != threadnum")
      exit(-1)
    for iconfig in Architecture.configlist:
      print("%-20s"%(iconfig + ":"), end="")
      print(Architecture.getCfgByName(iconfig))


