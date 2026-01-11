from UIContainer import UIContainer
from DialogueBox import DialogueBox
import pygame
from snek import BoardRules

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
            font=""
        )

        self.multiplier_box = DialogueBox(
            text=f"MULTIPLIER: x{self.rules.multiplier}",
            bounds=(200, 40),
            color=(40, 40, 40),
            text_color=(255, 255, 255),
            font=""
        )
        
        # Align the score box to the top-middle
        self.add_element(self.score_box, align="center")

    def update(self):
        """ Syncs the display with the current score from rules. """
        self.score_box.update_text(f"SCORE: {self.rules.score}")

    def draw(self, surface: pygame.Surface):
        self.draw(surface)