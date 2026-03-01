
''' Custom classes imports '''
from GameHud import GameHUD
from UserInput import FileHandler as data
from UserInput import KeyHandler

import json
import pygame
import random

# 12/08/25 - Take two, now implements basic tile logic and state storage
# 2/14/26 - My God, it works
# Stuff to add:
# - Handling palettes and sprites
# - Update spawner
# Augur

# Note: 
# Quick Overview of the structure:
# - SnakeGame: Central class, handles rendering, input and state management.
#   - BoardRules: Central hub for all the game logic and state, includes rules, win conditions, collisions and controls.
#   - GameBoard: Handles the mapping, tile management and drawing.
#   
#   The rest are disconnected from the main loop    
#   - Tile: Base classes for board objects. 
#   - Collectibles: Currently just fruits, but could be expanded for more complex items.
#   - Entity: Proto class for building more complex tiles, currently just the snake segments.

class Tile:
    scale = 1 # Here for scaling the window
    def __init__(self, personality:int, position=(0,0), color=(255, 0, 0), file_dir=None):
        self.personality = personality
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
        old_pos = self.position
        self.position = new_position
        return old_pos

    # Standard way of calling
    def __hash__(self):
        return hash(self.personality)
    
    def __index__(self):
        return self.personality
    
    # An accident happened here -- deprecated
    def __int__(self):
        return self.personality

    def __eq__(self, other):
        if isinstance(other, int):
            return self.personality == other
        if isinstance(other, Tile):
            return self.personality == other.personality
        return False
            
class Entity(Tile):
    """ Base class for entity components """
    def __init__(self, controller, **kwargs):
        self.controller = controller    # Unified means for movement logic
        super().__init__(**kwargs)

    class FollowerNode(Tile):
        def __init__(self, parent, **kwargs):
            self.back = None
            self.front = None
            self.parent = parent
            super().__init__(**kwargs)

        def move(self, new_position):
            old_pos = self.position
            self.position = new_position
            if self.back:
                self.back.move(old_pos)

        def draw(self, surface:pygame.Surface, scale=1):
            super().draw(surface)
            if self.back:
                self.back.draw(surface)

# Nesting the classes for the sake of classification
class Collectibles(Tile):
    """ Base class for interactive components, collectibles rn since thats the only current function  """
    # Thinking about developing (or borrowing) an algorithm for making fruit spawns have an in-game factor that determines how "easy" a fruit spawn should be
    class Fruit(Tile):
        def __init__(self, quality=1, tier=1, value=1, **kwargs):
            self.tier = tier
            self.value = value
            self.quality = quality
            super().__init__(**kwargs)

# Entity Instances
class Snake(Entity):
    _attributes = {
        "color": (0, 200, 0),
        "personality": 9
    }

    @classmethod
    def _node_factory_gen(cls):
        """Generator that accepts parent and position context for each new node."""
        context = yield None 
        while True:
            parent, pos = context
            node = Entity.FollowerNode(parent=parent, position=pos, personality=cls._attributes["personality"], color=cls._attributes["color"])
            context = yield node

    def __init__(self, position=(0, 0), direction=(1, 0), controller=None):
        super().__init__(
            personality=self._attributes["personality"],
            position=position,
            color=self._attributes["color"],
            controller=controller
        )
        
        self.node_factory = self._node_factory_gen()
        next(self.node_factory) # Prime the generator
        
        self.direction = direction
        self.last_moved_direction = direction
        
        # Initialize Persistent Tail with parent (self) and position
        self.tail = self.node_factory.send((self, position))
        self.back = self.tail 

    def grow(self):
        """ Insertion: Wedges a node between head and the previous back. """
        # Use the head as the parent and its current position as the start
        new_segment = self.node_factory.send((self, self.position))
        
        old_back = self.back 
        
        # Re-link Head -> New Segment
        self.back = new_segment
        # (New segment's .front is already set to 'self' by the factory)
        
        # Re-link New Segment -> Old Back (the previous body or tail)
        new_segment.back = old_back
        if old_back:
            old_back.front = new_segment

    def move(self, new_position=None):
        old_self_pos = self.position
        if new_position is None:
            new_position = (self.position[0] + self.direction[0], 
                            self.position[1] + self.direction[1])

        if self.back:
            self.back.move(old_self_pos)

        self.last_moved_direction = self.direction
        super().move(new_position)

    def draw(self, surface, scale):
        super().draw(surface, scale)
        if self.back:
            self.back.draw(surface, scale)



