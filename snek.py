
''' Custom classes imports '''
from GameHud import GameHUD
from UserInput import FileHandler as data
from UserInput import KeyHandler

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
    
    def centerBoard(self):
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
        self.game_state = {
            "state": True,
            "score": 0,
            "multiplier": 1.0,
            "fruit_count": 0,
            
            # Game loop
            "tick_rate": 8, # Game speed
            "ticks": pygame.time.get_ticks,       
            "time": lambda:pygame.time.get_ticks()/1000,   
        }
        self.clock = 0      # Helper variable for calculating delta time

        self.on_collide = {
            0: self.move_character,
            1: self.game_over, 
            2: self.collide_fruit,
            -1: self.game_over
        }

        self.action_map = {
            "movement":{
                "move_up": self.change_direction((0, -1)),
                "move_down": self.change_direction((0, 1)),
                "move_left": self.change_direction((-1, 0)),
                "move_right": self.change_direction((1, 0))
                }
        }

        # Contains the tick functions for each state
        self.state = {
            "paused" : self.paused,
            "running" : self.running,
            "minnesota": False,
        }

# Runtime functions 
    def change_direction(self, new_dir):
        if not self.is_illegal_turn(new_dir):
            self.character.change_direction(new_dir)

    def is_illegal_turn(self, new_dir):
        opposite = (new_dir[0] * -1, new_dir[1] * -1)
        return opposite == self.character.last_moved_direction

    def find_character(self) -> Entity.Char:
        return self.board.search_board(9)[0]



# Collision logic
    def game_over(self, tile=None):
        print(f"Game Over! Final Score: {self.game_state["score"]}")
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
        self.game_state["score"] += (tile.tier * 10)
        self.game_state["fruit_count"] += 1
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
    # Game checks/states
    def check_global(self):
        ''' Runs checks for global changes '''
        if self.game_state["fruit_count"] > 10:
            self.game_state["multiplier"] += 1.0
            self.game_state["fruit_count"] = 0

    def update_clock(self, dt):
        """
        Increments the accumulator based on program delta time.
        Returns True if a game tick should occur.
        """            
        self.clock += dt
        while self.clock >= self.game_state["tick_rate"]:
            self.run_tick()
            self.clock -= self.game_state["tick_rate"]
        return False

    def paused(self):
        pass

    def running(self, dt):
        self.clock += dt
        while self.clock >= self.game_state["tick_rate"]:
            self.check_collisions()
            self.board.refresh_map()
            self.clock -= self.game_state["tick_rate"]
        return False

    def run_tick(self):
        self.check_collisions()
        self.board.refresh_map()
        self.clock -= self.game_state["tick_rate"]
        
        self.state[self.game_state["state"]]()  # Call the function corresponding to the current state


class SnakeGame:
    def __init__(self):
        pygame.init()
        # Window and program setup

        # Data loading
        self.config = data.get_config()
        self.settings = data.get_settings()     # Might move this later

        # Window setup
        self.window = pygame.display.set_mode(self.config["window_size"])
        pygame.display.set_caption(self.config["caption"])
        self.clock = pygame.time.Clock
        
        # Player actions regarding the menu/system
        self.action_map = {
            "quit": pygame.quit,
            "pause": self.pauseGame,
            "restart": self.__init__    # TODO
        }

        # Immediately boots up the game
        self.initialize_game()

        self.states = {
            "running": self.running,
            "paused": self.paused
        }
        
        


# Some specific use case functions ==============================================================================================================   
    def centerBoard(self):
        " This is used for centering the board on the window. "
        return ((self.window.get_width() - self.board.get_width()) // 2, 
                (self.window.get_height() - self.board.get_height()) // 2)

    def getActionMap(self):
        """ This just flattens the action maps for the key handler. """
        return self.action_map | self.r.action_map

    # This a toggle, currently do not know how to do this properly
    def pauseGame(self):
        self.r.game_state["state"] = "paused" if self.r.game_state["state"] == "running" else "running"
        self.hud.pause_sequence()

    def restartGame(self):
        pass

# Game runtime loops
    def paused(self, dt):
        """ State: Game is paused, does nothing """
        # Current the single use pause game function is utilized here
        pass

    def running(self, dt):
        """ State: Gameloop is running """
        # Everything here is bound to the game's tick rate
        self.r.clock += dt
        while self.r.clock >= self.r.game_state["tick_rate"]:
            self.key_handler.evaluate_queue()  # Process buffered inputs
            self.r.run_tick()
            self.r.clock -= self.r.game_state["tick_rate"]

    def render(self):
        self.window.fill(self.config["window_background"])
        self.board.draw_board(self.window, self.config["center_window"])
        self.hud.draw(self.window)
        pygame.display.flip()

    def initialize_game(self):
        a = self.settings

        # Game object initialization
        self.board = GameBoard(dimensions=a["board_dimensions"], tile_unit=a["board_unit"])
        self.board.set_color(a["board_palette"])
        self.character = Entity.Char(position=(5,5))
        self.board.add_tile(self.character)
        self.r = BoardRules(self.board)
        self.r.spawn_fruit()

        self.key_handler = KeyHandler(data.load_keybinds(), self.getActionMap())
        self.hud = GameHUD(self.r.game_state, self.config, self.key_handler, self.window.get_size())
        self.config["center_window"] = self.centerBoard()

    def check_input(self):
        """ The GameHUD handles all the inputs, this is here for better distinction of the process. """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.key_handler.handle_keydown(event.key)
            self.hud.handle_events(event)

    def run(self):
        while True:
            dt = self.clock.tick(self.config["refresh_rate"])
            self.check_input()
            self.states[self.r.game_state["state"]](dt)  # Call the function corresponding to the current state
            self.render()

if __name__ == "__main__":
    SnakeGame().run()