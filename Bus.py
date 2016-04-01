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

from Cache import *
from VLC import *
from PCTracer import *
from Simulator import *
from GlobalVar import GlobalVar


class Bus:

  def __init__(self):
    self.bus_name       = ""     #bus_name  ex: PBUS
    self.bus_port_dist       = {}    #Port dist of this bus
  def construct(self, line_value):
    conf_regex = GlobalVar.conf_regex
    name_in_node  = re.search("([" + conf_regex + "]*)@[" + conf_regex + "]*", line_value).group(1)
    self.bus_name            = name_in_node
    return self.bus_name


  def pre_cycle(self):
    pass

  def cur_cycle(self):
    pass

  def pos_cycle(self):
    pass