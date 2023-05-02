from Tanks.Tank import Tank
from Aliases import jsonDict
import Tanks.Settings as Settings

class SPG(Tank):
    __slots__ = ()

    def __init__(self, tankData: jsonDict) -> None:
        """
        Initializes an SPG (Self-propelled artillery).

        :param tankData: A dictionary containing all the data of the tank entity.
        """
        super().__init__(tankData, Settings.TANKS["SPG"])