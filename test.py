from collections import OrderedDict

dict = {}
dict["A"] = "a"
dict["B"] = "b"
dict["C"] = "c"

list = []

dict = OrderedDict(sorted(dict.items()))

for key , value in dict.items():
    list.append(value)
    print(key , value)

