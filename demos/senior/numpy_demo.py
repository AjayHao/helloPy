import numpy as np

a = [1, 2, 3, 4]
b = np.array([1, 2, 3, 4])

c = a * 2
d = b * 2

# 列表和数组差异
print(c)
print(d)

# 包含3个服从标准正态分布的数组
a1 = np.random.randn(3)

# 将0～11这12个整数转换成3行4列的二维数组
a2 = np.arange(12).reshape(3,4)
a3 = np.random.randint(0,10, (4,4))
