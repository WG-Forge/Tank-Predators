from Tanks.Tank import Tank

jsonDict = dict[str, any] # alias

class MediumTank(Tank):
    __slots__ = ()

    def __init__(self, position: jsonDict):
        self._setAttributes(2, 2, 1, 2, position)