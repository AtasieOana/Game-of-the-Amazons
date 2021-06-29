# Game of the Amazons
**Project developed in Ptyhon, using Min-Max and Alpha-Beta algorithms**

## Game description

* The game is turn based.
* One player will use white pieces, the other black. 
* The player with white pieces is the one who moves first. 
* The game is played on the chessboard style board game but with 10X10 size.

# Rules and gameplay

A move has two actions:

1. Moving a piece on the board as many positions in a straight line, in a row, column or diagonal (in the style of the chess queen), but only on condition that there are no other pieces on that path (the piece cannot skip other pieces).
2. Launching an "arrow" that can also go in a straight line in a row, column or diagonal but without going through a cell with another piece in it. A X piece is placed in the place where the arrow arrived.

# End of the game
The game ends when one of the players has no moves, in which case the player loses and his opponent wins.

## Demo
![Demo](https://github.com/AtasieOana/Game-of-the-Amazons/blob/main/Demo.gif)

## Features

* The user chooses which symbol to play with.
* Display whose turn it is to move.
* At the end of the game the winner is specified.
* At each move the user can stop the game if he wants.
