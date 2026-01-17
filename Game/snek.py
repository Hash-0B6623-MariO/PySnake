''' Custom classes imports '''
from GameHud import GameHUD

import json
import pygame
import random



# 12/08/25 - Take two, now implements basic tile logic and state storage
# Stuff to add:
# - Centralize input assignment
# - Handling palettes and sprites
# - Optimization for movement, constant checks for moving a character
#       * Currently nested to one check but could be done with dicts
# - Update spawner
# Augur

# Prio: Final struct for board class

# Note: 
# - config currently is for aesthetics only
# - Funky interaction with how inputs are picked up, 
#   needs to be centralized since wherever the mouse is at 
#   chooses where the input goes to

class Tile:
    # Each id corresponds to a unique tile type, the rest of the code refers to types as ids
    # This is hardcoded. Reference for checking
    # This now acts as the sort of constructors for tile objects
    # Currently not really needed, but could be useful for building more complex tiles later
    tile_types = {}

    def __init__(self, position=(0,0), personality=None, color=(255, 0, 0), file_dir=None):
        self.personality = len(Tile.tile_types) + 1 if personality is None else personality
        Tile.tile_types[self.personality] = self

        self.sprite = self.replace_sprite(file_dir) if file_dir else None
        # Alternate when not using sprites
        self.color = color
        self.position = position

    def replace_sprite(self, file_dir):
        # Open image, buffer on a surface here. Could also be a color fill.
        try:
            return pygame.image.load(file_dir).convert_alpha()
        except Exception as e:
            print(f"Error loading sprite: {e}")
            return None

    # Helper function for drawing
    def scale_to_board(self, tile_unit):
        return tuple(pos * tile_unit for pos in self.position)

    def draw(self, surface:pygame.Surface, scale=1):
        if self.sprite:
            # Scaled blit for sprites
            surface.blit(pygame.transform.scale(self.sprite, (scale, scale)), self.scale_to_board(scale))
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
        return False

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
        if not bounds: return None
        pos = random.choice(bounds)
        return cls.Fruit(pos)
            
# Proto class for building tiles
class Entity:
    class Char(Tile):
        def __init__(self, position=(0, 0), direction=(1, 0), personality=9, color=(0, 255, 0)):
            super().__init__(position, personality, color=color)
            self.back = None 
            self.direction = direction 
            self.last_moved_direction = direction

        def grow_into(self, target_pos):
            # Create body segment at old head pos
            new_segment = Entity.Char(position=self.position, personality=1, color=(0, 200, 0))
            new_segment.back = self.back
            self.back = new_segment
            # Jump head to fruit pos
            self.position = target_pos
            self.last_moved_direction = self.direction

        def move(self, new_position=None):
            old_self_pos = self.position
            if new_position is None:
                new_position = self.get_front()

            if self.back:
                self.back.move(old_self_pos)

            self.last_moved_direction = self.direction
            super().move(new_position)

        def get_front(self):
            return (self.position[0] + self.direction[0], self.position[1] + self.direction[1])

        def change_direction(self, direction):
            self.direction = direction

        def draw(self, surface:pygame.Surface, scale=1):
            super().draw(surface, scale)
            if self.back:
                self.back.draw(surface, scale)
        

