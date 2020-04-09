"""
pandas库是基于NumPy库的一个开源Python库，被广泛用于完成数据快速分析及数据清洗和准备等工作，它的名字来源于“panel data”（面板数据）。pandas库提供非常直观的数据结构及强大的数据管理和数据处理功能，某种程度上可以把pandas库看成是Python版的Excel。
"""

import pandas as pd

# Series类似于通过NumPy库创建的一维数组，不同的是Series对象不仅包含数值，还包含一组索引
s1 = pd.Series(['张三', '李四', '王五'])
print(s1)
print(type(s1))

# DataFrame是一种二维表格数据结构，可以将其看成一个Excel表格。
# 通过列表创建DataFrame
a1 = pd.DataFrame([[1,2,3],[4,5,6],[7,8,9]])
print(a1)

# 指定行列索引名
a2 = pd.DataFrame([[1,2,3],[4,5,6],[7,8,9]], columns=['name', 'age', 'addr'], index=['A', 'B', 'C'])
print(a2)

# 由字典创建
a3 = pd.DataFrame.from_dict({'a' : [1,2,3], 'b' : [2,4,6]})
print(a3)
