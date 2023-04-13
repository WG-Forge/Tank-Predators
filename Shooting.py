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
