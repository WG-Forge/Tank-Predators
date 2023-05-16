def hexToTuple(hex):
    return (hex["x"], hex["y"], hex["z"])


def tupleToHex(hexTuple):
    return {"x": hexTuple[0], "y": hexTuple[1], "z": hexTuple[2]}
