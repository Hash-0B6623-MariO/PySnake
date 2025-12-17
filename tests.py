# WRITE YOUR SOLUTION HERE:
import pygame
from itertools import cycle 

# 12/08/25 - Take two, now implements basic tile logic and state storage
# Stuff to add:
# - Json config reading/writing for game settings and board layouts
# - Handling palettes and sprites


# Prio: Final struct for tile and board class

class Tile:
    # Each id corresponds to a unique tile type, the rest of the code refers to types as ids
    # This is hardcoded. Reference for checking
# This now acts as the sort of constructors for tile objects
# Currently not really needed, but could be useful for building more complex tiles later
    tile_types = {
        # 0:0,  # Empty tile
        # 1:0,  # Player tile (tail)
        # 9:0,  # Player tile (head)    
        # 2:0,  # Obstacle tile
        # 3:0  # Collectible tile
        }

    def __init__(self, position=(0,0), id=None, file_dir=None):
        self.id = len(Tile.tile_types) + 1 if id is None else id
        Tile.tile_types[self.id] = self

        self.sprite = self.replace_sprite(file_dir) if file_dir else None
        self.position = position

        # 2 Main rules, is it collision sensitive or a collectible? 0 means neither
        # Scale the game from here on further development
        # self.type = None
        # self.logic = None


    def replace_sprite(self, file_dir):
        # Open image, buffer on a surface here. Could also be a color fill.
        try:
            self.sprite = pygame.image.load(file_dir).convert_alpha()
        except Exception as e:
            print(f"Error loading sprite: {e}")

    def draw(self, surface:pygame.Surface, position:tuple, scale=1):
        if self.sprite:
            surface.blit(self.sprite.scale_by(scale), position)
        else:
            pygame.draw.rect(surface, (0, 255, 0), (position, (scale, scale))) # Placeholder

    # Tile Data Functions ==============================================================================================================
    def move(self, new_position:tuple):
        self.position = new_position

    def __eq__(self, other):
        return self.id == other.id


# Maybe tweak this so it uses composition
class Entity(Tile):
    def char_stats(self):
        pass



class Collectible(Tile):
    def set_properties(self):
        pass

# Proto class for building tiles
class EntityBuilder:
    class Char(Tile):
        def __init__(self, position=(0, 0), file_dir=None, Head=False):
            # Could be a problem for the board class
            id = 9 if Head else 1
            super().__init__(position, id, file_dir)
            self.trailing = None # Sort of a node structure for body segments
            self.direction = (0, 1) # Default moving right
        
        def grow(self, position:tuple, Char):
            self.trailing = Char
        
        def move(self, new_position=None):
            new_position = tuple(x1 + x2 for x1, x2 in (self.position, self.direction))
            if self.trailing:
                self.trailing.move()
            super().move(new_position)

        def draw(self, surface:pygame.Surface, position:tuple, scale=1):
            if self.trailing:
                self.trailing.draw(surface, position, scale)
            super().draw(surface, position, scale)

    
 


class GameBoard(pygame.Surface):
    def __init__(self, dimensions:list, tile_unit:int):
        super().__init__(tuple(x*tile_unit for x in dimensions))
        self.tile_unit = tile_unit
        self.board_matrix = [[0 for _ in range(dimensions[0])] for _ in range(dimensions[1])]
        self.tile_group = {}    # Tracks all active tiles on the board. Struct is {position: tile id}

        # Store tile palettes here
        self.__color =((0,0,0), (255,255,255)) # TODO: Change to a dictionary

    def get_color(self):
            return self.__color

    def set_color(self, value:tuple):
            self.__color = value

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
        self.draw_bg(self.get_color())
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
        return [key for key, value in self.tile_group.items() if int(value) == id]

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

# Game Logic built here ==============================================================================================================
# Includes rules, win conditions, collisions and controls
# Notes: 
#   Attribute syntax in SnakeGame, this just isolates the logic from the rest of the code 
#   Do player controls in one unified function
#   Use the coordinate system of the board for movement and collision detection
class BoardRules():
    def __init__(self, board):
        self.board = board
        self.character = self.find_character()

        self.key_mapping = {
            pygame.K_w: self.move_character((0, -1)),
            pygame.K_s: self.move_character((-1, 0)),
            pygame.K_a: self.move_character((0, 1)),
            pygame.K_d: self.move_character((1, 0))
        }
        
        
        # Here for sad
            # for key, value in attributes.items():
            #     setattr(self, key, value)
    
    def key_event(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in self.board.snake.key_map:
                    self.key_mapping[event.key](self.board.snake)



    # Handling tile data functions ==============================================================================================================
    def find_character(self):
        char = self.board.get_tiles(9)
        return char[0] if char else None

    
    def center_character(self):
        pass

    

    def move_character(self, direction:tuple):
        new_x = self.character.position[0] + direction[0]
        new_y = self.character.position[1] + direction[1]
        self.check_tile((new_x, new_y))
        self.character.move((new_x, new_y))



    # Logic functions ==============================================================================================================
    def check_collisions(self, character:Tile, board:GameBoard):
        pass
  
    def check_tile(self, coords:tuple):
        tile_front = self.board.search_board(coords)



    # Outcomes,results for conditional statements
    def collide_fruit(self, character:Tile, fruit_coords:tuple):
        pass





class SnakeGame:
    def __init__(self):
        # Static configurations
        self.config = {
            "window_scale": 0.4,
            "window_background": (0, 0, 0),
        }

        # Dynamic attributes, does not change during runtime though
        self.attributes = {
            "board_dimensions": [20, 20],
            "board_unit": 20,
            "board_palette": ((200, 200, 200), (100, 100, 100))
        }

        self.set_config()
        self.initialize_objects()
        self.initialize_logic()

        # palette=((255, 0, 0), (0, 0, 255))

    # Utility functions/properties
    def read_config(self):
        pass

    def set_config(self):
        pygame.init()
        c = self.config
        self.window = pygame.display.set_mode(self.update_window(c["window_scale"]))
        self.window.fill(c["window_background"])

    def initialize_objects(self):
        a = self.attributes
        self.board = GameBoard(a["board_dimensions"], a["board_unit"])
        self.board.set_color(a["board_palette"])

        self.character = EntityBuilder.Char(position=(10,10), Head=True)  # Player tile
        self.board.add_tile(self.character)
        print(self.board.get_tiles(9))

        

    def initialize_logic(self):
        # Abreviated for convenience
        self.r = BoardRules(self.board)

    def update_window(self, scale=0.4):
        # Assumes single monitor setup for now
        return tuple(x*scale for x in pygame.display.get_desktop_sizes()[0])

    @property   # Centers the board
    def __center(self):
        self.__center = ((self.window.get_width() - self.board.get_width()) // 2, (self.window.get_height() - self.board.get_height()) // 2)

    def get_center(self):
        return self.__center

    # Skeleton implementation of movement functions

    def run(self):
        loop = cycle((i for i in range(0,20)))
        char = Tile((5, next(loop)))
        self.board.add_tile(char)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            self.board.draw_board(self.window, self.get_center())
            

            # holy hack batman
            # fix, too laggy have board updates automatically handle tile updates
            char.move((5, next(loop)))
            # board.update_tile(char.id, char)


            pygame.time.Clock().tick(12)

            
            pygame.display.flip()


# HELLO?!??!
# board.draw_bg(colors)
# board.draw_board(window, ((window.get_width() - board.get_width()) // 2, (window.get_height() - board.get_height()) // 2))
# pygame.display.flip()

SnakeGame().run()