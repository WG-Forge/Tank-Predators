import click
import logging
from PlayerSession import PlayerSession
from Exceptions import AccessDeniedException
from Game import Game


def validatePositive(ctx, param, value):
    if value is not None and value <= 0:
        raise click.BadParameter("Value must be a positive number.")
    return value


@click.command()
@click.option("--name", required=True)
@click.option("--password", default="")
@click.option("--gamename", required=True)
@click.option("--numturns", type=int, default=45, callback=validatePositive)
@click.option("--numplayers", type=int, default=3, callback=validatePositive)
@click.option("--fullgame", is_flag=True)
@click.option("--observer", is_flag=True)
@click.option("--wait", is_flag=True)
def play(name, password, gamename, numturns, numplayers, fullgame, observer, wait):
    data = {"game": gamename, "num_turns": numturns, "num_players": numplayers, "is_full": fullgame,
            "is_observer": observer}

    click.echo("Playing...")

    with PlayerSession(name, password) as playerSession:
        try:
            game = Game(playerSession, data)
        except AccessDeniedException as exception:
            click.echo(f"Access denied: {exception.message}")
            return None

        if not observer:
            returnData = game.isWinner()
            if returnData:
                click.echo("You win!")
            else:
                click.echo("You lose!")
        else:
            returnData = None
            click.echo("Game over!")

        if wait:
            click.prompt("Enter anything to exit", default="")

        game.quit()
        return returnData


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)

    play()
