import pygame

class DialogueBox:
    ''' Acts as both an interact button or a label '''
    # Defaults
    _color = (50, 50, 50)
    _bounds = (300, 150)
    _size = (40, 40) # Not used, placeholder
    
    _text = "Oops, Something broke and now you have to debug lmao"
    _text_color = (255, 255, 255)
    _font = "Arial"
    _font_size = 24

    def __init__(self, text=_text, font=_font, font_size=_font_size, bounds=_bounds, color=_color, text_color=_color, callback=None):
        # Geometry (Position is now set by the Parent Container)
        self.rect = pygame.Rect(0, 0, bounds[0], bounds[1])
        self.hitbox_rect = self.rect.copy() 
        
        # State & Logic
        self.active = True
        self.is_hovered = False
        self.is_pressed = False
        self.text = text
        self.callback = callback

        # Aesthetics (Dynamic)
        self.styles = {
            "bg": color, 
            "bg_hover": tuple(min(c + 20, 255) for c in color), # Auto-calculate hover
            "bg_click": tuple(max(c - 20, 0) for c in color),   # Auto-calculate click
            "border_color": (200, 200, 200),
            "border_width": 2,
            "text_color": text_color,
        }
        self.update_font(font,font_size)



    def update_style(self, tag, value):
        """ bg, bg_hover, bg_click, border_color, border_width, text_color, font_name, font_size """
        if tag in self.styles:
            self.styles[tag] = value

    def update_styles(self, styles: dict):
        self.styles = {**self.styles, **styles}

    def update_text(self, new_text):
        """ Used by GameHUD to refresh scores or status. """
        self.text = new_text

    def update_font(self, font:str, size:int):
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.Font(font, size)

    def set_position(self, x, y):
        """Called by UIContainer.add_element to position the component."""
        self.rect.topleft = (x, y)
        self.hitbox_rect.topleft = (x, y)

    def _update_visual_state(self):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.hitbox_rect.collidepoint(mouse_pos)
        if not self.is_hovered:
            self.is_pressed = False

    def handle_event(self, event):
        if not self.active: return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hitbox_rect.collidepoint(event.pos):
                self.is_pressed = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.is_pressed and self.hitbox_rect.collidepoint(event.pos):
                    if self.callback: self.callback()
                self.is_pressed = False
        return True

    def draw(self, surface):
        if not self.active: return False
        self._update_visual_state()

        # Render Logic
        bg = self.styles["bg"]
        if self.is_pressed: bg = self.styles["bg_click"]
        elif self.is_hovered: bg = self.styles["bg_hover"]

        pygame.draw.rect(surface, bg, self.rect)
        pygame.draw.rect(surface, self.styles["border_color"], self.rect, self.styles["border_width"])

        # Render Text
        text_surf = self.font.render(self.text, True, self.styles["text_color"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)