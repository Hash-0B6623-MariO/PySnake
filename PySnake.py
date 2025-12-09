'''
Thing for part 14
Started 7/17/25
Deadline 7/27/25

GUIDELINES:
    The game has a sprite the player can move in some way
    The game has some Collectable items and/or Enemies
    The player needs to be set a clear task in the game
    The game contains a counter which tells the player how they are doing in the game
    The source code for the game is divided into functions like in the Sokoban example

    
NOTES:
    Default size should be 25x25
        Scale to display of 500x500
 
'''


import pygame
import math

class GameBoard:
    def __init__(self, area_size:int):
        self.area_size = area_size

class CharacterProp:
    pass



class SnakeGame():
    def __init__(self, area_size:int):
        self.__area_size = area_size
        self.board = []

        # Build area
        for y in range(0, area_size + 1):
            row = []
            for x in range(0, area_size + 1):
                row.append(0)
            self.board.append(row)
        
        self.charPos = self.__loadChar()


    ''' Private methods '''
    # Character loader
    def __loadChar(self):
        middle = math.ceil(self.__area_size / 2)
        self.board[middle][middle] = 1
        return (middle, middle)
    

    ''' User methods '''
    def print_board(self):
        for i in self.board:
            print(i)
        
    def move(self, pos_x:int, pos_y:int):
        placement = (pos_x, pos_y)
        # clear original position

        displacement = self.charPos + placement

        


# Character

board = SnakeGame(10)

board.print_board()
print("\n\n\n")

board.move(2,3)


