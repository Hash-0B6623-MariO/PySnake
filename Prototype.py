import pygame


import math
import random

# Sorry if this assaults your eyes 
'''
Thing for part 14
Started 7/17/25
    7/27/25: Prototype & Hiatus
    11/30/25: Fixing prototype
Deadline ?/??/??

GUIDELINES:
    The game has a sprite the player can move in some way (/)
    The game has some Collectable items and/or Enemies (1, could add walls)
    The player needs to be set a clear task in the game (points)
    The game contains a counter which tells the player how they are doing in the game (status board)
    The source code for the game is divided into functions like in the Sokoban example (divided? yes. readable? no.)
    
Notes:
    Functional, could do with A LOT of optimizations tho
    Get the app functions done
    Get sprites
    [IMPORTANT] Do take note of the fact that the visuals are tied to the functionality '''

''' Some classes to help with specific problems '''
class GameBoard:
    def __init__(self, properties:dict, window):
        self.color = properties["color"]  # in RGB format
        self.tile_unit = properties["tile_unit"]
     
     # TODO: Tweak this so that it has the center of the screen as the origin point agawgawwagwgag
        self.size = (x*self.tile_unit for x in properties["size"])
        self.window = window

        # Record: Had this tweaked for atleast 6 times now  -- [7/27/2025]
        self.setTiles()

        # SnakeGame properties
        self.fruit = Fruit(self)
        self.fruit.spawnRandom()
        self.snake = SnakeChar(self.window, self.tile_unit)  # Create a new snake character

        # Gamespeed
        self.clock = pygame.time.Clock()
        self.fps = 2

        # BoardStatus
        self.status = {
            "points" : self.fruit.getPoints,
            
            # Kinda pointless atm
            "time" : self.clock.get_fps
        }

    # Setter for tiles
    def setTiles(self):
        # Could be optimized -- What the fuck
        self.tiles = [(range(a, a + b, self.tile_unit) for a, b in zip(self.position[0], self.size[0])) for x in self.size[1]]

    def loss_animation(self):
        # TODO: Re-center for debugging
        self.snake.position = (a + (b // 2) for a, b in zip(self.position, self.size))

    def draw(self, window): 
        pygame.draw.rect(window, self.color, 
                         (self.position, self.size))


class SnakeChar:
    def __init__(self, window, tile_unit:int):
        self.color = (0, 255, 0)  # Green color for the snake
        self.size = {"width": tile_unit, "height": tile_unit}    # Scaled by image size
        self.position = (0, 0)
        
        self.body = [window, self.color]  # Placeholder for character properties
        self.segments = []  # Tracks snake position and size per tick with self.__tracebody
        self.length = 0  # Holder variable, modified in SnakeGame to bind it to points as a [function]...

        # Mapping for directional inputs
        self.key_map = {
            pygame.K_w: self.move_UP,
            pygame.K_s: self.move_DOWN,
            pygame.K_a: self.move_LEFT,
            pygame.K_d: self.move_RIGHT
        }

        self.move_RIGHT()  # Default state


    def __tracebody(self):
        pos_size = (self.position, self.size)
        self.segments.append(pos_size)    # New position appended

    def draw(self):
        self.__tracebody()
        # This should be going through the segments from -1 to -self.length - 2
        # Example: when self.length = 3, range outputs [-1, -2, -3, -4]
        for i in range(-1, -self.length() - 2, -1):
            try:
                # TODO: I refuse to fix this
                pygame.draw.rect(*[*self.body, self.segments[i]])
            except (IndexError) : break # Should only get raised at the start
            

    # Movement functions
    # Sets direction facing -- state[0] is axis, state[1] is the direction
    def move_UP(self): self.direction = (0, 1)   # Up
    def move_DOWN(self): self.direction = (0, -1)  # Down
    def move_LEFT(self): self.direction = (-1, 0) # Left
    def move_RIGHT(self): self.direction = (1, 0)  # Right

    # Constant movement -- called every tick
    def move_player(self, tile_unit:int):
        # TODO: Tweak so it works idk
        self.position += tile_unit * self.direction


class Fruit:
    def __init__(self, board:"GameBoard"):
        self.board = board
        self.position = (0, 0)
        self.color = (255, 0, 0)
        self.trigger = False
    
        self._points = 0 # TODO: GL tracking this

    def getPoints(self):
        return self._points

    def condition(self):
        # Trigger for 
        if (self.board.snake.position) == (self.position):
            self.spawnRandom()
            self._points += 1
            self.trigger = True

    # Spawn Fruit, use with snakegame or it breaks
    def spawnRandom(self):
        x_range, y_range = self.board.bounds
        self.board.fruit.position = random.randrange(min(x_range), max(x_range), self.board.tile_unit), random.randrange(min(y_range), max(y_range), self.board.tile_unit)


    def draw(self, window):
        # Optimize
        size_x, size_y = self.board.tile_unit
        pygame.draw.rect(window, self.color, 
                        (self.position, 
                        size_x, size_y))
        self.trigger = False   # Set back to default




''' The main game class '''
class SnakeGame:
    def __init__(self, BoardProperties:dict):
        pygame.init()
        
        # UI font
        pygame.font.init()


        # Window ---------------------------------------------------
        # Window size and title 
        self.window = pygame.display.set_mode([800, 540])  # Width, Height
        pygame.display.set_caption("PySnake")  # Window title

        # Window color and fill
        self.window.fill((0, 25, 80)) # This is the background color, Copy and paste it to the rest of the 200 lines

        # Game board --------------------------------------------------
        self.board = GameBoard(BoardProperties, self.window)

        # Center the board in the window
        # self.board.position["x"] = self.window.get_width() // 2 - self.board.size["width"] // 2
        self.window.get_size()
        # self.board.position["y"] = self.window.get_height() // 2 - self.board.size["height"] // 2
        # Record: Had this tweaked for atleast 4 times now  -- [7/26/2025]
        self.board.redoBounds()

        # Player --------------------------------------------------
        # Center player and resize relative to the board, still no proper coordinate system
        self.board.snake.size["width"] = self.board.tile_unit
        self.board.snake.size["height"] = self.board.tile_unit
        self.board.snake.position = {"x": self.board.position["x"] + self.board.size["width"] // 2, "y": self.board.position["y"] + self.board.size["height"] // 2}   

        # Bind points to length
        self.board.snake.length = lambda: 1 + self.board.fruit.getPoints()

        # self.board.snake.length = self.board.fruit.points

        self.board.fruit.spawnRandom()
        self.update_screen()


    # Board status
    def drawStatus(self):
        pass

    def updateStatus(self):
        pass


    # Essentials
    def update_screen(self):
        self.window.fill((0, 25, 80))  # Clear
        self.board.draw(self.window)  # Draw the board
        self.board.fruit.condition() # Draw fruit when set
        self.board.fruit.draw(self.window)

        self.board.snake.draw()  # Draw the player
        pygame.display.flip()  # Update
    
    def check_events(self):
        for event in pygame.event.get():
            # Does the movement
            # Check state
            if event.type == pygame.KEYDOWN:
                key_pressed = event.key
                if key_pressed in self.board.snake.key_map:
                    # Currently this is not tied to fps apparently, which is great but affects movement
                    self.moveChar(key_pressed)


            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    # Game rules
    def border_collision(self):
        # Border detection
        if self.board.snake.position[self.board.snake.state[0]] not in self.board.bounds[self.board.snake.state[0]]:
            print("Player has lost")
            self.board.loss_animation()
    
    def tail_collision(self):
        # Ok, so it essentially takes the recorded previous moves with respect to length, 
        # gets the positions into a list,
        # and checks if current position is in one of those 
        # Note: The snake.segments does record the size as well, hence the need for [:2]
        # Current status: Should not bug out, works even if you run in a loop at length 4
        snake_pos = [self.board.snake.position['x'], self.board.snake.position['y']]
        snake_bounds = [list(prev_pos[:2]) for prev_pos in self.board.snake.segments[len(self.board.snake.segments) - self.board.snake.length():]]  
        if snake_pos in snake_bounds:
            self.board.loss_animation()


    ''' Passive rules '''
    # Check current state to avoid moving backwards
    def moveChar(self, key_pressed):
        prev_state = self.board.snake.state[0]
        self.board.snake.key_map[key_pressed]()
        if prev_state == self.board.snake.state[0]:
            print("Move undone")
            self.board.snake.state[1] *= -1
        print("Prev", prev_state, "then", self.board.snake.state[0])


    def start_game(self):
        running = True
        while running:
            dt_ms = self.board.clock.tick(self.board.fps) 
            dt = dt_ms / 1000.0 # Convert milliseconds to seconds

            self.check_events()
            self.board.snake.move_player(self.board.tile_unit)



            # Check for collisions
            self.border_collision()
            self.tail_collision()
            self.board.fruit.condition()

            self.update_screen()

            color = (120, 215, 20, 220)
            rect = (55, 90, 140, 140)

            
            shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
            self.window.blit(shape_surf, rect)




''' Application-scale functions '''
class GameRunner:
    pass

def terminate():
    pass

def pause():
    pass



''' User end '''
def main():
    # Customizeable, for now
    # Make sure sizes are even or it breaks
    board_properties = {
        "color": (255, 0, 120),  # Red

        "size": (20, 20), 

        "tile_unit": 20  # Tile unit size/scale
    }
    # Snake Game instance
    snake_game = SnakeGame(board_properties)

    # Starts the game loop
    snake_game.start_game()
main()