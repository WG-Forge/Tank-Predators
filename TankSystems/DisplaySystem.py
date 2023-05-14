from Events.Events import TankAddedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
from HexGrid import *
from threading import Thread
from queue import Queue
import time
import copy


def runDisplay(map: Map, messageQueue: Queue) -> None:
    display = Display(map, messageQueue)
    display.run()


class Display:
    def __init__(self, map: Map, messageQueue: Queue) -> None:
        """
        Initializes a display for the given map, with the ability to receive update messages through a queue.

        :param map: The map to display.
        :param messageQueue: A queue used to receive update messages.
        """
        self.__updateRate = 1 / 60
        self.__messageQueue = messageQueue
        self.__window = Tk()
        self.__map = map
        self.__window.title(map.getName() + " on HexTanks")
        self.__size = map.getSize()
        self.__colors = {
            "Base": "green",
            "Obstacle": "grey0",
            "Catapult": "red",
            "LightRepair": "HotPink3",
            "HardRepair": "HotPink4",
        }

        self.__labels = {
            "Catapult": "CP",
            "LightRepair": "LR",
            "HardRepair": "HR",
        }

        self.__grid = HexagonalGrid(self.__window, hexaSize=20, grid_width=self.__size, grid_height=self.__size)
        self.__grid.grid(row=0, column=0, padx=5, pady=5)

        self.__grid.draw_grid(self.__size, 0, 0)
        self.__initializeMapContent()

    def __initializeMapContent(self) -> None:
        """
        Draws static map objects.
        """
        for position, obj in self.__map:
            self.__setCell(position, self.__colors.get(obj, "white"), self.__labels.get(obj, ""))

    def run(self):
        """
        Starts the display and runs an infinite loop to receive and handle messages.
        """
        while True:
            while True:
                try:
                    messageType, args = self.__messageQueue.get(block=False)

                    if messageType == "update":
                        for update in args[0]:
                            self.__emptyCell(*update)

                        for update in args[1]:
                            self.__setCell(*update)
                    elif messageType == "stop":
                        self.__window.quit()
                        return
                except:
                    break

            self.__window.update_idletasks()
            self.__window.update()
            time.sleep(self.__updateRate)

    def __setCell(self, position: tuple, fillColor: str, label: str = "") -> None:
        """
        Sets the color of the cell at the given position on the map.

        :param position: The position of the cell to change.
        :param fillColor: The color to fill the cell with.
        """
        offsetCoordinates = cube_to_offset(position[0], position[1])
        self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1,
                            fill=fillColor, label=label)

    def __emptyCell(self, position: tuple) -> None:
        """
        Sets the color of the cell at the given position on the map to the default color.

        :param position: The position of the cell to change.
        """
        objectType: str = self.__map.objectAt(position)
        self.__setCell(position, self.__colors.get(objectType, "white"), self.__labels.get(objectType, ""))


class DisplaySystem:
    """
    A system that manages the display.
    """

    def __init__(self, map: Map, eventManager: EventManager) -> None:
        """
        Initializes the DisplaySystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__teamColors = ["orange", "purple", "blue"]
        self.__OwnerColors = {}
        self.__tanks = {}
        self.__turnQueue = [[], []]
        self.__messageQueue = Queue()
        self.__displayThread = Thread(target=runDisplay, args=(map, self.__messageQueue))
        self.__displayThread.start()
        self.__tankLabels = {
            "AT_SPG": "TD",
            "HEAVY_TANK": "HT",
            "LIGHT_TANK": "LT",
            "MEDIUM_TANK": "MT",
            "SPG": "SPG",
        }

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has a health and position components

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        healthComponent = tankEntity.getComponent("health")
        positionComponent = tankEntity.getComponent("position")
        ownerComponent = tankEntity.getComponent("owner")

        if healthComponent and positionComponent and ownerComponent:
            self.__tanks[tankId] = {
                "cHealth": healthComponent.currentHealth,
                "mHealth": healthComponent.maxHealth,
                "healthComponent": healthComponent,
                "position": positionComponent.position,
                "positionComponent": positionComponent,
                "ownerId": ownerComponent.ownerId,
                "tankName": type(tankEntity).__name__
            }
            tankColor = self.__OwnerColors.get(ownerComponent.ownerId)
            tankLabel = self.__tankLabels[type(tankEntity).__name__]
            if not tankColor:
                self.__OwnerColors[ownerComponent.ownerId] = self.__teamColors.pop()
                tankColor = self.__OwnerColors[ownerComponent.ownerId]
            self.__turnQueue[1].append((positionComponent.position, tankColor, tankLabel))

    def turn(self) -> None:
        """
        Performs the turn logic for the system.

        It checks for any changes in tank position and updates the display accordingly. 
        It then puts the updated display data into a message queue for processing by the display thread.
        """
        for tankData in self.__tanks.values():
            positionComponent = tankData["positionComponent"]
            currentPosition = tankData["position"]
            newPosition = positionComponent.position
            if newPosition != currentPosition:
                self.__turnQueue[0].append((currentPosition,))
                self.__turnQueue[1].append((newPosition, self.__OwnerColors[tankData["ownerId"]],
                                            self.__tankLabels[tankData["tankName"]]))
                tankData["position"] = newPosition

        self.__messageQueue.put(("update", copy.deepcopy(self.__turnQueue)))
        self.__turnQueue[0].clear()
        self.__turnQueue[1].clear()

    def quit(self) -> None:
        """
        Stops the display thread.
        """
        self.__messageQueue.put(("stop", []))
        self.__displayThread.join()

    def reset(self) -> None:
        """
        Resets the system to it's initial state.
        """
        for tankData in self.__tanks.values():
            self.__turnQueue[0].append((tankData["position"],))

        self.__messageQueue.put(("update", copy.deepcopy(self.__turnQueue)))
        self.__turnQueue[0].clear()
        self.__turnQueue[1].clear()
        self.__tanks.clear()
