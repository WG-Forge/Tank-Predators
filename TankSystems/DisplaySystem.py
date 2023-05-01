from Events.Events import TankAddedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
from HexGrid import *
from tkinter import *
from threading import Thread
from queue import Queue
import time
import copy

def runDisplay(map: Map, messageQueue: Queue) -> None:
    display = Display(map, messageQueue)
    display.run()

class Display:
    def __init__(self, map: Map, messageQueue: Queue) -> None:
        '''
        Draws the map in its initial form.
        '''
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

        self.__grid = HexagonalGrid(self.__window, hexaSize=20, grid_width=self.__size, grid_height=self.__size)
        self.__grid.grid(row=0, column=0, padx=5, pady=5)

        draw_grid(self.__grid, self.__size, 0, 0)
        self.__initializeMapContent()

    def __initializeMapContent(self):
        for position, obj in self.__map:
            self.__setCell(position, self.__colors.get(obj, "white"))

    def run(self):
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
                pass

            self.__window.update_idletasks()
            self.__window.update()
            time.sleep(0.1)
       
    def __setCell(self, position: tuple, fillColor: str) -> None:
        '''
        Sets a cell to a given color on the map.

        :param position: Position tuple of the cell to change
        :param fillColor: Color to fill the cell with
        '''
        offsetCoordinates = cube_to_offset(position[0], position[1])
        self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1,
                            fill=fillColor)
        
    def __emptyCell(self, position: tuple) -> None:
        '''
        Sets a cell to default color.

        :param position: Position tuple of the cell to change
        '''
        self.__setCell(position, self.__colors.get(self.__map.objectAt(position), "white"))

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
        self.__turnQueue = [[], []]
        self.__messageQueue = Queue()
        self.__displayThread = Thread(target=runDisplay, args=(map, self.__messageQueue))
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
                "healthComponent": healthComponent,
                "position": positionComponent.position,
                "positionComponent": positionComponent,
                "ownerId": ownerComponent.ownerId
            }
            tankColor = self.__OwnerColors.get(ownerComponent.ownerId)
            if not tankColor:
                self.__OwnerColors[ownerComponent.ownerId] = self.__teamColors.pop()
                tankColor = self.__OwnerColors[ownerComponent.ownerId]
            self.__turnQueue[1].append((positionComponent.position, tankColor))

    def turn(self) -> None:
        for tankData in self.__tanks.values():
            positionComponent = tankData["positionComponent"]
            currentPosition = tankData["position"]
            newPosition = positionComponent.position
            if newPosition != currentPosition:
                self.__turnQueue[0].append((currentPosition,))
                self.__turnQueue[1].append((newPosition, self.__OwnerColors[tankData["ownerId"]]))
                tankData["position"] = newPosition

        self.__messageQueue.put(("update", copy.deepcopy(self.__turnQueue)))
        self.__turnQueue[0].clear()
        self.__turnQueue[1].clear()

    def stop(self) -> None:
        self.__messageQueue.put(("stop", []))
        self.__displayThread.join()

    def reset(self, eventManager: EventManager) -> None:
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)

        for tankData in self.__tanks.values():
            self.__turnQueue[0].append((tankData["position"],))

        self.__tanks.clear()

            

