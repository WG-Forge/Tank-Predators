def HexToTuple(hex):
    return (hex["x"], hex["y"], hex["z"])

def TupleToHex(hexTuple):
    return {"x" : hexTuple[0], "y" : hexTuple[1], "z" : hexTuple[2]}