class GameBoard(pygame.Surface):
    # Just for reference, this is the id for each tile
    lut = {
        0: "empty", 
        1: "tail",
        2: "fruit",
        8: "portal",
        9: "head"
    }   
    config = data.getConfig()["board"] # Access point for board config

    def __init__(self, attributes:dict):
        self.setAttributes(attributes)
        self.map = self.createMap()
        self.instances = []    # Tracks all instances tiles on the board.

    # Internal Data +---------------------------------------------------
    def setAttributes(self, a:dict):
        """ Sets all the attributes, manual for type safety. """
        c = GameBoard.config
        self.tile_unit = c["tile_unit"] * a["tile_scale"] # Visual, thinking of making this scale when the window resizes (tile scale here for a perk)
        self.bounds = a["dimensions"]
        self.color = c["palette"] # Visual
        super().__init__(tuple(x*self.tile_unit for x in self.bounds))
        
    def getAttributes(self):
        """ Return attribute as a dict. """
        return {key: getattr(self, key) for key in self.__dict__}

    # Mapping +---------------------------------------------------
    def createMap(self):
        """ Currently: just builds and empty map. """
        w, h = self.bounds
        return [[0 for _ in range(w)] for _ in range(h)]
    
    def getAvailable(self):
        w, h = self.bounds
        occupied = self.getOccupied()
        return [(x, y) for x in range(w) for y in range(h) if (x, y) not in occupied]

    def getOccupied(self):
        occupied = []
        for tile in self.instances:
            curr = tile
            while curr:
                occupied.append(curr.position)
                curr = getattr(curr, 'back', None)
        return occupied
    
    def getClearPercentage(self):
        total_tiles = self.bounds[0] * self.bounds[1]
        occupied_tiles = len(self.getOccupied())
        return (total_tiles - occupied_tiles) / total_tiles

    def centerBoard(self):
        """ Returns the coordinates for the center tile of the board. """
        w, h = self.bounds
        return ((w-1)//2, (h-1)//2)

    # Map Data +---------------------------------------------------
    def addTile(self, tile:Tile):
        self.instances.append(tile)
        self.refreshMap()

    def clearTile(self, tile):
        if tile in self.instances:
            self.instances.remove(tile)
        self.refreshMap()

    def getTile(self, position:tuple):
        """ Searches for a tile with their position. """
        x, y = position
        if 0 <= x < self.bounds[0] and 0 <= y < self.bounds[1]:
            return self.map[y][x] # Accessing by Row (y) then Col (x)
        return -1 # Boundary flag
        
    def searchBoard(self, personality):
        """ Searches for all tiles of a certain type on the board, returns positions as a list. """
        return [tile for tile in self.instances if tile.personality == personality]

    def refreshMap(self):
        """ Refreshes the map when positions are changed on the objects themselves. """
        self.map = self.createMap()
        for tile in self.instances:
            curr = tile
            while curr: # Traverse snake body
                tx, ty = curr.position
                if 0 <= tx < self.bounds[0] and 0 <= ty < self.bounds[1]:
                    self.map[ty][tx] = curr
                curr = getattr(curr, 'back', None)

    # Spawners +---------------------------------------------------
    def spawnRand(self, tile:Tile):
        """ Global spawner. """
        tile.position = random.choice(self.getAvailable())
        self.addTile(tile)

    # Drawing  +---------------------------------------------------
    def drawBg(self, palette):
        """ Draws the background tiles checkered. """
        for y in range(self.bounds[1]):
            for x in range(self.bounds[0]):
                pygame.draw.rect(self, palette[(x+y) % 2], ((x*self.tile_unit, y*self.tile_unit), (self.tile_unit,)*2))

    def drawTiles(self):
        for tile in self.instances:
            tile.draw(self, self.tile_unit)

    def drawBoard(self, window, position:tuple):
        # window.fill((0, 0, 0)) # Moved to SnakeGame loop
        self.drawBg(self.color)
        self.drawTiles()
        window.blit(self, position)





class BoardRules():
    """
        Central hub for all the game logic and state
        Includes rules, win conditions, collisions and controls
        Note: game_status["state"] is used for one-way communication to the SnakeGame class
    """
    def __init__(self, board_properties: dict, status:dict):
        self.startBoard(board_properties)
        self.game_status = status
        self.game_status["tick_speed"] = self.getTickSpeed
        self.clock = 0      # Helper variable for calculating delta time

        self.on_collide = {
            0: self.is_empty,
            1: self.collideTail, 
            2: self.collide_fruit,
            -1: self.game_over
        }

        self.action_map = {
            # Movement: Done with the assumption that you can only move one tile at a time
            #   - use of lambda expression to have the direction parameter preset
                "move_up": lambda : self.changeDirection((0, -1)),
                "move_down": lambda : self.changeDirection((0, 1)),
                "move_left": lambda : self.changeDirection((-1, 0)),
                "move_right": lambda : self.changeDirection((1, 0))
                
        }

# Onetime Events +---------------------------------------------------
    # Can be expanded for creating dynamic map progresion every loop
    def startBoard(self, board_properties:dict):
        """ Loads board with passed properties. """
        self.board = GameBoard(board_properties)
        self.character = Entity.Char(position=self.board.centerBoard())
        self.board.addTile(self.character)
        self.spawn_fruit()


# Character Logic/Functions +---------------------------------------------------
    def changeDirection(self, new_dir):
        if not self.isIllegalTurn(new_dir):
            self.character.changeDirection(new_dir)

    def isIllegalTurn(self, new_dir):
        """ Prevents 180s. """
        opposite = (new_dir[0] * -1, new_dir[1] * -1)
        return opposite == self.character.direction

# Board Data (or anything related to sending/requesting data to/from the board directly.)
# Tried to avoid direct interaction with the board inside of this class, but this works
    def spawn_fruit(self):
        available = self.board.getAvailable()
        if available:
            self.board.spawnRand(Collectibles.Fruit())

# Collision Logic +---------------------------------------------------
    def is_empty(self, tile=None):
        ''' Tile: 0. Basic tile function. '''
        self.character.move()
        self.multDecay()

    def collide_fruit(self, tile: Collectibles.Fruit):
        """ Tile: 2. """
        self.character.grow(tile.position)
        self.game_status["score"] += (tile.tier * 10)
        self.game_status["multiplier"] += (tile.quality * 10)



        self.game_status["fruit_count"] += 1
        self.board.clearTile(tile)
        self.spawn_fruit()
    
    def collideTail(self, tile:Entity.Char):
        """ Runs the loop logic mainly, but handle game over transition on body collision. """
        if tile.back != None:
            # Restarts the board, can be encapsulate to another function in the case that other events trigger a loop
            board_properties = self.board.getAttributes()
            self.startBoard(board_properties)
        else:
            self.game_over()

    def game_over(self, tile=None):
        """ Tile: 9 or -1 (boundary). """
        print(f"Game Over! Final Score: {self.game_status["score"]}")
        self.game_status["state"] = "loss"
        



# Dynamic Data  +---------------------------------------------------
    def getTickSpeed(self):
        """ Returns the current tick speed, calculated from the base and the clear percentage. """
        # Orig. version - (1000/self.game_status["tick_rate"])*(self.game_status["tick_base"] + self.board.getClearPercentage())
        return (1000/self.game_status["tick_rate"])*(1 + self.board.getClearPercentage() ** 10)

    def multDecay(self, n=.2):
        """ Multiplier decay over time, adds a bit of urgency to the game. """
        # This is a simple linear decay, could be made more complex with different decay rates or thresholds
        self.game_status["multiplier"] = 1 + (self.game_status["multiplier"]/n)
        yield n * 2

    def update_clock(self, dt):
        """
        Increments the accumulator based on program delta time.
        Returns True if a game tick should occur.
        """            
        self.clock += dt
        while self.clock >= self.game_status["tick_speed"]():
            self.runTick()
            self.clock -= self.game_status["tick_speed"]()
        return False

# Game Checks/Tick Loop +---------------------------------------------------
    def checkCollisions(self):
        target_pos = (self.character.position[0] + self.character.direction[0], self.character.position[1] + self.character.direction[1])
        front_tile = self.board.getTile(target_pos) 
        # Check if it's a Tile object or an integer (0 or -1)
        lookup = front_tile.personality if hasattr(front_tile, 'personality') else front_tile
        
        if lookup in self.on_collide:
            self.on_collide[lookup](front_tile)

    def runTick(self):
        self.checkCollisions()
        self.board.refreshMap()

# Central class ==============================================================================================================   
class SnakeGame:
    """ 
        Central class for the game, handles rendering, input and state management. 
        Calls BoardRules for game logic and data. 
    """
    def __init__(self):
        pygame.init()
        # Window and program setup

        # Data loading
        self.config = data.getConfig()

        # Window setup
        self.window = pygame.display.set_mode(self.config["window_size"])
        pygame.display.set_caption(self.config["caption"])
        self.clock = pygame.time.Clock()
        
        # Player actions regarding the menu/system
        self.action_map = {
            "quit": pygame.quit,
            "pause": self.pauseGame,
            "restart": self.initializeGame  
        }

        # Contains the tick functions for each state
        self.state = {
            "paused" : self.paused,
            "running" : self.running,
            "loss" : self.loss,
            "minnesota": False,
        }

        # Immediately boots up the game
        self.initializeGame()

# Some specific use case functions 
    def centerBoard(self):
        """ This is used for centering the board on the window. """
        return ((self.window.get_width() - self.r.board.get_width()) // 2, 
                (self.window.get_height() - self.r.board.get_height()) // 2)

    def getActionMap(self):
        """ This just flattens the action maps for the key handler. """
        return self.action_map | self.r.action_map

# Single-use functions +---------------------------------------------------
    # This a toggle, currently do not know how to do this properly
    def pauseGame(self):
        self.r.game_status["state"] = "paused" if self.r.game_status["state"] == "running" else "running"
        self.hud.pause_sequence()

# Game initialization +--------------------------------------------------- 
    def initializeGame(self, board_properties=None, status=None):
        """ Boots up game objects then UI. """
        if not board_properties and not status:
            board_properties = data.getBoardDefault()
            status = data.getGameDefault()
        self.r = BoardRules(board_properties, status)   # No clue how to deal with this but there should be no errors

        self.key_handler = KeyHandler(self.getActionMap())
        self.hud = GameHUD(self.r.game_status, self.config, self.key_handler, self.window.get_size())
        self.config["center_window"] = self.centerBoard()


# Game states +---------------------------------------------------
    def paused(self, dt):
        """ State: Game is paused, only accepts menu inputs. """
        pass

    def running(self, dt):
        """ State: Everything here is bound to the game's tick rate. """
        self.r.clock += dt
        while self.r.clock >= self.r.game_status["tick_speed"]():
            self.key_handler.evaluate_queue()  # Process buffered inputs
            self.r.runTick()
            self.r.clock -= self.r.game_status["tick_speed"]()

    def loss(self, dt):
        """ State: Game over, only accepts menu inputs. """
        self.initializeGame()

# Render/Runtime Loop +---------------------------------------------------
    def render(self):
        self.window.fill(self.config["window_background"])
        self.r.board.drawBoard(self.window, self.config["center_window"])
        self.hud.draw(self.window)
        pygame.display.flip()

    def check_input(self):
        """ The GameHUD handles all the inputs, this is here for better distinction of the process. """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.key_handler.handle_keydown(event.key)
            self.hud.handle_events(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def run(self):
        while True:
            dt = self.clock.tick(self.config["refresh_rate"]) # Delta time in seconds, normalized to tick rate
            self.check_input()
            self.state[self.r.game_status["state"]](dt) 

            # TODO: Keep in mind when scaling
            self.hud.update() # Update HUD elements
            self.render()

if __name__ == "__main__":
    SnakeGame().run()