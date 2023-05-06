from Entities.Entity import Entity


class Player(Entity):
    __slots__ = ("__tanks", "__capturePoints", "__destructionPoints")

    def __init__(self, idx: int, name: str, tanks: list[int]):
        super().__init__(idx, name)
        self.__capturePoints = 0
        self.__destructionPoints = 0
        self.__tanks = tanks  # list of tank ids

    def getPlayerTanks(self):
        return self.__tanks
