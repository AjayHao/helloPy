#!/usr/bin/python3

dict = {'Name': 'Runoob', 'Age': 7, 'Class': 'First'}

# 操作符
print ("[len()] dict: ", len(dict))
print ("[str()] dict:", str(dict))
print ("[keys()] dict:", dict.keys())
print ("[values()] dict:", dict.values())
print ("[get()] dict:", dict.get('Sex', 'Male'))
dict.setdefault('Sex', 'Male')
print ("after [setdefault()] dict:", dict)
# 类似extend
dict.update({'City': 'New York'})
print ("[update()] dict:", dict)