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

from Bus import *
from Node import *
from Port import *
from Topology import *

from Cache import *
from TCM import *
from VLC import *
from PCTracer import *
from GlobalVar import *
from NB_sim import *


if __name__ == "__main__":


  # #########################################################################3
  print("GlobalVar.parse start")
  GlobalVar.parse()

  # print(GlobalVar.allcontents_conf)
  # print(GlobalVar.allcontents_asm)
  # print(GlobalVar.allcontents_trc)
  print("GlobalVar.parse end")
  # #########################################################################3
  print("Topology start")


  # Cache.parseConfig()
  # VLC.parseConfig()

  # Cache.checkConfig()
  # VLC.checkConfig()

  GlobalVar.topology_ptr = Topology()
  GlobalVar.topology_ptr.parseConfig()
  GlobalVar.topology_ptr.constructNB()
  print("Topology end")
  # for key, value in GlobalVar.topology_ptr.node_dist.items():
    # print(key, value, value.node_name, value.node_port_dist)
  # print("")
  # for key, value in GlobalVar.topology_ptr.bus_dist.items():
    # print(key, value, value.bus_name, value.bus_port_dist)
  # print("")
  # for key, value in GlobalVar.topology_ptr.port_dist.items():
    # print(key, value, value.port_name, value.port_belong_node_ptr.node_name, value.port_belong_bus_ptr.bus_name)
  #########################################################################

  u_NB_sim = NB_sim()
  u_NB_sim.simulate()

  GlobalVar.outputptr.close()