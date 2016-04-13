mylist = []
for base in range(100):
    mod_num = 8 - (base%8)
    for i_subblocknum in range(8):
        if(i_subblocknum >= mod_num):
          mylist.append(base + i_subblocknum - 8)
        else:
          mylist.append(base + i_subblocknum)
    print(mylist)
    mylist = []