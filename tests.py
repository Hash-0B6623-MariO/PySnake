# WRITE YOUR SOLUTION HERE:
import pygame
from itertools import cycle
import random 

# 12/08/25 - Take two, now implements basic tile logic and state storage
# Stuff to add:
# - Json config reading/writing for game settings and board layouts
# - Handling palettes and sprites
# - Optimization for movement, constant checks for moving a character
#       * Currently nested to one check but could be done with dicts
# - Update spawner
# Augur


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
        # 2:0  # Fruit tile
        }

    def __init__(self, position=(0,0), personality=None, color=(255, 0, 0), file_dir=None):
        self.personality = len(Tile.tile_types) + 1 if personality is None else personality
        Tile.tile_types[self.personality] = self

        self.sprite = self.replace_sprite(file_dir) if file_dir else None
        # Alternate when not using sprites
        self.color = color
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

    # Helper function for drawing
    def scale_to_board(self, tile_unit):
        return tuple(pos * tile_unit for pos in self.position)

    def draw(self, surface:pygame.Surface, scale=1):
        if self.sprite:
            surface.blit(self.sprite.scale_by(scale), self.position)
        else:
            pygame.draw.rect(surface, self.color, (self.scale_to_board(scale), (scale, scale))) # Placeholder

    # Tile Data Functions ==============================================================================================================
    def move(self, new_position:tuple):
        self.position = new_position

    # Standard way of calling
    def __hash__(self):
        return hash(self.personality)
    
    def __index__(self):
        return self.personality
    
    # An accident happened here
    def __int__(self):
        return self.personality

    def __eq__(self, other):
        if isinstance(other, int):
            return self.personality == other
        if isinstance(other, Tile):
            return self.personality == other.personality
        return NotImplemented

# Spawner for this
class Collectibles():
    # Thinking about developing (or borrowing) an algorithm for making fruit spawns always be possible to eat
    # Could also have an in-game factor that determines how "possible" a fruit spawn should be
    #       Look up Flood Fill or BFS (Breadth-First Search) algorithm
    class Fruit(Tile):
        # Tier refers to point/length multiplier
        # Value refers to progrssion
        def __init__(self, position=(0, 0), tier=1, value=1, file_dir=None):
            self.tier = tier
            self.value = value
            super().__init__(position=position, personality=2, color=(255, 0, 0), file_dir=file_dir)
    
    # Do change this, maybe instead pass the entire map
    @classmethod
    def fruit_rand(cls, bounds):
        pos = random.choice(bounds)
        return cls.Fruit(pos)
            
# Proto class for building tiles
class Entity:
    class Char(Tile):
        def __init__(self, position=(0, 0), direction=(1, 0), file_dir=None, Head=False):
            # Could be a problem for the board class
            super().__init__(position, 9 if Head else 1, color=(0,255,0), file_dir=file_dir)
            self.front = None
            self.back = None # Sort of a node structure for body segments
            self.direction = direction # Default moving right
        
        # NOT Unique to the head tile only
        def get_front(self):
            return tuple(x1 + x2 for x1, x2 in zip(self.position, self.direction))

        def change_direction(self, direction):
            self.direction = direction
            
        def grow(self, new_pos):
            head_new = Entity.Char(position=new_pos, Head=True)
            self.personality = 1
            head_new.back = self
            return head_new 

        # TODO: NEW_POS here to deal with the calls from boardrules
        def move(self, new_position=None):
            new_position = self.get_front()
            if self.back:
                self.back.move(self.position)
            super().move(new_position)

        def draw(self, surface:pygame.Surface, scale=1):
            if self.back:
                self.back.draw(surface, scale)
            super().draw(surface, scale)
    
        # Utility functions
        def get_tail(self):
            return self if self.back == None else self.back.get_tail()
        

