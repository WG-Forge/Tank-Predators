from Tanks.Tank import Tank

jsonDict = dict[str, any] # alias

class TankDestroyer(Tank):
    __slots__ = ()

    def __init__(self, position: jsonDict):
        self._setAttributes(2, 1, 1, 2, position)