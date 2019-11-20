#!/usr/bin/python3

import sys


# 生成器函数 - 斐波那契
def fibonacci(n):
    a, b, counter = 0, 1, 0
    while True:
        if counter > n:
            return
        yield a
        a, b = b, a + b
        counter += 1


# f 是一个迭代器，由生成器返回生成
f = fibonacci(10)
while True:
    try:
        print(next(f), end=" ")
    except StopIteration:
        break

print("")

f2 = fibonacci(10)
for a in f2:
    print(a, end=" ")
