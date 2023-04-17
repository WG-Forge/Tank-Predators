from Map import Map
from Events.EventManager import EventManager
import Tanks.Settings as TankSettings
from TankManagement.TankManager import TankManager
from TankSystems.TankMovementSystem import TankMovementSystem
from TankSystems.TankShootingSystem import TankShootingSystem
import inspect
import Events.Events as AllEvents

tankData1 = {
    "player_id": 120,
    "vehicle_type": "light_tank",
    "health": 2,
    "spawn_position": {
        "x": 1,
        "y": 0,
        "z": -1
    },
    "position": {
        "x": 0,
        "y": 0,
        "z": 0
    },
    "capture_points": 0
}

tankData2 = {
    "player_id": 130,
    "vehicle_type": "at_spg",
    "health": 1,
    "spawn_position": {
        "x": -5,
        "y": -7,
        "z": 8
    },
    "position": {
        "x": 3,
        "y": 0,
        "z": -3
    },
    "capture_points": 0
}

tankData3 = {
    "player_id": 126,
    "vehicle_type": "at_spg",
    "health": 1,
    "spawn_position": {
        "x": -5,
        "y": -7,
        "z": 8
    },
    "position": {
        "x": 2,
        "y": 0,
        "z": -2
    },
    "capture_points": 0
}

# init map (should use server)
map = Map({
   "size":11,
   "name":"map022",
   "content":{
    "base":[],
    "obstacle":[]
   }})

# init event manager and all events
eventManager = EventManager()
allEvents = inspect.getmembers(AllEvents, inspect.isclass)

for _, cls in allEvents:
    eventManager.registerEvent(cls)

# init tank manager
tankManager = TankManager(eventManager)

# init systems
movementSystem = TankMovementSystem(map, eventManager, max(tank["sp"] for tank in TankSettings.TANKS.values()))
shootingSystem = TankShootingSystem(map, eventManager)

# logic, should be replaced by server later
tankManager.addTank("1", tankData1)
tankManager.addTank("2", tankData2)
tankManager.addTank("3", tankData3)

options = shootingSystem.getShootingOptions("2")
print(options)
print(len(options))
