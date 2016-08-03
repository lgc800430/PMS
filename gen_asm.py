import random
import re

base = 0
random.seed(9001) #9001 ASM

asm_list = []

for i in range(1000):
    ran = random.randint(1,8)

    asm = hex(base).replace("x", "").zfill(8)
    # print(asm, end="   ")
    base += ran

    asm_list.append(asm)
    
    str = ""
    for i in range(ran):
      str += hex(random.randint(0, 15)).replace("0x", "")
      str += hex(random.randint(0, 15)).replace("0x", "")
      str += " "

    # print("%22s" %str, end="   ")
    # print("string", i)
    
# print(asm_list)

random.seed(65)

for i in range(5000):
  a = re.search("0([\w]{7})", asm_list[random.randint(0, 999)]).group(1)
  print("         100,        ", i,", ", a)