class GameBoard(pygame.Surface):
    def __init__(self, dimensions:list, tile_unit:int):
        super().__init__(tuple(x*tile_unit for x in dimensions))
        self.tile_unit = tile_unit
        self.bounds = dimensions
        self.map = self.create_map()
        self.instances = []    # Tracks all instances tiles on the board.

        # Store tile palettes here
        self.__color = ((30, 30, 30), (45, 45, 45)) # Changed to default darks for visibility

    def get_color(self):
            return self.__color

    def set_color(self, value:tuple):
            self.__color = value

    # Mapping +---------------------------------------------------
    def create_map(self):
        w, h = self.bounds
        return [[0 for _ in range(w)] for _ in range(h)]
    
    def get_available(self):
        w, h = self.bounds
        occupied = self.get_occupied()
        return [(x, y) for x in range(w) for y in range(h) if (x, y) not in occupied]

    def get_occupied(self):
        # We need to flatten the linked snake body to get all occupied coordinates
        occupied = []
        for tile in self.instances:
            curr = tile
            while curr:
                occupied.append(curr.position)
                curr = getattr(curr, 'back', None)
        return occupied
    
    def get_center(self):
        w, h = self.bounds
        return ((w-1)//2, (h-1)//2)

    # Drawing Functions ==============================================================================================================
    # This draws the background tiles checkered style
    def draw_bg(self, palette):
        for y in range(self.bounds[1]):
            for x in range(self.bounds[0]):
                pygame.draw.rect(self, palette[(x+y) % 2], ((x*self.tile_unit, y*self.tile_unit), (self.tile_unit,)*2))

    # Could be better optimized
    def draw_tiles(self):
        for tile in self.instances:
            tile.draw(self, self.tile_unit)

    def draw_board(self, window, position:tuple):
        # window.fill((0, 0, 0)) # Moved to SnakeGame loop
        self.draw_bg(self.get_color())
        self.draw_tiles()
        window.blit(self, position)

    # Board Data Functions ==============================================================================================================
    def add_tile(self, tile:Tile):
        self.instances.append(tile)
        self.refresh_map()

    def clear_tile(self, tile):
        if tile in self.instances:
            self.instances.remove(tile)
        self.refresh_map()

    # Searches for a tile with their position
    def get_tile(self, position:tuple):
        x, y = position
        if 0 <= x < self.bounds[0] and 0 <= y < self.bounds[1]:
            return self.map[y][x] # Accessing by Row (y) then Col (x)
        return -1 # Boundary flag
        
    # Searches for all tiles of a certain type on the board, returns position
    def search_board(self, personality):
        return [tile for tile in self.instances if tile.personality == personality]

    # Refreshes the map when positions are changed on the objects themselves
    def refresh_map(self):
        self.map = self.create_map()
        for tile in self.instances:
            curr = tile
            while curr: # Traverse snake body
                tx, ty = curr.position
                if 0 <= tx < self.bounds[0] and 0 <= ty < self.bounds[1]:
                    self.map[ty][tx] = curr
                curr = getattr(curr, 'back', None)

# Game Logic built here ==============================================================================================================
# Includes rules, win conditions, collisions and controls
# Notes: 
#   Attribute syntax in SnakeGame, this just isolates the logic from the rest of the code 
#   Do player controls in one unified function
#   Use the coordinate system of the board for movement and collision detection
class BoardRules():
    ''' Central hub for all the game logic and current state '''
    def __init__(self, board: GameBoard):
        self.board = board
        self.character = self.find_character()
        self.buffer = []
        self.stat = {
            "score": 0,
            "multiplier": 1,
            "fruit_count": 0
        }

        self.key_mapping = {
            pygame.K_w: (0, -1),
            pygame.K_s: (0, 1),
            pygame.K_a: (-1, 0),
            pygame.K_d: (1, 0)
        }

        self.on_collide = {
            0: self.move_character,
            1: self.game_over, 
            2: self.collide_fruit,
            -1: self.game_over
        }

        self.game_state = {
            "running": True,

        }
    def key_event(self, event):
        """ Processes a single event passed from the main loop. """
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_mapping:
                new_dir = self.key_mapping[event.key]
                # Avoid adding the same direction twice in one tick
                if not self.buffer or self.buffer[-1] != new_dir:
                    self.buffer.append(new_dir)

    def is_illegal_turn(self, new_dir):
        opposite = (new_dir[0] * -1, new_dir[1] * -1)
        return opposite == self.character.last_moved_direction

    def process_buffer(self):
        while self.buffer:
            next_move = self.buffer.pop(0)
            if not self.is_illegal_turn(next_move):
                self.character.change_direction(next_move)
                break 

    def find_character(self) -> Entity.Char:
        return self.board.search_board(9)[0]
    
    def game_over(self, tile=None):
        print(f"Game Over! Final Score: {self.stat["score"]}")
        pygame.quit()
        exit()

    def check_collisions(self):
        target_pos = self.character.get_front()
        front_tile = self.board.get_tile(target_pos) 
        # Check if it's a Tile object or an integer (0 or -1)
        lookup = front_tile.personality if hasattr(front_tile, 'personality') else front_tile
        
        if lookup in self.on_collide:
            self.on_collide[lookup](front_tile)

    def collide_fruit(self, tile: Collectibles.Fruit):
        self.character.grow_into(tile.position)
        self.stat["score"] += (tile.tier * 10)
        self.stat["fruit_count"] += 1
        self.board.clear_tile(tile)
        self.spawn_fruit()

    def move_character(self, tile=None):
        self.character.move()
    

    def spawn_fruit(self):
        available = self.board.get_available()
        if available:
            self.board.add_tile(Collectibles.fruit_rand(available))

    # Work here =============================================================================================================
    # Try to optimize
    def check_global(self):
        ''' Runs checks for global changes '''
        if self.stat["fruit_count"] > 10:
            self.stat["multiplier"] += 1
            self.stat["fruit_count"] = 0

    def run_tick(self):
        self.process_buffer()
        self.check_collisions()
        self.board.refresh_map()


class SnakeGame:
    def __init__(self):
        # Aesthetic properties
        self.config = {
            "window_background": (10, 10, 10),
            "font": "Game/Assets/Hud/Font/KiwiSoda.ttf",
            "center_position": 0
            }
        
        # Game properties
        self.attributes = {
            "board_dimensions": [15, 15],
            "board_unit": 30,
            "board_palette": ((40, 40, 40), (50, 50, 50)),
        }

        # Player actions regarding the menu/system
        self.keybinds = {
            pygame.QUIT: pygame.quit,
            pygame.K_SPACE: self.pause_game

        }

        self.hud_callbacks = {
            "Menu":{
                "pause": self.pause_game
                }
        }

        self.set_config()
        self.initialize_objects()
        
        # Timing attributes
        self.tick_speed = 125 # Milliseconds per tick (8 FPS)
        self.last_tick = pygame.time.get_ticks()

    def get_center(self):
        return ((self.window.get_width() - self.board.get_width()) // 2, 
                (self.window.get_height() - self.board.get_height()) // 2)

    # File reading functions
    def set_config(self):
        pygame.init()
        self.window = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Snake - Tile Logic")
    
    def read_config(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error reading config file: {e}")
            return {}
    
    def write_config(self, file_path, data):
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error writing config file: {e}")

    def pause_game(self):
        self.paused = True
        while self.paused:
            print("Game Paused")

        

    def game_tick(self):
        # TICK LOGIC
        now = pygame.time.get_ticks()
        if now - self.last_tick >= self.tick_speed:
            self.r.run_tick()
            self.hud.update()
            self.last_tick = now

    def render(self):
        # RENDER
        self.window.fill(self.config["window_background"])
        self.board.draw_board(self.window, self.config["center_position"])
        self.hud.draw(self.window)
        pygame.display.flip()

    def initialize_objects(self):
        a = self.attributes
        self.board = GameBoard(dimensions=a["board_dimensions"], tile_unit=a["board_unit"])
        self.board.set_color(a["board_palette"])
        self.character = Entity.Char(position=(5,5))
        self.board.add_tile(self.character)
        self.r = BoardRules(self.board)
        self.r.spawn_fruit()

        self.config["center_position"] = self.get_center()
        self.hud = GameHUD(self.r.stat, self.config, self.hud_callbacks, self.window.get_size())


    def check_input(self):
        # SINGLE EVENT LOOP
        for event in pygame.event.get():
            # Special cases
            # Keyboard
            if event.type == pygame.KEYDOWN:
                if event.key in self.keybinds.keys():
                    self.keybinds[event.key]()

            # UI handling
            ui_captured = self.hud.handle_events(event)


            # Game priority: If UI didn't want it, pass to rules
            if not ui_captured:
                self.r.key_event(event) 

    def run(self):
        while True:
            self.check_input()
            self.game_tick()
            self.render()

if __name__ == "__main__":
    SnakeGame().run()