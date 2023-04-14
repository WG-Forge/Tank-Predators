from Utils import HexToTuple, distance

resultDict = dict[str, any]  # result dictionary type


def neutralityCheck(playerID: int, opponentID: int, gameState: resultDict) -> Bool:
    """
    Checks if we can attack opponent with specified id
    The player whose turn it is can attack this
    opponent only if this opponent attacked him on their previous
    turn or if this opponent was not attacked by the third player on their previous turn.
    :param playerID: id of our bot
    :param opponentID: id of opponent we want to attack
    :param gameState: current turn game state
    :return: True if we can attack an opponent, False otherwise
    """

    # attack_matrix is dictionary where: key is playerID, value is list of IDs of opponents he attacked
    for id, attacks in gameState["attack_matrix"].items():
        if id == playerID:
            continue
        elif id == opponentID:  # if they attacked us we can attack them
            if playerID in attacks:
                return True
        else:  # if third player didn't attack opponent we want to attack, we can attack opponent
            if opponentID not in attacks:
                return True
        return False


def __inRange(vehicleType: string, playerCoord: Dict[str, int], opponentCoord: Dict[str, int]) -> Bool:
    dst = distance(playerCoord, opponentCoord)
    # TODO obstacles lowers firing range
    if vehicleType == "spg":
        if dst == 3:
            return True
    elif vehicleType == "light_tank" or vehicleType == "medium_tank":
        if dst == 2:
            return True
    elif vehicleType == "heavy_tank":
        if 1 <= dst <= 2:
            return True
    elif vehicleType == "tank_destroyer":
        pass  # TODO
    return False


def getTanksInRange(playerID: int, tankID: int, gameState: resultDict) -> Dict[str, Any]:
    """
    Returns information about all tanks in the range of the tank with given id
    :return: Dictionary with tankID as key and with fields:
    position: {x, y, z} -> coordinates,
    health: int -> remaining tank health
    """
    inRange = {}
    tankCoord = gameState["vehicles"][str(tankID)]["position"]  # Dict of given tank coordinates
    tankType = gameState["vehicles"][str(tankID)]["vehicle_type"]  # vehicle type that determines range
    for id, vehicle in gameState["vehicles"].items():
        if vehicle["player_id"] == playerID:  # we don't need information about our own tanks
            continue
        if __inRange(tankType, tankCoord, vehicle["position"]):  # add tank to the result dict
            inRange[id]["position"] = vehicle["position"]
            inRange[id]["health"] = vehicle["health"]
    return inRange
