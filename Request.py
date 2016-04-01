__author__ = 'MTK07896'

class Request:
  stateRequest = ["WAIT"          #wait for trigger
                , "ACCESS_CACHE"  #counting
                , "EMPTY"         #wait for reset
                , "INITIAL"       #initial state
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

  def __init__(self):
    self.state        = Request.isRequestState("INITIAL")
    self.flushed      = False  #False:non-flushed    True:flushed
    self.ID           = -1     #which entry index
    self.counter      = -1
    self.subblockaddr = -1