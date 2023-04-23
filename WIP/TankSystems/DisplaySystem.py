from Events.Events import TankAddedEvent
from Events.Events import TankShotEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
from Aliases import positionTuple
from HexGrid import *
from tkinter import *
from threading import Thread
from queue import Queue

class Display:
    def __init__(self, map: Map, messageQueue: Queue) -> None:
        '''
        Draws the map in its initial form.
        '''
        self.__window = Tk()
        self.__window.title(map.getName() + " on HexTanks")
        self.__size = map.getSize()
        self.__colors = {
            "Base": "green",
            "Obstacle": "gray"
        }
        self.__grid = HexagonalGrid(self.__window, hexaSize=20, grid_width=self.__size, grid_height=self.__size)
        self.__grid.grid(row=0, column=0, padx=5, pady=5)

        draw_grid(self.__grid, self.__size, 0, 0)
        grid_set.clear()

        # draw the map
        for position, obj in map:
            self.__setCell(position, self.__colors.get(obj, "white"))

        while True:
            try:
                messageType, *args = messageQueue.get(block=False)
                if messageType == "setCell":
                    self.__setCell(*args)
            except Exception:
                pass

            self.__window.update_idletasks()
            self.__window.update()
        
    def __setCell(self, position: tuple, fillColor: str) -> None:
        '''
        Sets a cell to a given color on the map.

        :param position: Position tuple of the cell to change
        :param fillColor: Color to fill the cell with
        '''
        offsetCoordinates = cube_to_offset(position[0], position[1])
        self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1,
                            fill=fillColor)

class DisplaySystem:
    """
    A system that manages the health of tanks.
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
        self.__messageQueue = Queue()
        self.__displayThread = Thread(target=Display, args=(map, self.__messageQueue))
        self.__displayThread.start()

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
                "position": positionComponent.position,
                "ownerId": ownerComponent.ownerId
            }
            tankColor = self.__OwnerColors.get(ownerComponent.ownerId)
            if not tankColor:
                self.__OwnerColors[ownerComponent.ownerId] = self.__teamColors.pop()
                tankColor = self.__OwnerColors[ownerComponent.ownerId]

            self.__messageQueue.put(("setCell", positionComponent.position, tankColor))
