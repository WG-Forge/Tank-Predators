# Tank-Predators

#### Team members:
Miloš Kovačević <br/>
Pavle Prodanovic <br/>
Armandas Puidokas <br/>

## How to start the game:
Run Play.py where you can choose username, password, to create/join game as player/observer
Python version recommended: 3.10

## Current version(finished Stage IV):

#### Game Logic:
* Choice between shooting and moving depending on muliple parameters


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
