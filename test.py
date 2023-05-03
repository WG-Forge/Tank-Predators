import logging
import random
import string
from threading import Thread

from Play import Game
from PlayerSession import PlayerSession

def runOneWithUserName():
    logging.basicConfig(level=logging.DEBUG)
    username = input()
    password = ""
    with PlayerSession(username, password) as session:
        data = {}
        data["game"] = "test1"
        data["num_turns"] = 90
        data["num_players"] = 3
        game = Game(session, data)
        game.quitDisplay()
        print(game.isWinner())
        # game.quitDisplay()


def __threadBody(data, i):
    letters = string.ascii_letters
    playerName = ''.join(random.choice(letters) for _ in range(10))  # player name
    with PlayerSession(playerName, "") as session:
        game = Game(session, data)
        game.quitDisplay()
        if game.isWinner():
            winners.append(i)
            pass


def runAutomatically(numPlayers: int, numTurns: int, iteration: int):
    letters = string.ascii_letters
    randomGameName = ''.join(random.choice(letters) for _ in range(10))  # name
    data = {"game": "partija" + str(iteration), "num_turns": numTurns, "num_players": 3}
    threads = []

    for i in range(numPlayers):
        thread = Thread(target=__threadBody, args=(data, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    winners = []
    winByPlayer = [0, 0, 0]
    numGames = 5
    for i in range(numGames):
        runAutomatically(1, 99, i)
    for winner in winners:
        winByPlayer[winner] += 1

    print(winByPlayer)



