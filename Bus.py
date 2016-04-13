from GlobalVar import *
from Transaction import *
__author__ = 'MTK07896'

TOPPEST = 0

class Bus:

  def __init__(self):
    self.bus_name       = ""     #bus_name  ex: PBUS
    self.bus_port_dist  = {}    #Port dist of this bus
    ### bus_port_arbitor ###
    self.bus_port_arbitor  = {}
    
    self.bus_delay    = -1
    self.multi_access = -1

  def construct(self, root):
    self.bus_name     = root.attrib["name"]
    self.bus_delay    = int(root.attrib["bus_delay"])
    self.multi_access = int(root.attrib["multi_access"])

  def initial_cycle(self):
    ### bus_port_arbitor construct###
    for key, value in self.bus_port_dist.items():
      self.bus_port_arbitor[value.port_belong_node_ptr.node_name] = []
    
  def pre_cycle(self):
    for key, value in self.bus_port_dist.items():
      if( len(value.port_NB_trans) > 0):
        ### there should be only one item in port_NB_trans of each port ###
        # assert (len(value.port_NB_trans) == 1), (key, value.port_name, "len(value.port_NB_trans) == ", len(value.port_NB_trans))
        # if(len(value.port_NB_trans) > 1):
          # print(key, value.port_name, "len(value.port_NB_trans) == ", len(value.port_NB_trans))
        ### get the transaction ###
        cur_transaction = value.port_NB_trans[TOPPEST]
        assert (cur_transaction.state == Transaction.isTransactionState("INITIAL")), ("cur_transaction.state == INITIAL")
        del value.port_NB_trans[TOPPEST]
        cur_transaction.duration_list.append(self)
        ### set all transaction in bus_port_arbitor counter to exact value (bus_delay) ###
        cur_transaction.counter = self.bus_delay
        cur_transaction.state = Transaction.isTransactionState("WAIT")
        assert (not cur_transaction.destination_list == None ), ("not cur_transaction.destination_list == None")
        ### classify the transaction to right destination in bus_port_arbitor ###
        for i_destination in cur_transaction.destination_list:
          self.bus_port_arbitor[i_destination.node_name].append(cur_transaction)

  def cur_cycle(self):
    for key, value in self.bus_port_arbitor.items():
      ### count down the counter for each transaction in bus_port_arbitor ###
      for i_trans in value:
        if(i_trans.state == Transaction.isTransactionState("WAIT") and i_trans.counter > 0 ):
          i_trans.counter -= 1

  def pos_cycle(self):
    for key, value in self.bus_port_arbitor.items():
      if( len(value) > 0):
        ### find the transaction which state is "WAIT" & counter is 0, (depende on self.multi_access)###
        access_num = self.multi_access
        cur_transaction = None
        for i_trans in value:
          if(i_trans.state == Transaction.isTransactionState("WAIT") and i_trans.counter == 0):
            cur_transaction = i_trans
            cur_transaction.state = Transaction.isTransactionState("INITIAL")
            del value[value.index(cur_transaction)]
            access_num -= 1
          ### (depende on self.multi_access)### ###
          if(access_num == 0):
            break
        ### handle the toppest one transaction which state is "WAIT" & counter is 0 only ###
        if(not cur_transaction == None):
          self.bus_port_dist[key + "_" + self.bus_name].port_BN_trans.append(cur_transaction)
