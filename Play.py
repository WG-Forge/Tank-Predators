import click
import logging
from PlayerSession import PlayerSession
from Exceptions import AccessDeniedException
from Game import Game
    
def validatePositive(ctx, param, value):
    if value is not None and value <= 0:
        raise click.BadParameter("Value must be a positive number.")
    return value

def deactivatePrompts(ctx, param, value):
    if value:
        for p in ctx.command.params:
            if isinstance(p, click.Option) and p.prompt is not None:
                p.prompt = None
    return value

@click.command()
@click.option('-q/--quiet', default=False, is_eager=True, expose_value=False, callback=deactivatePrompts)
@click.option("--name", prompt="Name")
@click.option("--password", prompt="Password", default="")
@click.option("--gamename", prompt="Enter game name")
@click.option("--numturns", prompt="Enter turn count (max - 100)", type=int, default=45, callback=validatePositive)
@click.option("--numplayers", prompt="Enter player count (1-3)", type=int, default=3, callback=validatePositive)
@click.option("--fullgame", prompt="Full game?", type=click.Choice(["Y", "N"], case_sensitive=False), default="Y")
@click.option("--observer", prompt="Are you an observer?", type=click.Choice(["Y", "N"], case_sensitive=False), default="N")
@click.option("--wait", prompt="Wait for input before returning?", type=click.Choice(["Y", "N"], case_sensitive=False), default="N")
def play(name, password, gamename, numturns, numplayers, fullgame, observer, wait):
        data = {"game": gamename, "num_turns": numturns, "num_players": numplayers, "is_full": fullgame == "Y", "is_observer": observer == "Y"}

        click.echo("Playing...")
        
        with PlayerSession(name, password) as playerSession:
            try:
                game = Game(playerSession, data)
                returnData = game.isWinner()
            except AccessDeniedException as exception:
                click.echo(f"Access denied: {exception.message}")
                return None

            if returnData:
                click.echo("You win!")
            else:
                click.echo("You lose!")
            
            if wait == "Y":
                click.prompt("Enter anything to exit", default="")

            game.quit()
            return returnData
        


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)

    play()
