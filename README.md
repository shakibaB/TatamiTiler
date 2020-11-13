# TatamiTiler

This repo contains a tatami tile layout calulator.

## Input 

The tiler reads a file with a specific format defining a topdown view of a room. It then outputs all possible configurations of how tatami (according to the rules below) might fit. For now, it doesn't distinguish between rotations and reflections of already existing solutions.

## Rules

The tatami tiling has four rules:
1. Only one half tatami can be used per room.
2. The corners of only three tatami can touch. This can be reduced to two in case of rectangular rooms.
3. No regular grid patterns. (This is an extension of rule 2.)
4. There can not be a line in the room that neatly bisects the tiling in two (this reminds one of harakiri/seppuku).

There is technically another rule: history/good taste forbids a specific tiling for a 3x3 room, which forms the layout of a room in which harakiri/seppuku was performed.
