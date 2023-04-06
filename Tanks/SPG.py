from Tanks.Tank import Tank

jsonDict = dict[str, any] # alias

class SPG(Tank):
    __slots__ = ()

    def __init__(self, position: jsonDict):
        self._setAttributes(1, 1, 1, 1, position)