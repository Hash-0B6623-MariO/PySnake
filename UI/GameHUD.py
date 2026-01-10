from UI.UIStack import UIStack
from UI.UIContainer import UIContainer
from UI.DialogueBox import DialogueBox
import pygame

class GameHUD(UIStack):
    """ 
    A specialized UIStack that manages all in-game HUD elements.
    Inheritance allows it to be treated as a single drawable object.
    """
    def __init__(self, rules, window_size: tuple):
        super().__init__()
        self.rules = rules
        self.width, self.height = window_size
        # Default styling for HUD elements
        self.style = {
            "font_A": "Assets/Hud/Font/KiwiSoda.ttf",
            "font_B": "Arial",  
            }


        
        # Initialize and organize components
        self.setup_components()

    def setup_components(self):
        """ 
        Creates UIContainers for different screen regions and 
        pushes them onto the internal stack.
        """
        # --- 1. Top HUD (Score & Status) ---
        self.stats_container = UIContainer(size=(self.width, 80), position=(0, 10))
        
        self.score_box = DialogueBox(
            text=f"SCORE: {self.rules.score}",
            size=(220, 50),
            color=(30, 30, 30),
            text_color=(255, 255, 255)
        )
        
        # Centering the score box within the full-width container
        self.stats_container.add_element(self.score_box, align="center")
        
        # Push to the stack (Layer 0)
        self.push(self.stats_container)

    def update(self):
        """ 
        Synchronizes the UI text with the game rules data. 
        Called every game tick or frame depending on performance needs.
        """
        self.score_box.update_text(f"SCORE: {self.rules.score}")

    def draw(self, surface):
        """ 
        Optional: Override if you need background dimming or 
        specific HUD-wide effects before drawing the stack.
        """
        super().draw(surface)

    # Helper functions

    def font(self, size):
        ''' Get font, defaults to Arial '''
        font = ''
        try:
            font = pygame.font.SysFont(self.style["font_A"], size)
        except:
            font = pygame.font.SysFont(self.style["font_B"], size)
        return font