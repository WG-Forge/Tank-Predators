from Map import Map
from Events.EventManager import EventManager
import Tanks.Settings as TankSettings
from TankManagement.TankManager import TankManager
from TankSystems.TankMovementSystem import TankMovementSystem
from TankSystems.TankShootingSystem import TankShootingSystem
from TankSystems.TankHealthSystem import TankHealthSystem
from TankSystems.DisplaySystem import DisplaySystem
from TankSystems.TankRespawnSystem import TankRespawnSystem
import random
import inspect
import Events.Events as AllEvents
import time
from PlayerSession import PlayerSession
from Utils import HexToTuple
from Utils import TupleToHex
from ServerConnection import Action

# init event manager and all events
eventManager = EventManager()
allEvents = inspect.getmembers(AllEvents, inspect.isclass)

for _, cls in allEvents:
    eventManager.registerEvent(cls)

# init tank manager
tankManager = TankManager(eventManager)

turnOrder = ["spg", "light_tank", "heavy_tank", "medium_tank", "at_spg"]

print("Name: ", end="")
name = input()
with PlayerSession(name) as session:
    playerID = session.login()
    print(playerID)   

    gameState = session.getGameState()
    playerTanks = [None] * 5
    for tankId, tankData in gameState["vehicles"].items():
        if tankData["player_id"] == playerID:
            playerTanks[turnOrder.index(tankData["vehicle_type"])] = tankId

    # Prepare arguments for Map creation.
    mapInfo = session.getMapInfo()
    map = Map(mapInfo)
    # init systems
    movementSystem = TankMovementSystem(map, eventManager, max(tank["sp"] for tank in TankSettings.TANKS.values()))
    shootingSystem = TankShootingSystem(map, eventManager)
    healthSystem = TankHealthSystem(eventManager)
    displaySystem = DisplaySystem(map, eventManager)
    respawnSystem = TankRespawnSystem(eventManager)

    while not gameState["finished"]:
        # add missing tanks
        for tankId, tankData in gameState["vehicles"].items():
            tankId = str(tankId)
            if not tankManager.hasTank(tankId):
                tankManager.addTank(tankId, tankData)

        # perform other player actions
        gameActions = session.getGameActions()
        for action in gameActions["actions"]:
            if action["action_type"] == Action.MOVE and action["player_id"] != playerID:
                actionData = action["data"]
                print(f"Moving: {actionData['vehicle_id']}, {HexToTuple(actionData['target'])}")
                movementSystem.move(str(actionData["vehicle_id"]), HexToTuple(actionData["target"]))
            elif action["action_type"] == Action.SHOOT and action["player_id"] != playerID:
                actionData = action["data"]
                print(f"Shooting: {actionData['vehicle_id']}, {HexToTuple(actionData['target'])}")
                shootingSystem.shoot(str(actionData["vehicle_id"]), HexToTuple(actionData["target"]))

        respawnSystem.turn()
        displaySystem.turn()

        if gameState["current_player_idx"] == playerID:  # our turn
            for tankId in playerTanks:
                # perform actions
                options = shootingSystem.getShootingOptions(tankId)
                if len(options) > 0:
                    randomChoice = random.randint(0, len(options) - 1)
                    print(f"Shooting: {tankId}, {options[randomChoice][0]}")
                    session.shoot({"vehicle_id": int(tankId), "target": TupleToHex(options[randomChoice][0])})
                    shootingSystem.shoot(tankId, options[randomChoice][0])
                    continue

                options = movementSystem.getMovementOptions(tankId)
                if len(options) > 0:
                    randomChoice = random.randint(0, len(options) - 1)
                    print(f"Moving: {tankId}, {options[randomChoice]}")
                    session.move({"vehicle_id": int(tankId), "target": TupleToHex(options[randomChoice])})
                    movementSystem.move(tankId, options[randomChoice])

        respawnSystem.turn()
        displaySystem.turn()
        session.nextTurn()
        gameState = session.getGameState()

    # perform other player actions
    gameActions = session.getGameActions()
    for action in gameActions["actions"]:
        if action["action_type"] == Action.MOVE and action["player_id"] != playerID:
            actionData = action["data"]
            movementSystem.move(str(actionData["vehicle_id"]), HexToTuple(actionData["target"]))
        elif action["action_type"] == Action.SHOOT and action["player_id"] != playerID:
            actionData = action["data"]
            shootingSystem.shoot(str(actionData["vehicle_id"]), HexToTuple(actionData["target"]))
    respawnSystem.turn()
    displaySystem.turn()

    print(gameState["winner"])
    session.logout()

    #displaySystem.stop()