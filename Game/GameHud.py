from UI.UIStack import UIStack
from UI.UIContainer import UIContainer
from UI.DialogueBox import DialogueBox

from UserInput import InputHandler, InputMask

# The Deadlock Chain Incident of 1/13/2026
# from BoardRules import BoardRules

import pygame


class StatDisplay(UIContainer):
    ''' Displays the score and multiplier '''
    def __init__(self, stat:dict, config:dict, window_width: int):
        self.game_state = stat
        self.config = config
        # Create a container that spans the top of the window
        super().__init__(
            size=(window_width, 50), 
            position=(0, 10), # 10 pixels padding from top
        )
        
        # We place it in the center of our wide HUD container
        self.score_box = DialogueBox(
            text=f"SCORE: {self.game_state["score"]}",
            bounds=(200, 40),
            color=(40, 40, 40),
            text_color=(255, 255, 255),
            font=self.config["font"]
        )

        self.multiplier_box = DialogueBox(
            text=f"MULTIPLIER: x{self.game_state["multiplier"]:.3f}",
            bounds=(200, 40),
            color=(40, 40, 40),
            text_color=(255, 255, 255),
            font=self.config["font"]
        )
        
        # Align the score box to the top-middle
        self.add_element(self.score_box, align="center")
        # Align the multiplier box to the top-right
        self.add_element(self.multiplier_box, relative_pos=(window_width - 220, 5))

    def update(self):
        """ Syncs the display with the current score from rules. """
        self.score_box.update_text(f"SCORE: {self.game_state["score"]}")
        self.multiplier_box.update_text(f"MULTIPLIER: x{self.game_state["multiplier"]:.3f}")

class PauseMenu(UIContainer):
    ''' A simple pause menu overlay '''
    def __init__(self, window_size: tuple, config: dict, callbacks:dict):
        super().__init__(
            position=(window_size[0]//4, window_size[1]//4),
            size=(window_size[0]//2, window_size[1]//2),
            bg_color=(30, 30, 30, 220)
        )
        self.config = config
        self.active = False  # Start inactive
        
        # Title Box
        self.title_box = DialogueBox(
            text="Game Paused",
            bounds=(self.rect.width - 40, 60),
            color=(60, 60, 60),
            text_color=(255, 255, 255),
            font=self.config["font"],
            font_size=32
        )
        self.add_element(self.title_box, relative_pos=(20, 20))
        
        # Resume Button
        self.resume_button = DialogueBox(
            text="Resume",
            bounds=(self.rect.width - 80, 50),
            color=(80, 80, 80),
            text_color=(255, 255, 255),
            font=self.config["font"],
            callback=self.pause(callbacks["pause"])
        )
        self.add_element(self.resume_button, relative_pos=(40, 100))

    def pause(self, pause_callback):
        """ Modifies callback for handling visual changes. """
        def toggle_pause():
            self.active = not self.active
            pause_callback()
        return toggle_pause

class GameHUD(UIStack):
    """ 
    A specialized UIStack that manages all in-game HUD elements.
    Inheritance allows it to be treated as a single drawable object.
    """
    def __init__(self, stat:dict, config:dict, callbacks:dict, window_size:tuple):
        super().__init__()
        self.game_state = stat
        self.config = config
        self.width, self.height = window_size
        self.key_mask = None
        
        # Initialize and organize components
        self.setup_components(callbacks)

    def setActionMap(self, keybinds:dict):
        """ Sets up an InputHandler and InputMask for HUD input capture. """
        # Create InputHandler with setActionMapd keybinds
        input_handler = InputHandler(keybinds)
        for keybind in keybinds:
            input_handler.setActionMap(keybind)

        # Create InputMask covering the whole screen
        self.key_mask = InputMask((self.width, self.height), input_handler)
        self.push(self.key_mask)

    def setup_components(self, callbacks:dict):
        """ 
        Creates UIContainers for different screen regions and 
        pushes them onto the internal stack.
        """
        self.push(StatDisplay(self.game_state, self.config, self.width))
        self.push(PauseMenu((self.width, self.height), self.config, callbacks["Menu"]))
    
    def update(self):
        """ Updates all HUD elements to reflect current game state. """
        for element in self.elements:
            if hasattr(element, 'update'):
                element.update()


    # Helper functions