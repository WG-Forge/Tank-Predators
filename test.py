import logging
import random
import string
from threading import Thread
from Game import Game
from PlayerSession import PlayerSession


def runOneWithUserName():
    #logging.basicConfig(level=logging.DEBUG)
    username = "pavle"
    password = ""
    with PlayerSession(username, password) as session:
        data = {
            "game": "abd",
            "num_players": 3,
            "is_observer": False,
            "is_full": True
        }
        game = Game(session, data)
        print(game.isWinner())
        # game.quitDisplay()


def __threadBody(data, i, playerName):
    with PlayerSession(playerName, "") as session:
        game = Game(session, data)
        if game.isWinner():
            winners.append(i)  # remove comment for seeing number of winners
            pass


def runAutomatically(numPlayers: int, numTurns: int, iteration: int):
    letters = string.ascii_letters
    randomGameName = ''.join(random.choice(letters) for _ in range(10))  # name
    data = {"game": randomGameName, "num_turns": numTurns, "num_players":3, "is_full": True}
    threads = []

    for i in range(numPlayers):
        playerName = ''.join(random.choice(letters) for _ in range(10))  # player name
        thread = Thread(target=__threadBody, args=(data, i, playerName))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    winners = []
    winByPlayer = [0, 0, 0]
    numGames = 5
    for i in range(numGames):
        runAutomatically(3, 99, i)
    for winner in winners:
        winByPlayer[winner] += 1

    print(winByPlayer)
"""
Code for automatic running of threads
winners = []
winByPlayer = [0, 0, 0]
numGames = 5
for i in range(numGames):
    runAutomatically(3, 99, i)
for winner in winners:
    winByPlayer[winner] += 1

print(winByPlayer)
"""
