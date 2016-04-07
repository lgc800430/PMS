import random

base = 0
for i in range(100):
    ran = random.randint(1,8)

    asm = hex(base).replace("x", "").zfill(8)
    print(asm, end="   ")
    base += ran

    str = ""
    for i in range(ran):
      str += hex(random.randint(0, 15)).replace("0x", "")
      str += hex(random.randint(0, 15)).replace("0x", "")
      str += " "

    print("%22s" %str, end="   ")
    print("string", i)