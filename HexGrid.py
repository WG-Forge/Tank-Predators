# The map is drawn in offset coordinates but the game map is in cube coordinates (https://www.redblobgames.com/grids/hexagons/).
# Corresponding conversions are implemented.

from tkinter import *
import threading


class HexaCanvas(Canvas):
    """ A canvas that provides a create-hexagone method """

    def __init__(self, master, *args, **kwargs):
        Canvas.__init__(self, master, *args, **kwargs)

        self.hexaSize = 20

    def setHexaSize(self, number):
        self.hexaSize = number

    def create_hexagone(self, x, y, color="black", fill="blue", color1=None, color2=None, color3=None, color4=None,
                        color5=None, color6=None):
        """ 
        Compute coordinates of 6 points relative to a center position.
        Point are numbered following this schema :
    
        Points in euclidean grid:
                     
                  1   2
                        
                6   .   3
                       
                  5   4
                    
    
        Each color is applied to the side that link the vertex with same number to its following.
        Ex : color 1 is applied on side (vertex1, vertex2)
    
        Take care that tkinter ordinate axes is inverted to the standard euclidean ones.
        Point on the screen will be horizontally mirrored.
        Displayed points:
    
                  color1
                  1 _ 2
           color6/     \color2
                6   .   3
           color5\      /color3
                  5 _  4
                  color4
        """
        size = self.hexaSize
        Δy = ((3 ** 0.5) / 2) * size

        point1 = (x - size / 2, y + Δy)
        point2 = (x + size / 2, y + Δy)
        point3 = (x + size, y)
        point4 = (x + size / 2, y - Δy)
        point5 = (x - size / 2, y - Δy)
        point6 = (x - size, y)

        # this setting allow to specify a different color for each side.
        if color1 is None:
            color1 = color
        if color2 is None:
            color2 = color
        if color3 is None:
            color3 = color
        if color4 is None:
            color4 = color
        if color5 is None:
            color5 = color
        if color6 is None:
            color6 = color

        self.create_line(point1, point2, fill=color1, width=2)
        self.create_line(point2, point3, fill=color2, width=2)
        self.create_line(point3, point4, fill=color3, width=2)
        self.create_line(point4, point5, fill=color4, width=2)
        self.create_line(point5, point6, fill=color5, width=2)
        self.create_line(point6, point1, fill=color6, width=2)

        if fill is not None:
            self.create_polygon(point1, point2, point3, point4, point5, point6, fill=fill)


class HexagonalGrid(HexaCanvas):
    """ A grid whose each cell is hexagonal """

    def __init__(self, master, hexaSize, grid_width, grid_height, *args, **kwargs):
        width = grid_width * (hexaSize * 3)
        height = (3 ** 0.5 * hexaSize) * (grid_height * 2 - 1) + 10

        HexaCanvas.__init__(self, master, background='white', width=width, height=height, *args, **kwargs)
        self.setHexaSize(hexaSize)

    def setCell(self, xCell, yCell, *args, **kwargs):
        """ Create a content in the cell of coordinates x and y. Could specify options throughout keywords :
         color, fill, color1, color2, color3, color4; color5, color6"""

        # compute pixel coordinate of the center of the cell:
        size = self.hexaSize
        Δy = ((3 ** 0.5) / 2) * size

        pix_y = Δy + 2 * Δy * yCell
        if xCell % 2 == 1:
            pix_y += Δy

        pix_x = size + xCell * 1.5 * size + 5
        pix_y += 5

        self.create_hexagone(pix_x, pix_y, *args, **kwargs)


def axial_distance(aq: int, ar: int, bq: int, br: int):
    '''
    Calculates distance between two cells (in axial coordinates).

    :param aq: The q coordinate of the first cell.
    :param ar: The r coordinate of the first cell.
    :param bq: The q coordinate of the second cell.
    :param br: The r coordinate of the second cell.

    :return: The distance between the cells.
    '''
    return (abs(aq - bq)
            + abs(aq + ar - bq - br)
            + abs(ar - br)) / 2


def offset_to_axial(x: int, y: int):
    '''
    Converts offset coordinates to axial coordinates.

    :param x: The x coordinate of a cell. 
    :param y: The y coordinate of a cell.

    :return: Axial coordinates as a (q, r) tuple.
    '''
    q = x
    r = y - (x - (x & 1)) / 2
    return (q, r)


def cube_to_offset(q: int, r: int):
    '''
    Converts cube coordinates to offset coordinates.

    :param q: The q coordinate of a cell. 
    :param r: The r coordinate of a cell.

    :return: Offset coordinates as a (x, y) tuple.
    '''
    x = q
    y = r + (q - (q & 1)) / 2
    return (x, y)


# used to keep track of already drawn cells
grid_set = set()


def draw_grid(grid: HexagonalGrid, size: int, x: int, y: int):
    '''
    Draws the grid. Uses grid_set to keep track of already drawn cells.

    :param size: The size of the grid.
    :param x: The x coordinate of a given cell.
    :param y: The y coordinate of a given cell.
    '''
    axial_coordinates = offset_to_axial(x, y)
    distance_from_center = axial_distance(0, 0, axial_coordinates[0], axial_coordinates[1])
    if distance_from_center == size or (x, y) in grid_set:
        return

    cellFill = 'green' if distance_from_center < 2 else 'white'
    grid.setCell(x + size - 1, y + size - 1, fill=cellFill)
    grid_set.add((x, y))

    draw_grid(grid, size, x, y - 1)  # up
    if x & 1 == 0:
        draw_grid(grid, size, x + 1, y - 1)  # up right
        draw_grid(grid, size, x + 1, y)  # down right
        draw_grid(grid, size, x, y + 1)  # down
        draw_grid(grid, size, x - 1, y)  # down left
        draw_grid(grid, size, x - 1, y - 1)  # up left
    else:
        draw_grid(grid, size, x + 1, y)  # up right
        draw_grid(grid, size, x + 1, y + 1)  # down right
        draw_grid(grid, size, x, y + 1)  # down
        draw_grid(grid, size, x - 1, y + 1)  # down left
        draw_grid(grid, size, x, y - 1)  # up left


if __name__ == "__main__":
    tk = Tk()
    tk.title("HexTanks")
    board_size = 11  # map size

    grid = HexagonalGrid(tk, hexaSize=20, grid_width=board_size, grid_height=board_size)
    grid.grid(row=0, column=0, padx=5, pady=5)

    draw_grid(grid, board_size, 0, 0)
    grid_set.clear()

    tk.mainloop()
