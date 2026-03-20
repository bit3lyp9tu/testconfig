
def add(x, y, z):
    return x + y + z

def subtract(x, y):
    return x - y

def multiply(x, y, z):
    return x * y * z

def addAll(*args):
    return sum(args)


class AClass:
    def __init__(self, param) -> None:
        self.param = param + 1

    def getParam(self):
        return self.param
