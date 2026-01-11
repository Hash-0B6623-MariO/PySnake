from UI.UIStack import UIStack
from UI.UIContainer import UIContainer
from UI.DialogueBox import DialogueBox

from snek import BoardRules

import pygame

# I miss Java
class var:
    ''' Holds global variables '''
    # Default styling for HUD elements
    text = {
        "font": "Assets/Hud/Font/KiwiSoda.ttf",
    }


class StatDisplay(UIContainer):
    def __init__(self, rules: BoardRules, window_width: int):
        self.rules = rules
        # Create a container that spans the top of the window
        super().__init__(
            size=(window_width, 50), 
            position=(0, 10), # 10 pixels padding from top
        )
        
        # Initialize the score box using your DialogueBox logic
        # We place it in the center of our wide HUD container
        self.score_box = DialogueBox(
            text=f"SCORE: {self.rules.score}",
            bounds=(200, 40),
            color=(40, 40, 40),
            text_color=(255, 255, 255),
            font=var.text["font"]
        )

        self.multiplier_box = DialogueBox(
            text=f"MULTIPLIER: x{self.rules.multiplier}",
            bounds=(200, 40),
            color=(40, 40, 40),
            text_color=(255, 255, 255),
            font=var.text["font"]
        )
        
        # Align the score box to the top-middle
        self.add_element(self.score_box, align="center")

    def update(self):
        """ Syncs the display with the current score from rules. """
        self.score_box.update_text(f"SCORE: {self.rules.score}")


class GameHUD(UIStack):
    """ 
    A specialized UIStack that manages all in-game HUD elements.
    Inheritance allows it to be treated as a single drawable object.
    """
    def __init__(self, rules, window_size: tuple):
        super().__init__()
        self.rules = rules
        self.width, self.height = window_size
        
        # Initialize and organize components
        self.setup_components()

    def setup_components(self):
        """ 
        Creates UIContainers for different screen regions and 
        pushes them onto the internal stack.
        """
        self.push(StatDisplay(self.rules, self.width))



    def update(self):
        """ 
        Synchronizes the UI text with the game rules data. 
        Called every game tick or frame depending on performance needs.
        """
        self.update

    def draw(self, surface):
        """ 
        Optional: Override if you need background dimming or 
        specific HUD-wide effects before drawing the stack.
        """
        super().draw(surface)

    # Helper functions