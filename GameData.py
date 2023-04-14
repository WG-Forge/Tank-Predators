from Tanks import Tanks

playerTanks = [None] * len(Tanks.turnOrder)  # list of IDs of player's tanks, initialized at the start of the game
playerID = -1  # player ID given after the login
gameMap = None  # Map class object that is used in GUI

"""
game state dictionary, updated every turn

Contains:
num_players - numbers of players playing this game.
num_turns - number of game turns to be played.
current_turn - number of the current turn.
players - list of players.
observers - list of observers.
current_player_idx - id of player whose turn it is.
finished - whether the game is finished.
vehicles - map of vehicles. Keys are vehicle ids.
attack_matrix - stores which player attacked whom. Used for the neutrality rule check.
winner - id of player who has won the game.
win_points - map with score of each player.
catapult_usage - history of catapult usage. Catapults can be used a limited number of times.
Each vehicle is:

player_id - id of owner.
vehicle_type - type of vehicle.
health - current health of vehicle.
spawn_position - where a vehicle is respawned. Movement to other vehicle spawn points is restricted.
position - current position of vehicle.
capture_points - number of capture points.
shoot_range_bonus - current bonus for shooting range. Added by catapults. Shot resets bonus.
Each win point is:

capture - total number of capture points for a player.
kill - number of kill points for a player.
"""
gameState = {}

"""
Map info dictionary, initialized at the start of the game

Contains:
size - map size.
name - map name in database. Different name means different content.
spawn_points - list of spawn points for each player.
content - coordinates of special hexes.
Each element in the spawn_points list determines vehicle spawn points for a concrete player (by player index).

Each element in the concrete player spawn points map determines a list of spawn points for a concrete vehicle type. 
There are next possible vehicle types: "medium_tank", "light_tank", "heavy_tank", "at_spg", "spg".

And finally each element in the concrete vehicle type spawn points determines a list of coordinates.

Special hex types are:

base - this hex is part of the base.
obstacle - impassable obstacles. Tanks cannot occupy hexes with obstacles or move through them.
light_repair - list of hexes where light repair factories are located. Light repair factories heal "medium_tank".
hard_repair - list of hexes where hard repair factories are located. Hard repair factories heal "heavy_tank" and "at_spg".
catapult - catapult's hexes, catapult improves range of shooting.
"""
mapInfo = {}

