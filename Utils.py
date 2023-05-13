import itertools


def hexToTuple(hex):
    return (hex["x"], hex["y"], hex["z"])


def tupleToHex(hexTuple):
    return {"x": hexTuple[0], "y": hexTuple[1], "z": hexTuple[2]}


def pathingOffsets(maxDistance: int) -> list[dict[tuple[int, int, int], set[tuple[int, int, int]]]]:
    """
    Calculates all reachable positions for a given maximum travel distance using a hexagonal grid system.
    
    :maxDistance): The maximum distance that a target can travel. This value must be a non-negative integer.
    
    :return: pathingOffsets: A list of dictionaries representing all possible positions a target can move to in a given number of steps (i.e., distance). 
    The keys of each dictionary are the reachable positions, represented as a tuple of (x, y, z) coordinates, where x, y, and z are integers. 
    The values of each dictionary are sets containing the positions that can reach the key position in exactly the same number of steps as the dictionary index. 
    The first dictionary in the list contains only the starting position, with itself as the only element of its set.
    """
    # Get offsets for all 6 directions
    hexPermutations = list(itertools.permutations([-1, 0, 1], 3))

    # Get the maximum travel distance of any tank.
    startingPosition = (0, 0, 0)

    # Keep track of which positions have already been visited.
    visited = set()
    visited.add(startingPosition)

    # The 'pathingOffsets' list will store dictionaries representing reachable positions at each distance.
    pathingOffsets = []
    pathingOffsets.append({startingPosition: {startingPosition}})

    # Perform breadth-first search to find all possible movement options
    for currentDistance in range(1, maxDistance + 1): \
            # Create a new dictionary for the current distance
        pathingOffsets.append({})
        # Iterate over each position in the previous distance to obtain current distance offsets.
        for position in pathingOffsets[currentDistance - 1]:
            for permutation in hexPermutations:
                nextPosition = tuple(x + y for x, y in zip(position, permutation))
                # If the next position has not been visited before (is not reachable by another source),
                # add it to the current distance and add the position as its source.
                if not nextPosition in visited:
                    pathingOffsets[currentDistance][nextPosition] = {position}
                    visited.add(nextPosition)
                # If the next position has already been added to the current distance (is already reachable by another source but at the same distance),
                # add the position to the existing set of source positions.
                elif nextPosition in pathingOffsets[currentDistance]:
                    pathingOffsets[currentDistance][nextPosition].add(position)

    return pathingOffsets
