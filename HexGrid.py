# The map is drawn in offset coordinates but the game map is in cube coordinates (https://www.redblobgames.com/grids/hexagons/).
# Corresponding conversions are implemented.

from tkinter import Canvas, Tk


class HexaCanvas(Canvas):
    """A canvas that provides a create-hexagone method"""

    def __init__(self, master, *args, **kwargs):
        Canvas.__init__(self, master, *args, **kwargs)

        self.hexaSize = 20

    def setHexaSize(self, number):
        self.hexaSize = number

    def create_hexagone(self, x, y, fill="blue", label=""):
        """
        Compute coordinates of 6 points relative to a center position.
        Point are numbered following this schema :

        Points in euclidean grid:

                  1   2

                6   .   3

                  5   4

        Returns an objectID (int) of the created hexagone.
        """
        size = self.hexaSize
        deltaY = ((3**0.5) / 2) * size

        points = []
        points.append((x - size / 2, y + deltaY))
        points.append((x + size / 2, y + deltaY))
        points.append((x + size, y))
        points.append((x + size / 2, y - deltaY))
        points.append((x - size / 2, y - deltaY))
        points.append((x - size, y))

        polygonId = self.create_polygon(points, fill=fill, width=1, outline="black")

        coords = self.coords(polygonId)
        centerX = sum(coords[::2]) / len(coords[::2])
        centerY = sum(coords[1::2]) / len(coords[1::2])

        # Add text to the middle of the polygon
        labelId = self.create_text(x, y, text=label, fill='black')
        return polygonId, labelId


class HexagonalGrid(HexaCanvas):
    """A grid whose each cell is hexagonal.
    Has one private field - a dict to keep track of all the cells that are drawn as well their objectIDs
    """

    def __init__(self, master, hexaSize, grid_width, grid_height, *args, **kwargs):
        self.__drawn_cells_dict = {}
        self.__drawn_labels_dict = {}
        width = grid_width * (hexaSize * 3)
        height = (3**0.5 * hexaSize) * (grid_height * 2 - 1) + 10

        HexaCanvas.__init__(
            self,
            master,
            background="white",
            width=width,
            height=height,
            *args,
            **kwargs
        )
        self.setHexaSize(hexaSize)

    def setCell(self, xCell, yCell, *args, **kwargs):
        """Create a content in the cell of coordinates x and y. Could specify options throughout keywords :
        color, fill, color1, color2, color3, color4; color5, color6.

        Returns an objectID (int) of the created hexagone.
        """

        # compute pixel coordinate of the center of the cell:
        size = self.hexaSize
        deltaY = ((3**0.5) / 2) * size

        pix_y = deltaY + 2 * deltaY * yCell
        if xCell % 2 == 1:
            pix_y += deltaY

        pix_x = size + xCell * 1.5 * size + 5
        pix_y += 5

        polygonId, labelId = self.create_hexagone(pix_x, pix_y, *args, **kwargs)
        # Delete the old cell.
        if (xCell, yCell) in self.__drawn_cells_dict:
            self.delete(self.__drawn_cells_dict[(xCell, yCell)])
        if (xCell, yCell) in self.__drawn_labels_dict:
            self.delete(self.__drawn_labels_dict[(xCell, yCell)])
        self.__drawn_cells_dict[(xCell, yCell)] = polygonId
        self.__drawn_labels_dict[(xCell, yCell)] = labelId

    def draw_grid(self, size: int, x: int, y: int):
        """
        Draws the grid. Uses drawn_cells_dict to keep track of already drawn cells.

        :param size: The size of the grid.
        :param x: The x coordinate of a given cell.
        :param y: The y coordinate of a given cell.
        """
        axial_coordinates = offset_to_axial(x, y)
        distance_from_center = axial_distance(
            0, 0, axial_coordinates[0], axial_coordinates[1]
        )
        if (
            distance_from_center == size
            or (x + size - 1, y + size - 1) in self.__drawn_cells_dict
        ):
            return

        self.setCell(x + size - 1, y + size - 1, fill="white", label="")

        self.draw_grid(size, x, y - 1)  # up
        if x & 1 == 0:
            self.draw_grid(size, x + 1, y - 1)  # up right
            self.draw_grid(size, x + 1, y)  # down right
            self.draw_grid(size, x, y + 1)  # down
            self.draw_grid(size, x - 1, y)  # down left
            self.draw_grid(size, x - 1, y - 1)  # up left
        else:
            self.draw_grid(size, x + 1, y)  # up right
            self.draw_grid(size, x + 1, y + 1)  # down right
            self.draw_grid(size, x, y + 1)  # down
            self.draw_grid(size, x - 1, y + 1)  # down left
            self.draw_grid(size, x, y - 1)  # up left


def axial_distance(aq: int, ar: int, bq: int, br: int):
    """
    Calculates distance between two cells (in axial coordinates).

    :param aq: The q coordinate of the first cell.
    :param ar: The r coordinate of the first cell.
    :param bq: The q coordinate of the second cell.
    :param br: The r coordinate of the second cell.

    :return: The distance between the cells.
    """
    return (abs(aq - bq) + abs(aq + ar - bq - br) + abs(ar - br)) / 2


def offset_to_axial(x: int, y: int):
    """
    Converts offset coordinates to axial coordinates.

    :param x: The x coordinate of a cell.
    :param y: The y coordinate of a cell.

    :return: Axial coordinates as a (q, r) tuple.
    """
    q = x
    r = y - (x - (x & 1)) / 2
    return q, r


def cube_to_offset(q: int, r: int):
    """
    Converts cube coordinates to offset coordinates.

    :param q: The q coordinate of a cell.
    :param r: The r coordinate of a cell.

    :return: Offset coordinates as a (x, y) tuple.
    """
    x = q
    y = r + (q - (q & 1)) / 2
    return x, y


if __name__ == "__main__":
    tk = Tk()
    tk.title("HexTanks")
    board_size = 11  # map size

    grid = HexagonalGrid(tk, hexaSize=20, grid_width=board_size, grid_height=board_size)
    grid.grid(row=0, column=0, padx=5, pady=5)

    grid.draw_grid(board_size, 0, 0)

    tk.mainloop()
