jsonDict = dict[str, any] # alias

class Tanks():
   # Players can only use tanks in a strict order
   turnOrder = ["spg", "light_tank", "heavy_tank", "medium_tank", "at_spg"]

   # Stats of each tank
   allTanks = {
      "spg" : {
         "hp" : 1,
         "sp" : 1,
         "damage" : 1,
         "destructionPoints" : 1,
      },
      "light_tank" : {
         "hp" : 1,
         "sp" : 3,
         "damage" : 1,
         "destructionPoints" : 1,
      },
      "heavy_tank" : {
         "hp" : 3,
         "sp" : 1,
         "damage" : 1,
         "destructionPoints" : 3,
      },
      "medium_tank" : {
         "hp" : 2,
         "sp" : 2,
         "damage" : 1,
         "destructionPoints" : 2,
      },
      "at_spg" : {
         "hp" : 2,
         "sp" : 1,
         "damage" : 1,
         "destructionPoints" : 2,
      },
   }