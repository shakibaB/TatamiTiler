from typing import List, Tuple, Optional, Dict
from enum import Enum

#the orientation states where another half tatami can connect,
#or whether it is a true half tatami
class Orientation(Enum):
    north = 0
    west = 1
    south = 2
    east = 3
    half = 4
    empty = 5 #a tatami can be placed, but is not currently
    blocked = 6 #a tatami cannot be placed here

#a (half) tatami is defined as a tuple of an enum and an integer
Tatami = Tuple[Orientation, int]

def key(tatami: Tatami) -> int:
    """
    Returns the tatami index of a tatami.
    """
    return tatami[1]

def orientation(tatami: Tatami) -> Orientation:
    """
    Returns the orientation of a tatami.
    """
    return tatami[0]

def add_offset(pos: Tuple[int, int], offset: Tuple[int, int]) -> Tuple[int, int]:
    """
    Adds an offset to the given position.
    """
    return (pos[0]+offset[0], pos[1]+offset[1])

def other_side(orientation: Orientation) -> Orientation:
    """
    Returns the orientation of the other half of a tatami.
    """
    if orientation == Orientation.north:
        return Orientation.south
    if orientation == Orientation.east:
        return Orientation.west
    if orientation == Orientation.south:
        return Orientation.north
    if orientation == Orientation.west:
        return Orientation.east
    if orientation == Orientation.half:
        return Orientation.half

def other_offset(orientation: Orientation) -> Tuple[int, int]:
    """
    Returns the position of the other half of a tatami.
    """
    if orientation == Orientation.north:
        return (-1, 0)
    if orientation == Orientation.east:
        return (0, -1)
    if orientation == Orientation.south:
        return (1, 0)
    if orientation == Orientation.west:
        return (0, 1)
    if orientation == Orientation.half:
        return (0, 0)

