__author__ = 'MTK07896'

class Request:
  stateRequest = ["INITIAL"       #initial state
                , "WAIT"          #wait for trigger
                , "OUTSTANDING"   #OUTSTANDING
                , "COMMITTED"         #wait for reset
                  ]

  @staticmethod
  def isRequestState(inputState):
    assert (inputState in Request.stateRequest), ("Error: %s is not in stateRequest list" % inputState)
    return inputState

  def resetAttribute(self):
    self.state        = Request.isRequestState("INITIAL")
    self.flushed      = False  #False:non-flushed    True:flushed
    self.ID           = -1     #which entry index
    self.counter      = -1
    self.subblockaddr = -1
    
    self.source_node       = [] #source node
    self.destination_list  = [] #destination node list
    self.duration_list     = [] #duration node list

  def __init__(self):
    self.state        = Request.isRequestState("INITIAL")
    self.flushed      = False  #False:non-flushed    True:flushed
    self.ID           = -1     #which entry index
    self.counter      = -1
    self.subblockaddr = -1
    
    self.source_node       = [] #source node
    self.destination_list  = [] #destination node list
    self.duration_list     = [] #duration node list
    
    self.resetAttribute()