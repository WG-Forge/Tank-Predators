class BaseCaptureComponent:
    """
    Component for handling the base capture mechanics of an entity.
    """

    __slots__ = ("__capturing", "__capturedPoints")

    def __init__(self) -> None:
        """
        Initializes a new instance of the BaseCaptureComponent class.
        """
        self.__capturing = False
        self.__capturedPoints = 0

    def enterCaptureZone(self) -> None:
        """
        Marks the entity as entering the capture zone.
        """
        self.__capturing = True

    def exitCaptureZone(self) -> None:
        """
        Marks the entity as exiting the capture zone and resets the captured points to 0.
        """
        self.__capturing = False

    def isInCaptureZone(self) -> bool:
        """
        Returns a boolean indicating if the entity is currently in the capture zone.

        :return: A boolean indicating if the entity is in the capture zone.
        """
        return self.__capturing

    def addCapturedPoints(self, points: int = 1) -> None:
        """
        Adds the specified amount of points to the captured points.

        :param points: An integer representing the number of points to add to the captured points. Defaults to 1.
        """
        self.__capturedPoints += points

    def resetCapturedPoints(self) -> None:
        """
        Resets the captured points to 0.
        """
        self.__capturedPoints = 0

    def getCapturedPoints(self) -> int:
        """
        Returns the current number of captured points.

        :return: An integer representing the current number of captured points.
        """
        return self.__capturedPoints
