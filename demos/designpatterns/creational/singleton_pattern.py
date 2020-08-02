class Singleton:
    def __init__(self):
        pass

    def __new__(cls):
        if not hasattr(Singleton, "__instance"):
            Singleton.__instance = super(Singleton, cls).__new__(cls)
        return Singleton.__instance


obj1 = Singleton()
obj2 = Singleton()
print(obj1, obj2)