# Tank-Predators

#### Team members:
Miloš Kovačević 
Pavle Prodanovic 
Armandas Puidokas

## How to start the game:
Run PlayerSession.py, enter your name and you will join preordered session. You can change session parameters in PlayerSession.login() method.
Python version recommended: 3.10

## Current version(finished Stage III):

#### Game Logic:
* Random choice between shooting at random opponent in range and random movement on the map

#### Game map interface:
* White color tiles are empty
* Green color tiles are the central base
* Gray color tiles are obstacles
* Other colors are tanks of the teams, each their own color (orange, purple and blue)

#### Game mechanics:
* Tank movement with guaranteed legal moves
* Tank shooting with rule of neutrality and different range of shooting depending on the tank type

#### Server connection:
* ServerConnection.py which works as a Request handler between client(player) and server(wargaming forge) 
