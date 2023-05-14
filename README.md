# Tank-Predators

#### Team members:
[Miloš Kovačević](https://github.com/theOriginalFelto) <br/>
[Pavle Prodanovic](https://github.com/PavleProd) <br/>
[Armandas Puidokas](https://github.com/DeviatorZ) <br/>

## Installation:
- Clone the repository or download the source code.
- Make sure you have Python 3.10 or higher and "pip" package manager installed on your system.
- Open a terminal or command prompt.
- Navigate to the directory where source code is located: 
<br/>`cd pathToCode`
- Install the required dependencies: 
<br/>`pip install -r requirements.txt`

## Starting a game:
- Open a terminal or command prompt.
- Navigate to the directory where source code is located: 
<br/>`cd pathToCode`
- Run the script with the following command: 
<br/>`python Play.py --name=<your_name> [--password=<your_password>] --gamename=<game_name> [--numturns=<num_turns>] [--numplayers=<num_players>] [--fullgame] [--observer] [--wait]`
<br/>Replace the placeholders (<your_name>, <your_password>, <game_name>, <num_turns>, <num_players>) with your desired values. The --name and --gamename options are required.
<br/>Optional flags:
    - --password: Specify your password (if needed).
    - --numturns: Set the number of turns (default is 45).
    - --numplayers: Set the number of players (default is 3).
    - --fullgame: Enable full game mode.
    - --observer: Play as an observer.
    - --wait: Wait for user input before exiting.
    
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
