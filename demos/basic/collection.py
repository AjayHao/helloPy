#!/usr/bin/python3

from collections import deque
from collections import namedtuple
from collections import Counter
from collections import defaultdict
from collections import ChainMap

# 样例数据
playersData = [
    ('HOU', 'James Harden', 'Guard'),
    ('HOU', 'Russell Westbrook', 'Guard'),
    ('LAC', 'Kawhi Leonard', 'Forward')
]

# namedtuple
Player = namedtuple('Player', ['city', 'name', 'position'])
for player in playersData:
    playertuple = Player._make(player)
    print(playertuple.city)
    print('type of player', type(playertuple))

print('type of Player', type(Player))

# deque
queue = deque(["A", "B", "C", "D", "E"])
queue.append("F")
print(queue.popleft())
print(queue.pop())

# Counter
print("统计字符出现的次数", Counter('hello world'))

counterlist = 'hello world hello world hello nihao'.split()
counter = Counter(counterlist)
print("统计单词数", counter)
print("获取指定对象的访问次数, %s 或 %s" % (counter.get('hello'), counter['hello']))

d = Counter('hello world'.split())
print("增加统计数", counter + d)
print("减少统计数", counter - d)

# defaultdict 内置类型工厂用法
fruit = defaultdict(list)
fruit['apple'] = 1
fruit['orange'] = 'a'
fruit['banana']
print("defaultdict 带参构造器，内置类型工厂用法", fruit)

playerdict = defaultdict(list)
for city, name, position in playersData:
    playerdict[city].append((city, name, position))
print("使用defaultdict处理分组", playerdict)

# ChainMap
d1 = {'apple':1,'banana':2}
d2 = {'orange':2,'apple':3,'pike':1}
combined_d = ChainMap(d1,d2)
for k,v in combined_d:
    print(k,v)
