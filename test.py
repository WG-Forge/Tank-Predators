import logging
import random
from Play import Game
from PlayerSession import PlayerSession

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    username = input()
    password = ""
    with PlayerSession(username, password) as session:
        data = {}
        data["game"] = "Test382"
        data["num_turns"] = 90
        data["num_players"] = 3
        game = Game(session, data)
        print(game.isWinner())
        # game.quitDisplay()