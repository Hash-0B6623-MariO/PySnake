import pygame

class UIStack:
    def __init__(self):
        # Index 0 is bottom (background), -1 is top (pop-ups/overlays)
        self.elements = []

    def push(self, element):
        """Adds a UIContainer or UI element to the top of the stack."""
        self.elements.append(element)

    def pop(self):
        """Removes the top-most element."""
        if self.elements:
            return self.elements.pop()
        return None

    def handle_events(self, event):
        """
        Processes events from top to bottom (Reverse Painter's Algorithm).
        If a top-level container handles the event, we stop propagation.
        """
        # Iterate backwards to catch top-most elements first
        for element in reversed(self.elements):
            # Check if the element is a container with its own children
            if hasattr(element, 'elements'):
                # Containers handle their own internal child event loop
                if element.handle_event(event):
                    return True
            
            # Or if it's a standalone DialogueBox/Button
            elif hasattr(element, 'handle_event'):
                # Logic: If the mouse is over the element, let it try to handle the event
                mouse_pos = getattr(event, 'pos', pygame.mouse.get_pos())
                if hasattr(element, 'hitbox_rect') and element.hitbox_rect.collidepoint(mouse_pos):
                    element.handle_event(event)
                    return True 
                    
        return False

    def draw(self, surface):
        """Draws elements from bottom to top so overlays appear on top."""
        for element in self.elements:
            # We assume containers and boxes have a .draw() method
            element.draw(surface)