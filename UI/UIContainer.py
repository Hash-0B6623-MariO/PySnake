import pygame

class UIContainer:
    def __init__(self, position=(0, 0), size=(400, 400), bg_color=(40, 40, 40, 180)):
        self.rect = pygame.Rect(position, size)
        # hitbox_rect is used by UIStack to check if this layer is being interacted with
        self.hitbox_rect = self.rect.copy() 
        self.active = True # Default to True for HUD layers
        
        self.bg_color = bg_color 
        self.border_color = (100, 100, 100)
        self.elements = [] 

    def add_element(self, element, relative_pos=(0, 0), align=None):
        """
        Adds a DialogueBox.
        If align="center", it ignores relative_pos and centers the element 
        within the container's area.
        """
        if align == "center":
            # Center math: (Parent_Center) - (Child_Half_Size)
            abs_x = self.rect.centerx - (element.rect.width // 2)
            abs_y = self.rect.centery - (element.rect.height // 2)
        else:
            abs_x = self.rect.x + relative_pos[0]
            abs_y = self.rect.y + relative_pos[1]
        
        # Use the setter method we defined in the updated DialogueBox
        element.set_position(abs_x, abs_y)
        self.elements.append(element)

    def handle_event(self, event):
        """
        Passes events to children. Returns True if the event was 
        handled or if the mouse is over the container.
        """
        if not self.active:
            return False

        # Determine if mouse is over the container
        mouse_pos = getattr(event, 'pos', pygame.mouse.get_pos())
        is_over = self.rect.collidepoint(mouse_pos)

        # Pass events to children (Top to Bottom)
        for element in reversed(self.elements):
            element.handle_event(event)

        # Return True if we are hovering/clicking this container 
        # to prevent game logic from firing (e.g., snake turning)
        return is_over

    def draw(self, surface):
        if not self.active: return

        # Handle Alpha transparency if needed
        if len(self.bg_color) == 4:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            overlay.fill(self.bg_color)
            surface.blit(overlay, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect)
            
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        for element in self.elements:
            element.draw(surface)

    def show(self):
        self.active = True
    def hide(self):
        self.active = False