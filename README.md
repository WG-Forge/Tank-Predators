# Tank-Predators

## How to start the game:
Run PlayerSession.py, which will create one player thread that will do random movement with game map shown
Player needs to add its name and the session will be started on preordered game name

## Current version(Stage II):

#### Game map interface:
* White color squares are empty
* Green color squares are the central base
* Other colors are tanks of the teams, each their own color

#### Game logic:
* Random tank movement with guaranteed legal moves
* Information about all tanks classes, movement depending on the class type

#### Server connection:
* ServerConnection.py which works as a Request handler between client(player) and server(wargaming forge) 