class GameBoard(pygame.Surface):
    def __init__(self, dimensions:list, tile_unit:int):
        super().__init__(tuple(x*tile_unit for x in dimensions))
        self.tile_unit = tile_unit
        self.bounds = dimensions
        self.map = self.create_map()
        self.instances = []    # Tracks all instances tiles on the board.

        # Store tile palettes here
        self.__color =((0,0,0), (255,255,255)) # TODO: Change to a dictionary

    def get_color(self):
            return self.__color

    def set_color(self, value:tuple):
            self.__color = value

    # Mapping +---------------------------------------------------
    def create_map(self):
        x, y = self.bounds
        return [[0 for _ in range(x)] for _ in range(y)]
    
    def get_available(self):
        x, y = self.bounds
        return list(set([(y2,x2) for y2 in range(0,x) for x2 in range(0,y)]) - set(self.get_occupied()))

    def get_occupied(self):
        return tuple(tile.position for tile in self.instances)
    
    def get_center(self):
        x, y = self.bounds
        return ((len(x)-1)//2, (len(y)-1)//2)

    # Drawing Functions ==============================================================================================================
    # This draws the background tiles checkered style
    def draw_bg(self, palette):
        for y in range(0, len(self.map[1])):
            for x in range(0, len(self.map[0])):
                pygame.draw.rect(self, palette[(x+y) % 2], (tuple(a*self.tile_unit for a in (x, y)), (self.tile_unit,)*2))

    # Could be better optimized
    def draw_tiles(self):
        for tile in self.instances:
            tile.draw(self, self.tile_unit)

    def draw_board(self, window, position:tuple):
        window.fill((0, 0, 0))
        self.draw_bg(self.get_color())
        self.draw_tiles()
        window.blit(self, position)

    # Board Data Functions ==============================================================================================================
    def add_tile(self, tile:Tile):
        x, y = tile.position
        self.instances.append(tile)
        self.map[x][y] = tile

    def clear_tile(self, position):
        x, y = position
        tile = self.get_tile(position)
        self.instances.remove(tile)
        self.map[x][y] = 0

    # Searches for a tile with their position
    def get_tile(self, position:tuple):
        x, y = position
        return self.map[x][y]
        
    # Searches for all tiles of a certain type on the board, returns position
    def search_board(self, personality):
        return [tile for tile in self.instances if tile == personality]

    def update_tile(self, position, tile=None):
        pass  

    # Zero utility at the moment, made to give attributes to all tiles of a type
    def update_tiles(self, personality, args):
        # Get coords
        tiles = [self.get_tile(tile) for tile in self.search_board(personality)]
        # If no instances found
        if len(tiles) == 0:
            raise ValueError("No tiles of that type found on the board.")
        # If unique
        elif len(tiles) == 1:
            tile = tiles[0]
            for key, value in args.items():
                setattr(tile, key, value)

    # Refreshes the map when positions are changed on the objects themselves
    def refresh_map(self):
        for tile in self.instances:
            self.clear_tile(tile.position)
            self.add_tile(tile)
        
# Game Logic built here ==============================================================================================================
# Includes rules, win conditions, collisions and controls
# Notes: 
#   Attribute syntax in SnakeGame, this just isolates the logic from the rest of the code 
#   Do player controls in one unified function
#   Use the coordinate system of the board for movement and collision detection
class BoardRules():
    def __init__(self, board:GameBoard):
        self.board = board
        self.character = self.find_character()

        self.key_mapping = {
            pygame.K_w: (0, -1),
            pygame.K_s: (0, 1),
            pygame.K_a: (-1, 0),
            pygame.K_d: (1, 0)
        }

        # Here for referencing any effects of specific tile types
        self.on_collide = {
            0:self.move_character,
            1:'asdasd',
            2:self.collide_fruit
        }
    
    def key_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_mapping:
                    self.character.change_direction(self.key_mapping[event.key])

    # Handling tile data functions ==============================================================================================================    
    def find_character(self) -> Entity.Char:
        return self.board.search_board(9)[0]
    
    def center_character(self):
        pass

    # Logic functions ==============================================================================================================
    def check_collisions(self):
        front = self.board.get_tile(self.character.get_front())
        self.on_collide[front](front)

    # On Collide Functions ------------------------------------------------------------------------------------
    def collide_fruit(self, tile:Collectibles.Fruit):
        pos = tile.position
        self.board.clear_tile(pos)
        # Inevitable source of headaces, may be overlapping
        self.character = self.character.grow(pos)
        self.board.add_tile(self.character)
        self.spawn_fruit()

    # A bit undescriptive but it just runs a tick basically
    def move_character(self, tile=None):
        self.character.move()
        

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Utility functions
    def spawn_fruit(self):
        self.board.add_tile(Collectibles.fruit_rand(tuple(self.board.get_available())))

    # Have all the checks just be here
    def run_tick(self):
        self.key_event()
        self.check_collisions()
        self.board.refresh_map()
        



class SnakeGame:
    def __init__(self):
        # Static configurations
        self.config = {
            "window_scale": 0.4,
            "window_background": (0, 0, 0),
        }

        # Dynamic attributes, does not change during runtime though
        self.attributes = {
            "board_dimensions": [9, 9],
            "board_unit": 20,
            "board_palette": ((100, 100, 100), (100, 100, 100))
        }

        self.set_config()
        self.initialize_objects()

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
        self.board = GameBoard(dimensions=a["board_dimensions"], tile_unit=a["board_unit"])
        self.board.set_color(a["board_palette"])

        self.character = Entity.Char(position=(0,0), Head=True)  # Player tile
        self.board.add_tile(self.character)

        self.r = BoardRules(self.board)

        self.r.spawn_fruit()

        


    def update_window(self, scale=0.4):
        # Assumes single monitor setup for now
        return tuple(x*scale for x in pygame.display.get_desktop_sizes()[0])

    # Gets the center of the window
    def get_center(self):
        self.center = ((self.window.get_width() - self.board.get_width()) // 2, (self.window.get_height() - self.board.get_height()) // 2)

    # Skeleton implementation of movement functions

    def run(self):
        loop = cycle((i for i in range(0,20)))
        char = Tile((5, next(loop)))
        self.board.add_tile(char)
        self.get_center()

        while True:
            self.r.run_tick()
            self.board.draw_board(self.window, self.center)

            # holy hack batman
            # fix, too laggy have board updates automatically handle tile updates
            # board.update_tile(char.id, char)
            pygame.time.Clock().tick(4)
            pygame.display.flip()

SnakeGame().run()