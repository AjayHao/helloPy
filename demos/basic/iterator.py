#!/usr/bin/python3

class MyNumbers:
    def __iter__(self):
        self.a = 0
        return self

    def __next__(self):
        if self.a < 20:
            self.a += 1
            return self.a
        else:
            raise StopIteration

myclass = MyNumbers()
myiter = iter(myclass)

for x in myiter:
    print(x)