class Room:
    """
    This class has all necessary methods to run a tatami layout calculator.
    """
    def __init__(self, height: int, width: int) -> None:
        self.width = width
        self.height = height
        self.tiles = [[(Orientation.empty, -1) for j in range(width)] for i in range(height)]
        self.corners = [[0 for j in range(width+1)] for i in range(height+1)]

    def read_from_file(self, filename: str) -> None:
        """
        Reads a room from a file. Haven't tested whether reading in tatami goes
        as planned.
        """
        with open(filename) as f:
            lines = [line.rstrip('\n').split(' ') for line in f]
        self.height, self.width = int(lines[0][0]), int(lines[0][1])
        self.tiles = [[(Orientation.empty, -1) for j in range(self.width)] for i in range(self.height)]
        self.corners = [[0 for j in range(self.width+1)] for i in range(self.height+1)]
        del lines[0]
        lines.reverse()
        tatami_index = 0
        for i in range(self.height):
            for j in range(self.width):
                if lines[i][j] == 'b' or lines[i][j] == '#':
                    self.tiles[i][j] = (Orientation.blocked, -1)
                if lines[i][j] == '.':
                    self.tiles[i][j] = (Orientation.empty, -1)
                if lines[i][j] == 'n':
                    self.place_tatami((i, j), (Orientation.north, tatami_index))
                    tatami_index += 1
                if lines[i][j] == 'e':
                    self.place_tatami((i, j), (Orientation.east, tatami_index))
                    tatami_index += 1
                if lines[i][j] == 's':
                    self.place_tatami((i, j), (Orientation.south, tatami_index))
                    tatami_index += 1
                if lines[i][j] == 'w':
                    self.place_tatami((i, j), (Orientation.west, tatami_index))
                    tatami_index += 1
                if lines[i][j] == 'h':
                    self.place_tatami((i, j), (Orientation.half, tatami_index))
                    tatami_index += 1


    def __getitem__(self, pos: Tuple[int, int]) -> Tatami:
        if pos[1] >= self.width or pos[0] >= self.height:
            raise IndexError
        return self.tiles[pos[0]][pos[1]]

    def __setitem__(self, pos: Tuple[int, int], tatami: Tatami) -> None:
        if pos[1] >= self.width or pos[0] >= self.height:
            raise IndexError
        self.tiles[pos[0]][pos[1]] = tatami

    def __delitem__(self, pos: Tuple[int, int]) -> None:
        if pos[1] >= self.width or pos[0] >= self.height:
            raise IndexError
        self.tiles[pos[0]][pos[1]] = (Orientation.empty, -1)

    def __str__(self) -> str:
        output = ""
        for i in range(self.height-1, -1, -1):
            output += " "
            for j in range(self.width):
                if self.orientation_at((i, j)) == Orientation.north:
                    #output += "n "
                    output += "\u2293 "
                elif self.orientation_at((i, j)) == Orientation.east:
                    #output += "e "
                    output += "\u2290 "
                elif self.orientation_at((i, j)) == Orientation.south:
                    #output += "s "
                    output += "\u2294 "
                elif self.orientation_at((i, j)) == Orientation.west:
                    #output += "w "
                    output += "\u228F "
                elif self.orientation_at((i, j)) == Orientation.half:
                    #output += "h "
                    output += "\u22A1 "
                elif self.orientation_at((i, j)) == Orientation.empty:
                    output += ". "
                elif self.orientation_at((i, j)) == Orientation.blocked:
                    output += "# "
            output += "\n"

        return output

    def __eq__(self, other: 'Room') -> bool:
        """
        Checks whether two rooms are equal in terms of tatami orientations.
        """
        if not isinstance(other, Room):
            return False

        if self.width != other.width or self.height != other.height:
            return False

        for i in range(self.height):
            for j in range(self.width):
                if self.tiles[i][j][0] != other.tiles[i][j][0]:
                    return False

        return True

    def is_empty(self) -> bool:
        """
        Checks whether this rooms is empty.
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.tiles[i][j][0] != Orientation.empty:
                    return False

        return True

    def is_empty_spot(self, pos: Tuple[int, int]) -> bool:
        """
        Checks whether the given position has no tatami placed on it.
        """
        if self.orientation_at(pos) != Orientation.empty:
            return False

        return True

    def is_full(self) -> bool:
        """
        Checks whether this rooms is full.
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.is_empty_spot((i, j)):
                    return False

        return True

    def orientation_at(self, pos: Tuple[int, int], offset: Tuple[int, int]=(0, 0)) -> Orientation:
        """
        Returns the orientation of a tatami at pos, with a possible offset.
        """
        return self.tiles[pos[0]+offset[0]][pos[1]+offset[1]][0]

    def print_corners(self) -> None:
        """
        Output the corner array.
        """
        output = ""
        for i in range(self.height, -1, -1):
            for j in range(self.width+1):
                output += str(self.corners[i][j]) + " "
            output += "\n"
        print(output)

    def can_place_tatami(self, pos: Tuple[int, int], tatami: Tatami) -> bool:
        """
        Checks whether a given tatami can be placed at the given position, and
        also checks the associated place, depending on the type of tatami
        """
        if not self.is_empty_spot(pos):
            return False

        if orientation(tatami) == Orientation.south:
            if pos[0]+1 >= self.height or not self.is_empty_spot(add_offset(pos, (1, 0))):
                return False

        elif orientation(tatami) == Orientation.east:
            if pos[1]-1 < 0 or not self.is_empty_spot(add_offset(pos, (0, -1))):
                return False

        elif orientation(tatami) == Orientation.west:
            if pos[1]+1 >= self.width or not self.is_empty_spot(add_offset(pos, (0, 1))):
                return False

        elif orientation(tatami) == Orientation.north:
            if pos[0]-1 < 0 or not self.is_empty_spot(add_offset(pos, (-1, 0))):
                return False

        #now check whether the corners of three tatami are together, if so return false:
        corners: Dict[str, int] = self.number_of_corners(pos)
        if orientation(tatami) == Orientation.north and (corners["nw"] > 2 or corners["ne"] > 2):
            return False
        if orientation(tatami) == Orientation.south and (corners["sw"] > 2 or corners["se"] > 2):
            return False
        if orientation(tatami) == Orientation.west  and (corners["sw"] > 2 or corners["nw"] > 2):
            return False
        if orientation(tatami) == Orientation.east  and (corners["se"] > 2 or corners["ne"] > 2):
            return False
        if orientation(tatami) == Orientation.half  and (corners["se"] > 2 or corners["ne"] > 2 or corners["nw"] > 2 or corners["sw"] > 2):
            return False

        if not orientation(tatami) == Orientation.half:
            other_corners: Dict[str, int] = self.number_of_corners(add_offset(pos, other_offset(orientation(tatami))))
            if other_side(orientation(tatami)) == Orientation.north and (other_corners["nw"] > 2 or other_corners["ne"] > 2):
                return False
            if other_side(orientation(tatami)) == Orientation.south and (other_corners["sw"] > 2 or other_corners["se"] > 2):
                return False
            if other_side(orientation(tatami)) == Orientation.west  and (other_corners["nw"] > 2 or other_corners["sw"] > 2):
                return False
            if other_side(orientation(tatami)) == Orientation.east  and (other_corners["ne"] > 2 or other_corners["se"] > 2):
                return False

        return True

    def number_of_corners(self, pos: Tuple[int, int]) -> Dict[str, int]:
        corners: Dict[str, int] = {
            "nw": self.corners[pos[0]+1][pos[1]],
            "ne": self.corners[pos[0]+1][pos[1]+1],
            "sw": self.corners[pos[0]][pos[1]],
            "se": self.corners[pos[0]][pos[1]+1]
        }

        return corners

    def place_tatami(self, pos: Tuple[int, int], tatami: Tatami) -> None:
        self[pos] = tatami
        if orientation(tatami) == Orientation.south:
            self.corners[pos[0]][pos[1]] += 1
            self.corners[pos[0]][pos[1]+1] += 1
            other_pos = add_offset(pos, (1, 0))
            self[other_pos] = (Orientation.north, tatami[1])
            self.corners[other_pos[0]+1][other_pos[1]+1] += 1
            self.corners[other_pos[0]+1][other_pos[1]] += 1
        if orientation(tatami) == Orientation.west:
            self.corners[pos[0]][pos[1]] += 1
            self.corners[pos[0]+1][pos[1]] += 1
            other_pos = add_offset(pos, (0, 1))
            self[other_pos] = (Orientation.east, tatami[1])
            self.corners[other_pos[0]][other_pos[1]+1] += 1
            self.corners[other_pos[0]+1][other_pos[1]+1] += 1
        if orientation(tatami) == Orientation.north:
            self.corners[pos[0]+1][pos[1]+1] += 1
            self.corners[pos[0]+1][pos[1]] += 1
            other_pos = add_offset(pos, (-1, 0))
            self[other_pos] = (Orientation.south, tatami[1])
            self.corners[other_pos[0]][other_pos[1]] += 1
            self.corners[other_pos[0]][other_pos[1]+1] += 1
        if orientation(tatami) == Orientation.east:
            self.corners[pos[0]][pos[1]+1] += 1
            self.corners[pos[0]+1][pos[1]+1] += 1
            other_pos = add_offset(pos, (0, -1))
            self[other_pos] = (Orientation.west, tatami[1])
            self.corners[other_pos[0]][other_pos[1]] += 1
            self.corners[other_pos[0]+1][other_pos[1]] += 1
        if orientation(tatami) == Orientation.half:
            self.corners[pos[0]][pos[1]] += 1
            self.corners[pos[0]][pos[1]+1] += 1
            self.corners[pos[0]+1][pos[1]+1] += 1
            self.corners[pos[0]+1][pos[1]] += 1

    def remove_tatami(self, pos: Tuple[int, int]) -> None:
        tatami = self[pos]
        if orientation(tatami) == Orientation.empty:
            return

        self[pos] = (Orientation.empty, -1)
        if orientation(tatami) == Orientation.south:
            self.corners[pos[0]][pos[1]] -= 1
            self.corners[pos[0]][pos[1]+1] -= 1
            other_pos = add_offset(pos, (1, 0))
            self[other_pos] = (Orientation.empty, -1)
            self.corners[other_pos[0]+1][other_pos[1]+1] -= 1
            self.corners[other_pos[0]+1][other_pos[1]] -= 1
        if orientation(tatami) == Orientation.west:
            self.corners[pos[0]][pos[1]] -= 1
            self.corners[pos[0]+1][pos[1]] -= 1
            other_pos = add_offset(pos, (0, 1))
            self[other_pos] = (Orientation.empty, -1)
            self.corners[other_pos[0]][other_pos[1]+1] -= 1
            self.corners[other_pos[0]+1][other_pos[1]+1] -= 1
        if orientation(tatami) == Orientation.north:
            self.corners[pos[0]+1][pos[1]+1] -= 1
            self.corners[pos[0]+1][pos[1]] -= 1
            other_pos = add_offset(pos, (-1, 0))
            self[other_pos] = (Orientation.empty, -1)
            self.corners[other_pos[0]][other_pos[1]] -= 1
            self.corners[other_pos[0]][other_pos[1]+1] -= 1
        if orientation(tatami) == Orientation.east:
            self.corners[pos[0]][pos[1]+1] -= 1
            self.corners[pos[0]+1][pos[1]+1] -= 1
            other_pos = add_offset(pos, (0, -1))
            self[other_pos] = (Orientation.empty, -1)
            self.corners[other_pos[0]][other_pos[1]] -= 1
            self.corners[other_pos[0]+1][other_pos[1]] -= 1
        if orientation(tatami) == Orientation.half:
            self.corners[pos[0]][pos[1]] -= 1
            self.corners[pos[0]][pos[1]+1] -= 1
            self.corners[pos[0]+1][pos[1]+1] -= 1
            self.corners[pos[0]+1][pos[1]] -= 1

    width: int
    height: int
    tiles: List[List[Tatami]]
    corners: List[List[int]]

#if __name__ == "__main__":
#    room = Room(4, 7)
#    print(room)
#    room.print_corners()
#    #print(room.is_empty())
#    #print(room.is_full())
#
#    tatami = (Orientation.half, 1)
#    #pos = (1,1)
#    for i in range(room.height):
#        for j in range(room.width):
#            print(f"{(i, j)}: {room.can_place_tatami((i, j), tatami)}")
#            #print(room.can_place_tatami((i, j), tatami))
#            if room.can_place_tatami((i, j), tatami):
#                print(room.number_of_corners((i, j)))
#                room.place_tatami((i, j), tatami)
#                print(room)
#                room.print_corners()
#    #room.remove_tatami(pos)
#    #room.remove_tatami(pos)
#    print(room)
#    room.print_corners()
#
#    print(len(room.corners))
#    print(len(room.corners[0]))
#    print(room.number_of_corners((3, 6)))
#    room.read_from_file("example_room2.txt")
#    print(room)
