def HexToTuple(hex):
    return (hex["x"], hex["y"], hex["z"])


def TupleToHex(hexTuple):
    return {"x": hexTuple[0], "y": hexTuple[1], "z": hexTuple[2]}


# Distance between 2 coordinates given as dictionary
def distance(coord1, coord2) -> int:
    return (abs(coord1['x'] - coord2['x']) + abs(coord1['y'] - coord2['y']) + abs(coord1['z'] - coord2['z'])) // 2
