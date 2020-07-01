#!/usr/bin/python3
import re
import os

c = "Hello*Python\\With|chars\\/:*?\"<>|"
result = re.sub(r'\\|/|:|\*|\?|"|<|>|\|', '', c)
# 字符串格式化
print (result)

# 串提取
line = "【【洛书融智乾兴私募证券投资基】20191231开放估值材料"
matchObj = re.match( r'【(.*)】.*', line, re.M|re.I)
if matchObj:
    print ("matchObj.group(1) : ", matchObj.group(1))
else:
    print ("No match!!")

# 串提取-非贪心
# 串提取
line = "aaa--bbbbbb-cccccc"
matchObj = re.match( r'(\w*-).*', line, re.M|re.I)
if matchObj:
    print ("matchObj.group(1) : ", matchObj.group(1)[0:-1])
else:
    print ("No match!!")

