from Exceptions import AccessDeniedException, InputException
from PlayerSession import PlayerSession
from Game import Game
import logging

def play():
    print("Name: ", end="")
    name = input()

    if not name:
        print("Invalid name!")
        return

    print("Password (leave empty to skip): ", end="")
    password = input()

    with PlayerSession(name, password) as session:
        data = {}
        while True:
            try:
                data.clear()

                print("Joining or creating a game? (J/C): ", end="")
                playType = input()

                if not (playType.upper() == "C" or playType.upper() == "J"):
                    raise InputException("Invalid input!")

                print("Enter game name: ", end="")
                gameName = input()
                if not gameName:
                    raise InputException("Invalid game name!")
                data["game"] = gameName

                if playType.upper() == "C":
                    print("Enter turn count (max - 100): ", end="")
                    turnCount = int(input())
                    if 0 < turnCount < 101:
                        data["num_turns"] = turnCount
                    else:
                        raise InputException("Invalid turn count!")

                    print("Enter player count (1-3): ", end="")
                    playerCount = int(input())
                    if 0 < playerCount < 4:
                        data["num_players"] = playerCount
                    else:
                        raise InputException("Invalid player count!")

                print("Are you an observer? (Y/N): ", end="")
                isObserver = input()
                if isObserver.upper() == "Y":
                    data["is_observer"] = True
                elif not isObserver.upper() == "N":
                    raise InputException("Invalid input!")

                print("Playing...")
                try:
                    game = Game(session, data)

                    if not isObserver.upper() == "Y":
                        if game.isWinner():
                            print("You win!")
                        else:
                            print("You lose!")
                    else:
                        print("Game ended!")
                except AccessDeniedException as exception:
                    print(f"Access denied: {exception.message}")

                print("Play again? (Y/Any): ", end="")
                playAgain = input()
                game.quit()
                if not playAgain.upper() == "Y":
                    return
            except InputException as e:
                print(e.message)
            except ValueError:
                print("Invalid input!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)

    play()
