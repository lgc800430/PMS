from GlobalVar import *
from Transaction import *
from collections import OrderedDict
__author__ = 'MTK07896'

TOPPEST = 0

class Bus:

  def __init__(self):
    self.bus_name       = ""     #bus_name  ex: PBUS
    self.bus_port_dist  = {}    #Port dist of this bus
    ### bus_port_arbitor ###
    self.bus_port_arbitor  = {}

    self.bus_delay      = 0
    self.multi_access   = 0
    self.OutsdngTCM     = 0 # 0:infinite 
    self.OngoTransTCM   = 0 # must < self.out_standing

  def construct(self, root):
    self.bus_name     = root.attrib["name"]
    if "bus_delay" in root.attrib:
      self.bus_delay    = int(root.attrib["bus_delay"])
    if "multi_access" in root.attrib:
      self.multi_access = int(root.attrib["multi_access"])
    if "OutsdngTCM" in root.attrib:
      self.OutsdngTCM = int(root.attrib["OutsdngTCM"])
      
      
  def initial_cycle(self):
    ### bus_port_arbitor construct###
    for key, value in self.bus_port_dist.items():
      self.bus_port_arbitor[value.port_belong_node_ptr.node_name] = []

    self.bus_port_arbitor = OrderedDict(sorted(self.bus_port_arbitor.items()))
      
      
  def pre_cycle(self):
    for key, value in self.bus_port_dist.items():
      if( len(value.port_NB_trans) > 0):
          
  
          
        ### there should be only one item in port_NB_trans of each port ###
        ### get the transaction ###
        cur_transaction = value.port_NB_trans[TOPPEST]
        assert (cur_transaction.state == Transaction.isTransactionState("INITIAL")), ("cur_transaction.state == INITIAL")
        
        # print("key", key)
        
        # print("self.bus_name", self.bus_name, "self.OutsdngTCM", self.OutsdngTCM, "key", key, "self.OngoTransTCM", self.OngoTransTCM, "cur_transaction.last", cur_transaction.last)
        
        if(key == "EMI_AXI" and self.OutsdngTCM > 0):
          if(cur_transaction.last == 1):
            self.OngoTransTCM -= 1

        
        del value.port_NB_trans[TOPPEST]
        cur_transaction.duration_list.append(self)
        ### set all transaction in bus_port_arbitor counter to exact value (bus_delay) ###
        cur_transaction.counter = self.bus_delay
        cur_transaction.state = Transaction.isTransactionState("WAIT")
        assert (not cur_transaction.destination_list == None ), ("not cur_transaction.destination_list == None")
        ### classify the transaction to right destination in bus_port_arbitor ###
        for i_destination in cur_transaction.destination_list:
          try:
            self.bus_port_arbitor[i_destination.node_name].append(cur_transaction)
          except:
            print(i_destination.node_name)
            print(self.bus_port_arbitor)
            exit(-1)

  def cur_cycle(self):
    for key, value in self.bus_port_arbitor.items():
      ### count down the counter for each transaction in bus_port_arbitor ###
      for i_trans in value:
        if(i_trans.state == Transaction.isTransactionState("WAIT") and i_trans.counter > 0 ):
          i_trans.counter -= 1

  def pos_cycle(self):
    # print("pos_cycle")
    for key, value in self.bus_port_arbitor.items():
      # print(key, len(value))
      if( len(value) > 0):
        
        ### find the transaction which state is "WAIT" & counter is 0, (depende on self.multi_access)###
        access_num = self.multi_access
        cur_transaction = None
        
        del_cur_transaction = []
        for i_trans in value:
          if(i_trans.state == Transaction.isTransactionState("WAIT") and i_trans.counter == 0):
          
            if(key == "EMI" and self.OutsdngTCM > 0):
              if(self.OngoTransTCM < self.OutsdngTCM):
                self.OngoTransTCM += 1
                cur_transaction = i_trans
                cur_transaction.state = Transaction.isTransactionState("INITIAL")
                del_cur_transaction.append(cur_transaction)
                access_num -= 1
                ### handle the toppest one transaction which state is "WAIT" & counter is 0 only ###
                assert(not cur_transaction == None)
                self.bus_port_dist[key + "_" + self.bus_name].port_BN_trans.append(cur_transaction)              
            else:
              cur_transaction = i_trans
              cur_transaction.state = Transaction.isTransactionState("INITIAL")
              del_cur_transaction.append(cur_transaction)
              access_num -= 1
              ### handle the toppest one transaction which state is "WAIT" & counter is 0 only ###
              assert(not cur_transaction == None)
              self.bus_port_dist[key + "_" + self.bus_name].port_BN_trans.append(cur_transaction)
            
            
          ### (depende on self.multi_access)### ###
          if(access_num <= 0):
            break
        for i_del in del_cur_transaction:
          value.remove(i_del)





