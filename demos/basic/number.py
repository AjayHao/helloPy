#!/usr/bin/python3

'''
int(x) 将x转换为一个整数。
float(x) 将x转换到一个浮点数。
complex(x) 将x转换到一个复数，实数部分为 x，虚数部分为 0。
complex(x, y) 将 x 和 y 转换到一个复数，实数部分为 x，虚数部分为 y。x 和 y 是数字表达式。
'''

print(17 / 3)  # 整数除法返回浮点型
print(17 // 3)  # 整数除法返回向下取整后的结果
print(17 % 3)  # ％操作符返回除法的余数

file = open("D:/GitRepo/helloPy/demos/resources/e.txt", mode="a", encoding='utf8')
for i in range(100000):
    if (i != 0):
        file.write('第{0}次迭代:值为{1}\n'.format(i, pow((1+1/i),i)))

file.close()