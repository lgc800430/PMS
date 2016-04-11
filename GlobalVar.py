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
import xml.etree.cElementTree as ET
from xml import *


class GlobalVar:


  global options
  global allcontents_conf
  global allcontents_asm
  global allcontents_trc
  global outputptr
  global topology_ptr

  conf_regex = "\w\_\@\<\>\=\.\*\+\-\,"
  conf_s_regex = conf_regex + "\s"

  options          = None            #for run parameter options
  allcontents_conf = None
  allcontents_asm  = None
  allcontents_trc  = None
  outputptr        = None
  topology_ptr     = None

  @staticmethod
  def parse():
    parser = optparse.OptionParser()

    parser.add_option("--Dflag"         , action="store_true", dest="Dflag")
    parser.add_option("--Sproc"         , action="store_true", dest="Sproc")
    # Input Parser
    parser.add_option("-c","--config"   , action="store"     , dest="input_conf"  , default="MT6296_Program_Memory_Simulator.xml")
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
    parser.add_option("--Trace_idx"     , action="store"     , dest="user_Trace_idx")
    #TCM Config
    parser.add_option("--TCMdelay"      , action="store"     , dest="user_TCMdelay")
    (GlobalVar.options, args) = parser.parse_args()




    if ( os.path.isfile(GlobalVar.options.input_conf) == False):
      print("Error :Config file '%1s' does not exist, please check." % GlobalVar.options.input_conf)
      exit(1)
    # asm file exist check
    if ( os.path.isfile(GlobalVar.options.input_asm) == False):
      print("Error :Assembly file '%1s' does not exist, please check." % GlobalVar.options.input_asm)
      exit(1)

    # input_conf_ptr      = open(GlobalVar.options.input_conf, "r")
    input_asm_ptr       = open(GlobalVar.options.input_asm , "r")


    tree = ET.parse(GlobalVar.options.input_conf)
    GlobalVar.allcontents_conf = tree.getroot()
    GlobalVar.allcontents_asm  = re.sub("//[\w \t\.,_\|]*", "" , input_asm_ptr.read())

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

    input_asm_ptr.close()
    for i_trc in range(len(input_trc_list)):
      input_trc_list_ptr[i_trc].close()

    GlobalVar.outputptr = open(GlobalVar.options.output_re , "w")
    # need
    GlobalVar.outputptr.write(str(sys.argv) + "\n")