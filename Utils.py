def HexToTuple(hex):
    return (hex["x"], hex["y"], hex["z"])


def TupleToHex(hexTuple):
    return {"x": hexTuple[0], "y": hexTuple[1], "z": hexTuple[2]}


# Distance between 2 coordinates given as dictionary
def distance(coord1, coord2) -> int:
    return (abs(coords1['x'] - coords2['x']) + abs(coords1['y'] - coords2['y']) + abs(coords1['z'] - coords2['z'])) // 2
