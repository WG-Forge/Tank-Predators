from Tanks.Tank import Tank

jsonDict = dict[str, any] # alias

class HeavyTank(Tank):
    __slots__ = ()

    def __init__(self, position: jsonDict):
        self._setAttributes(3, 1, 1, 3, position)