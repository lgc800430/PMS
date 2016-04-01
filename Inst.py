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

#--------------------------------------------
# class CacheTop
#--------------------------------------------
class Inst:

  def __init__(self, input_ID        , input_length  , input_address
                   , input_machine   , input_tag     , input_tag_ID
                   , input_assembly  , input_byteaddr):
    self.ID           = input_ID
    self.length       = input_length
    self.address      = input_address
    self.machine      = input_machine
    self.tag          = input_tag
    self.tag_ID       = input_tag_ID
    self.assembly     = input_assembly
    self.subblockaddr = input_byteaddr
    self.subblocklist = []

  #*************User interface***************
  #*************User end*********************
