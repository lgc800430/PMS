__author__ = 'MTK07896'

import re
from GlobalVar import GlobalVar

class PCTracer:

  statePCSim   = ["PCTracer_CORE_STALL"
                , "PCTracer_ASSIGN_PC"
                , "PCTracer_PENDING_BY_VLC"]

  @staticmethod
  def isPCTracer_state(inputState):
    if (inputState in PCTracer.statePCSim):
      return inputState
    else:
      print("Error: %s is not in statePCSim list" % inputState)
      print("PCTracer.statePCSim", PCTracer.statePCSim)
      exit(100)

  def transPCTracerNextState(self, inputState):
    self.PCTracer_nextState = self.isPCTracer_state(inputState)

  def consumePC(self):
    self.PCpointer += 1

    if GlobalVar.options.Sproc == True:
      if(self.PCpointer%10000 == 0):
        print("[%s] PCpointer = %s/%s" %(self.VLC_ptr.node_ptr.node_name, self.PCpointer, len(self.PClist)))
    
    print("[%s] PCpointer = %s/%s" %(self.VLC_ptr.node_ptr.node_name, self.PCpointer, len(self.PClist)))

    if (self.PCpointer == len(self.PClist)):
      return "PCend"
    else:
      return "ongo"

  def nextPC(self):
    (myabstime, myclock, myPC) = self.PClist[self.PCpointer].replace(" ", "").split(",")

    try:
      without_0x_myPC = re.sub("^0x", "", myPC)
    except:
      print("No 0x in Class PCTracer!")
      exit(-1)

    # left most two-bits is for context0-1
    mask_left_two_bit_myPC = re.search("^[\w]{1}([\w]{6})", without_0x_myPC).group(1)

    # self.PCpointer += 1
    return (int(myabstime), int(myclock), int(mask_left_two_bit_myPC, 16))

  def initialize(self, input_trc_idx):
    if(input_trc_idx >= len(GlobalVar.allcontents_trc)):
      print("NB: input_trc_idx >= len(GlobalVar.allcontents_trc)")
      exit(-1)
    #select which trace idx will be run
    self.PClist = GlobalVar.allcontents_trc[input_trc_idx].split("\n")

    if (self.PClist[-1] == ""):
      del self.PClist[-1]

  def __init__(self):
    self.PCpointer = 0
    self.PClist    = []

    self.PCTracer_nextState = 0
    self.PCTracer_state     = 0
    self.PCTracer_counter   = 0
    
    self.VLC_ptr = None

