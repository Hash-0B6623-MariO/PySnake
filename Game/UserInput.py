from UI.DialogueBox import DialogueBox
from collections import deque

import pygame

class InputHandler:
    def __init__(self, keybinds: dict):
        self._key_mapping = keybinds 
        self._action_mapping = {}
        self.setActionMap(keybinds)
        
        self.input_queue = [] 
        self.paused = False

        # Strategy Dispatch Table: Map tags to internal logic methods
        self._evaluation_strategies = {
            "System": self._eval_system,
            "Movement": self._eval_movement,
            "Action": self._eval_standard
        }

    def setActionMap(self, keybinds: dict):
        """Compiles the keybinds into an internal map with metadata."""
        action_map = {}
        for tag, mapping in keybinds.items():
            for key, action in mapping.items():
                # Store as a tuple of (tag, function)
                action_map[key] = (tag, action)
        self._action_mapping = action_map

    def evaluate_tick(self):
        """Entry point for the recursive evaluation loop."""
        if not self.input_queue:
            return
            
        # Convert to a reversed list so we process from the latest input first
        pending = list(reversed(self.input_queue))
        self.input_queue.clear()
        
        self._process_recursive(pending, processed_tags=set())

    def _process_recursive(self, queue, processed_tags):
        """Recursively evaluates the input buffer until empty."""
        if not queue:
            return

        key = queue.pop(0) # Take the latest available key
        
        if key in self._action_mapping:
            tag, action = self._action_mapping[key]
            
            # Look up the strategy for this tag
            strategy = self._evaluation_strategies.get(tag, self._eval_standard)
            
            # Execute strategy; if it returns True, it might stop the loop (like Pause)
            should_interrupt = strategy(action, tag, processed_tags)
            
            if should_interrupt:
                return 

        # Recursive call for the next item in the buffer
        self._process_recursive(queue, processed_tags)

    # --- Strategy Implementations ---

    def _eval_system(self, action, tag, processed_tags):
        """System actions (like Pause) execute immediately and interrupt everything."""
        action()
        return True # Interrupt the rest of the buffer

    def _eval_movement(self, action, tag, processed_tags):
        """Movement rule: Only execute the latest movement found in the tick."""
        if tag not in processed_tags and not self.paused:
            is_illegal = action()
            if not is_illegal:
                processed_tags.add(tag)
        return False

    def _eval_standard(self, action, tag, processed_tags):
        """Standard actions: Allow multiple, but perhaps only once per tag per tick."""
        if not self.paused:
            action()
        return False

    def handle_keydown(self, key):
        """Buffers the key."""
        if key not in self.input_queue:
            self.input_queue.append(key)

class InputMask(DialogueBox):
    def __init__(self, screen_size, input_handler):
        super().__init__(text="", bounds=screen_size, color=(0,0,0,0))
        self.handler = input_handler

    def handle_event(self, event):
        """ Blocks mouse bleed-through and buffers keys. """
        # Keyboard inputs are buffered for end-of-tick processing
        if event.type == pygame.KEYDOWN:
            self.handler.handle_keydown(event.key)
            return True # Consume to prevent other UI from double-triggering

        # Mouse blocking: Return True for mouse events to stop propagation
        mouse_events = (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION)
        if event.type in mouse_events:
            return True 

        return False