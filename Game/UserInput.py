from UI.DialogueBox import DialogueBox
from collections import deque

import pygame

class InputHandler:
    def __init__(self, keybinds:dict):
        # Action Dictionary, compiles every keybind from every class that has one
        self._key_mapping = keybinds # Compilation of all keybinds, labeled
        self._keybinds = self.merge(keybinds) # Actual key-to-function mapping
        self.move_buffer = deque(maxlen=2)
        self.paused = False

    # Have this reusable for dynamic rebinding
    def merge(self, keybinds:dict):
        """Merge another keybind dictionary into this one."""
        keybind_map = {}
        for tag, keybind in keybinds:
            if keybind.keys() not in self._keybinds.keys(): # Could be unoptimized
                keybind_map.update(keybind)
            else:
                raise KeyError(f"Keybind {tag} for {keybind.keys()} already exists.")
        return keybind_map

    def bind_action(self, key, func):
        """Bind a specific pygame key to a function."""
        self._keybinds[key] = func

    def handle_keydown(self, key):
        """Redirected input from the InputMask."""
        if key in self._keybinds:
            self._keybinds[key]()

class InputMask(DialogueBox):
    def __init__(self, screen_size, input_handler):
        # Create an invisible box covering the whole screen
        super().__init__(text="", bounds=screen_size, color=(0,0,0,0))
        self.handler = input_handler

    def handle_event(self, event):
        """Picks up all actions and redirects them to the handler."""
        if event.type == pygame.KEYDOWN:
            self.handler.handle_keydown(event.key)
        # Return False so it never 'captures' the mouse from other UI
        return False