import sys

try:
    f = open('myfile.txt')
    s = f.readline()
    i = int(s.strip())
except OSError as err:
    print("OS error: {0}".format(err))
except ValueError:
    print("Could not convert data to an integer.")
except (RuntimeError, TypeError, NameError):
    pass
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

with open("myfile.txt") as f:
    for line in f:
        print(line, end="")

# 以上这段代码执行完毕后，就算在处理过程中出问题了，文件 f 总是会关闭。