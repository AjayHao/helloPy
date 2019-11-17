#!/usr/bin/python3

basket = {'apple', 'orange', 'apple', 'pear', 'orange', 'banana'}
print("集合去重效果, set: ", basket)

newset = set(["abcabcde","bcd"])
print("list转set, set:", newset)


set1 = set("abcabcde")
set2 = set("def")
print(set1)
print(set2)
# 集合操作
print(set1 & set2)
print(set1 | set2)
print(set1 - set2)
print(set1 ^ set2)

# add
set2.add("x")
set2.update("yz")
set2.update(["h","i"], ["j","k"])
print(set2)

# remove不存在报错, discard不报错
set2.discard("x")
print(set2)