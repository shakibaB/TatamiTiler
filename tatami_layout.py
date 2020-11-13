from typing import Tuple, List
from copy import deepcopy
from room import Room, Orientation, Tatami

class TatamiLayoutCalculator:
    """
    Given a room, this class will attempt to find a tatami layout for it. This
    one only works from bottom left to top right, but in the future it might
    start in the middle and work in a spiral outwards, just for kicks.
    The rules of laying down tatami are as follows:
        1) Only one half tatami can be used.
        2) The corners of only three tatamis can touch. (in purely rectangular rooms,
           this can be taken as that only the corners of two tatami can touch,
           however, if non-rectangular rooms we might have a corner touching
           three tatami corners.)
        3) (From 2) No regular grid patterns. Unless it's at a wake.
        4) No line that divides the layout in half. This resembles harakiri.
    """
    def __init__(self, room: Room) -> None:
        self.solutions = []
        self.calculate_layout(self.next_position((0, 0), room), 0, room, False)

    def calculate_layout(self, pos: Tuple[int, int], tatami_index: int, tmpRoom: Room, half_used: bool) -> None:
        """
        Recursively calculates the layout for a given room, filling the solutions
        member array with all possible solutions. It doesn't check whether the
        solutions themselves are rotation or reflection invariant.
        """
        #print(tmpRoom)
        #room.print_corners()
        #print(pos)
        #stop condition:
        if tmpRoom.is_full() and self.is_solution(tmpRoom):
            if room not in self.solutions:
                self.solutions.append(deepcopy(tmpRoom))

        #try horizontal:
        if tmpRoom.can_place_tatami(pos, (Orientation.west, tatami_index)):
            tmpRoom.place_tatami(pos, (Orientation.west, tatami_index))
            self.calculate_layout(self.next_position(pos, tmpRoom), tatami_index+1, tmpRoom, half_used)
            tmpRoom.remove_tatami(pos)

        #try vertical:
        if tmpRoom.can_place_tatami(pos, (Orientation.south, tatami_index)):
            tmpRoom.place_tatami(pos, (Orientation.south, tatami_index))
            self.calculate_layout(self.next_position(pos, tmpRoom), tatami_index+1, tmpRoom, half_used)
            tmpRoom.remove_tatami(pos)

        #try half:
        if not half_used and tmpRoom.can_place_tatami(pos, (Orientation.half, tatami_index)):
            half_used = True
            tmpRoom.place_tatami(pos, (Orientation.half, tatami_index))
            self.calculate_layout(self.next_position(pos, tmpRoom), tatami_index+1, tmpRoom, half_used)
            tmpRoom.remove_tatami(pos)
            half_used = False

    def next_position(self, pos: Tuple[int, int], room: Room) -> Tuple[int, int]:
        """
        Obtain the next position in the room to try, given the current (now probably
        occupied position). Works from the corner in the bottom left to the corner
        in the upper right. Can try to define one that goes in a spiral outwards, too.
        """
        #do it stupidly: just walk from the bottom left to the top right, and return
        #the position of the first empty spot:
        seen_pos: bool = False
        for k in range(0, room.width+room.height+1):
            for j in range(k+1):
                i = k-j
                if i < room.height and j < room.width:
                    if pos == (i, j):
                        seen_pos = True
                    if seen_pos and room.is_empty_spot((i, j)):
                        return (i, j)

        #otherwise return nonexisting value:
        return (-1, -1)

    def is_solution(self, room: Room) -> bool:
        """
        Checks the last rules if the given room is full and returns true if
        the given room also adheres to these.
        """
        if room.is_full():
            return True

        return False

    half_used: bool
    solutions: List[Room]

if __name__ == "__main__":
    room = Room(3, 3)
    room.read_from_file("example_room6.txt")
    print(room)
    #room.print_corners()

    layout = TatamiLayoutCalculator(room)
    for solution in layout.solutions:
        print(solution)
