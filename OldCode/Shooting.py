from Utils import distance, HexToTuple
import GameData

resultDict = dict[str, any]  # result dictionary type


def neutralityCheck(opponentID: int) -> bool:
    """
    Checks if we can attack opponent with specified id
    The player whose turn it is can attack this
    opponent only if this opponent attacked him on their previous
    turn or if this opponent was not attacked by the third player on their previous turn.
    :param opponentID: id of opponent we want to attack
    :return: True if we can attack an opponent, False otherwise
    """

    # attack_matrix is dictionary where: key is playerID, value is list of IDs of opponents he attacked
    for pid, attacks in GameData.gameState["attack_matrix"].items():
        if pid == GameData.playerID:
            continue
        elif pid == opponentID:  # if they attacked us we can attack them
            if GameData.playerID in attacks:
                return True
        else:  # if third player didn't attack opponent we want to attack, we can attack opponent
            if opponentID not in attacks:
                return True
        return False


def __inRangeTankDestroyer(playerCoord: dict[str, int], opponentCoord: dict[str, int], dst: int) -> tuple[bool, dict[str, int]]:
    """
    Checks if tank destroyer can attack opponent at given coordinates
    Conditions:
    AT_SPG cannot shoot through obstacles
    AT_SPG can attack 3 tiles if opponent is in the perpendicular(90 degrees) from the player, otherwise 1 tile
    AT_SPG can hit multiple opponents that are in the range of attack
    :param playerCoord: AT_SPG (tank destroyer) coordinates
    :param opponentCoord: opponent tank coordinates
    :return: True if attack is possible, and coordinates in which AT_SPG should shoot, False, empty dict otherwise
    """
    if dst == 1:
        return True, opponentCoord
    differentCoordinate = 'x'
    numOfSameCoordinates = 0
    if playerCoord['x'] == opponentCoord['x']:
        numOfSameCoordinates += 1
    if playerCoord['y'] == opponentCoord['y']:
        numOfSameCoordinates += 1
    else:
        differentCoordinate = 'y'
    if playerCoord['z'] == opponentCoord['z']:
        numOfSameCoordinates += 1
    else:
        differentCoordinate = 'z'

    if numOfSameCoordinates != 2:  # not at 90 degrees
        return False, dict()
    tileInfo = GameData.gameMap.__map
    for i in range(3): # we iterate from player to tank and check if obstacle is there
        playerCoord[differentCoordinate] += 1
        # obstacle is between player and opponent so we cannot shoot
        if tileInfo[HexToTuple(playerCoord)] == "Obstacle":
            return False, dict()
    playerCoord[differentCoordinate] -= 2  # 2 because we return adjacent tile that will be direction of shooting

    return True, playerCoord


def __inRange(vehicleType: str, playerCoord: dict[str, int], opponentCoord: dict[str, int]) -> tuple[bool, dict[str, int]]:
    """
    Checks for the given player vehicle type whether opponent tanks is in range
    Note: AT_SPG cannot shoot through obstacles, other tanks can
    :return: True, coordinates for shooting if tank is in range; false, empty dict otherwise
    """
    dst = distance(playerCoord, opponentCoord)
    if vehicleType == "spg":
        if dst == 3:
            return True, opponentCoord
    elif vehicleType == "light_tank" or vehicleType == "medium_tank":
        if dst == 2:
            return True, opponentCoord
    elif vehicleType == "heavy_tank":
        if 1 <= dst <= 2:
            return True, opponentCoord
    elif vehicleType == "tank_destroyer":
        canShoot, coord = __inRangeTankDestroyer(playerCoord, opponentCoord, dst)
        if canShoot:
            return True, coord
    return False, dict()


def getTanksInRange(tankID: int) -> dict[str, any]:
    """
    Returns information about all tanks in the range of the tank with given id.
    Note: For AT_SPG it returns tile neighboring the AT-SPG's position hex that represents direction of shooting.
    :param tankID: id of the tank
    :return: Dictionary with tankID as key and with fields:
    position: {x, y, z} -> coordinates,
    health: int -> remaining tank health
    """
    inRange = {}
    tankCoord = GameData.gameState["vehicles"][str(tankID)]["position"]  # Dict of given tank coordinates
    tankType = GameData.gameState["vehicles"][str(tankID)]["vehicle_type"]  # vehicle type that determines range
    for pid, vehicle in GameData.gameState["vehicles"].items():
        if vehicle["player_id"] == GameData.playerID:  # we don't need information about our own tanks
            continue
        canShoot, coord = __inRange(tankType, tankCoord, vehicle["position"])
        if canShoot:  # add tank to the result dict
            inRange[pid] = {}
            inRange[pid]["position"] = coord
            inRange[pid]["health"] = vehicle["health"]
    return inRange
