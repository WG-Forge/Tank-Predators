from Entities.Entity import Entity
from Tanks.Tank import Tank
from TankManagement.TankManager import TankManager


class Player(Entity):
    __slots__ = ("__tanks", "__capturePoints", "__destructionPoints")

    def __init__(self, idx: int, name: str, tanks: list[str]):
        super().__init__(idx, name)
        self.__capturePoints = 0
        self.__destructionPoints = 0
        self.__tanks = tanks  # list of tank ids

    def getPlayerTanks(self):
        return self.__tanks

    def getCapturePoints(self):
        return self.__capturePoints

    def getDestructionPoints(self):
        return self.__destructionPoints

    def turn(self, capturePoints: int, destructionPoints: int):
        self.__capturePoints = capturePoints
        self.__destructionPoints = destructionPoints

