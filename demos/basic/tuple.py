#!/usr/bin/python3

# 元祖与列表类似，但元素不可修改
tup1 = ()
tup2 = (1)
tup3 = (2,)
tup4 = (3,4,5,6)
print ("empty tuple: ", tup1)
print ("type tuple: ", type(tup2))
print ("type tuple: ", type(tup3))

# 随机读取
print ("tup4[0]: ", tup4[0])
print ("tup4[-2]: ", tup4[-2])
print ("tup4[1:3]: ", tup4[1:3])
print ("tup4[2:]: ", tup4[2:])


# 操作符
print ("[len()] tup4: ", len(tup4))
print ("tup3 + tup4: ", tup3 + tup4)
print ("tup3 * 2: ", tup3 * 2)
print ("3 in tup4: ", 3 in tup4)
for x in tup4: print(x, end=" ")
print()

# 列表数组转换
list = list(tup4)
list[1] = 100
print(list[1])