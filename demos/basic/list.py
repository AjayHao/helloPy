#!/usr/bin/python3

# 元祖
list1 = ['Google', 'Runoob', 1997, 2000]
list2 = [1, 2, 3, 4, 5, 6, 7, 8]

# 随机读取
print ("list1[0]: ", list1[0])
print ("list1[-2]: ", list1[-2])
print ("list2[1:3]: ", list2[1:3])
print ("list2[2:]: ", list2[2:])

# 更新
list1[2] = '123'
print ("[update] list1: ", list1)

# 删除
del list1[2]
print ("[del] list1: ", list1)

# 操作符
print ("[len()] list1: ", len(list1))
print ("list1 + list2: ", list1 + list2)
print ("list1 * 2: ", list1 * 2)
print ("2000 in list1: ", 2000 in list1)
for x in list1: print(x, end=" ")
print()

print(1 not in list2)

# 列表数组转换
tuple = tuple(list2)
print(tuple)