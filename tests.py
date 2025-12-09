# WRITE YOUR SOLUTION HERE:
import pygame
from itertools import cycle 

# 12/08/25 - Take two, now implements basic tile logic and state storage

class Tile:
    # Each id corresponds to a unique tile type, the rest of the code refers to types as ids
    tile_types = {}

    def __init__(self, position=(0,0), file_dir=None):
        self.id = len(Tile.tile_types) + 1
        Tile.tile_types[self.id] = self

        self.sprite = self.replace_sprite(file_dir) if file_dir else None
        self.position = position

        # This
        self.state = None
        self.logic = None
        # Or
        self.tile_properties = {}   # Id, tile object


    def replace_sprite(self, file_dir):
        # Open image, buffer on a surface here. Could also be a color fill.
        try:
            self.sprite = pygame.image.load(file_dir).convert_alpha()
        except Exception as e:
            print(f"Error loading sprite: {e}")

    def draw(self, surface:pygame.Surface, position:tuple,scale=1):
        print(position)
        if self.sprite:
            surface.blit(self.sprite.scale_by(scale), position)
        else:
            pygame.draw.rect(surface, (0, 255, 0), (position, (scale, scale))) # Placeholder

    # Tile Data Functions ==============================================================================================================
    def move_tile(self, new_position:tuple):
        self.position = new_position


# Game Logic built here ==============================================================================================================
# Includes rules, win conditions, collisions and controls
# Notes: 
#   Do player controls in one unified function
#   Use the coordinate system of the board for movement and collision detection
class BoardRules():
    def __init__(self):
        self.key_mapping = {
            pygame.K_w: self.move_UP,
            pygame.K_s: self.move_DOWN,
            pygame.K_a: self.move_LEFT,
            pygame.K_d: self.move_RIGHT
        }

    # Skeleton implementation of movement functions
    def move_character(self, character:Tile, direction:tuple):
        new_x = character.position[0] + direction[0]
        new_y = character.position[1] + direction[1]
        character.move_tile((new_x, new_y))


class GameBoard(pygame.Surface):
    def __init__(self, dimensions:list, tile_unit:int):
        super().__init__(tuple(x*tile_unit for x in dimensions))
        self.tile_unit = tile_unit
        self.board_matrix = [[0 for _ in range(dimensions[0])] for _ in range(dimensions[1])]
        self.tile_group = {}    # Tracks all active tiles on the board. Struct is {position: tile id}

        # Store tile palettes here
        self.__palette =((0,0,0), (255,255,255)) # TODO: Change to a dictionary

    def get_palette(self):
            return self.__palette

    def set_palette(self, value:tuple):
            self.__palette = value

    # Drawing Functions ==============================================================================================================
    # Look up overloaded methods for python
    # This draws the background tiles checkered style
    def draw_bg(self, palette):
        for y in range(0, len(self.board_matrix[1])):
            for x in range(0, len(self.board_matrix[0])):
                pygame.draw.rect(self, palette[(x+y) % 2], (tuple(a*self.tile_unit for a in (x, y)), (self.tile_unit,)*2))

    # Could be better optimized
    def draw_tiles(self):
        for row_index, row  in enumerate(self.board_matrix):
            for col_index, column in enumerate(row):
                if self.board_matrix[row_index][col_index] != 0:
                    tile = self.board_matrix[row_index][col_index]
                    tile.draw(self, tuple(pos * self.tile_unit for pos in tile.position), self.tile_unit)

    def draw_board(self, window, position:tuple):
        window.fill((0, 0, 0))
        self.draw_bg(self.get_palette())
        self.draw_tiles()
        window.blit(self, position)

    # Board Data Functions ==============================================================================================================

    def add_tile(self, tile:Tile):
        x, y = tile.position
        self.board_matrix[x][y] = tile
        self.tile_group[tile.position] = tile.id

    # Searches for a tile with position
    def search_board(self, position:tuple):
        return self.board_matrix[position[0]][position[1]]
        
    # Searches for all tiles of a certain type on the board
    def get_tiles(self, id):
        return [key for key, value in self.tile_group.items() if value == id]

    # Currently implemented to function for unique and non-unique tiles
    def update_tile(self, id, args:dict, tile=None):
        if tile:
            self.add_tile(tile)
        
        # Might brick something eventually -- Try having these specialized functions for different tile types
        # Id is supposed to be the type of tile something is, not the specific instance on the board
        else:
            # Get coords
            tiles = [self.search_board(tile) for tile in self.get_tiles(id)]
            # If no instances found
            if len(tiles) == 0:
                raise ValueError("No tiles of that type found on the board.")
            # If unique
            elif len(tiles) == 1:
                tile = tiles[0]
                for key, value in args.items():
                    setattr(tile, key, value)

    # The main bulk of the game logic runs here ==============================================================================================================
    def run_game(self):
        pass


pygame.init()
window = pygame.display.set_mode((500, 500))
# palette=((255, 0, 0), (0, 0, 255))
board = GameBoard([20, 20], 20)
board.set_palette(((200, 200, 200), (100, 100, 100)))

window.fill((40, 40, 40))
# board.draw_bg(colors)
# board.draw_board(window, ((window.get_width() - board.get_width()) // 2, (window.get_height() - board.get_height()) // 2))
# pygame.display.flip()



loop = cycle((i for i in range(0,20)))

char = Tile((5, next(loop)))
board.add_tile(char)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    board.draw_board(window, ((window.get_width() - board.get_width()) // 2, (window.get_height() - board.get_height()) // 2))
    

    # holy hack batman
    # fix, too laggy have board updates automatically handle tile updates
    char.move_tile((5, next(loop)))
    # board.update_tile(char.id, char)


    pygame.time.Clock().tick(12)

    
    pygame.display.flip()