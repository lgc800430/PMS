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
from datetime import datetime

from Architecture import *
from Cache import *
from VLC import *
from PCTracer import *
from Simulator import *
from GlobalVar import GlobalVar


#############################################
## Main start
#############################################
if __name__ == "__main__":

  print("main starting")

  parser = optparse.OptionParser()

  parser.add_option("--Dflag"         , action="store_true", dest="Dflag")
  parser.add_option("--ShowProgress"         , action="store_true", dest="ShowProgress")
  # Input Parser
  parser.add_option("-c","--config"   , action="store"     , dest="input_conf"  , default="MT6296_Program_Memory_Simulator.config")
  # parser.add_option("-a","--assembly" , action="store"     , dest="input_asm"   , default="ELBRUS_PCB01_ELBRUS_S00_DOUBLE_ICC_IMC.disasm")
  parser.add_option("-a","--assembly" , action="store"     , dest="input_asm"   , default="ICC_IMC.txt")
  default_trace = ""
  default_trace += "icc_pm_profiling_35525_shift00000000.txt"
  default_trace += ",imc_pm_profiling_35525_shift0001e734.txt"
  default_trace += ",icc_pm_profiling_35515_shift00042f3b.txt"
  default_trace += ",imc_pm_profiling_35515_shift0006166f.txt"

  # parser.add_option("-t","--trace"    , action="store"     , dest="input_trc"   , default=default_trace)
  parser.add_option("-t","--trace"    , action="store"     , dest="input_trc"   , default="icc.txt,imc.txt")
  parser.add_option("-o","--output"   , action="store"     , dest="output_re"   , default="output.txt")
  #Architecture Config
  parser.add_option("--threadnum"     , action="store"     , dest="user_threadnum")
  parser.add_option("--threadlist"    , action="store"     , dest="user_threadlist")
  parser.add_option("--threadpriority", action="store"     , dest="user_threadpriority")
  parser.add_option("--vtilenum"      , action="store"     , dest="user_vtilenum")
  #Cache Config
  parser.add_option("--cachesize"     , action="store"     , type="string"      , dest="user_cachesize")
  parser.add_option("--assoc"         , action="store"     , dest="user_assoc")
  parser.add_option("--block"         , action="store"     , dest="user_block")
  parser.add_option("--blocksize"     , action="store"     , dest="user_blocksize")
  parser.add_option("--subblocksize"  , action="store"     , dest="user_subblocksize")
  parser.add_option("--subblocknum"   , action="store"     , dest="user_subblocknum")
  parser.add_option("--hitdelay"      , action="store"     , dest="user_hitdelay")
  parser.add_option("--misspenalty"   , action="store"     , dest="user_misspenalty")
  parser.add_option("--replacement"   , action="store"     , dest="user_replacement")
  parser.add_option("--prefetch"      , action="store"     , dest="user_prefetch")
  #PC,VLC Config
  parser.add_option("--depth"         , action="store"     , dest="user_depth")
  parser.add_option("--entrysize"     , action="store"     , dest="user_entrysize")
  parser.add_option("--outsdng"       , action="store"     , dest="user_outsdng")
  parser.add_option("--PBUS_bandwidth", action="store"     , dest="user_PBUS_bandwidth")
  parser.add_option("--PBUS_priority" , action="store"     , dest="user_PBUS_priority")

  (GlobalVar.options, args) = parser.parse_args()

  # print(GlobalVar.options)
  # config file exist check
  if ( os.path.isfile(GlobalVar.options.input_conf) == False):
    print("Error :Config file '%1s' does not exist, please check." % GlobalVar.options.input_conf)
    exit(1)
  # asm file exist check
  if ( os.path.isfile(GlobalVar.options.input_asm) == False):
    print("Error :Assembly file '%1s' does not exist, please check." % GlobalVar.options.input_asm)
    exit(1)

  input_conf_ptr      = open(GlobalVar.options.input_conf, "r")
  input_asm_ptr       = open(GlobalVar.options.input_asm , "r")
  GlobalVar.outputptr = open(GlobalVar.options.output_re , "w")
  GlobalVar.outputptr.write(str(sys.argv) + "\n")

  input_trc_list            = []
  input_trc_list_ptr        = []
  GlobalVar.allcontents_trc = []
  input_trc_list = str(GlobalVar.options.input_trc).split(",")
  # input_trc_ptr = open(GlobalVar.options.input_trc , "r")

  for i_trc in input_trc_list:
      # trc file exist check
    if ( os.path.isfile(i_trc) == False):
      print("Error :Trace log file '%1s' does not exist, please check." % i_trc)
      exit(1)
    input_trc_list_ptr.append(open(i_trc , "r"))
  for i_trc_ptr in input_trc_list_ptr:
    GlobalVar.allcontents_trc.append(i_trc_ptr.read())

  # print(str(sys.argv))

  GlobalVar.allcontents_conf = re.sub("#.*", "", input_conf_ptr.read())
  print(GlobalVar.allcontents_conf)
  GlobalVar.allcontents_asm  = re.sub("//[\w \t\.,_\|]*", "" , input_asm_ptr.read())

  input_conf_ptr.close()
  input_asm_ptr.close()
  for i_trc in range(len(input_trc_list)):
    input_trc_list_ptr[i_trc].close()

  # print(GlobalVar.allcontents_asm)

  Architecture.parseConfig()
  # Cache.parseConfig()
  # VLC.parseConfig()
  # Architecture.checkConfig()
  # Cache.checkConfig()
  # VLC.checkConfig()

  #################################################################

  u_simulator = Simulator()

  u_simulator.simulate()

  GlobalVar.outputptr.close()

  # for i in range(0, 100000):
  #   U_Cache.accessCache(random.randint((256*16)*500,(256*16)*512))
  # U_Cache.accessCache(1)
  # U_Cache.accessCache(12)
  # U_Cache.accessCache(14)
  # U_Cache.accessCache(16)
  # U_Cache.accessCache(10)
  # U_Cache.accessCache(16*256-1)
  # U_Cache.printInfo(-1)

  print("main ending")
