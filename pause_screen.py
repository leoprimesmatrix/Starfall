import pygame
import pygame_gui
from constants import *

class PauseScreen:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.resume_button = None
        self.quit_button = None
        self.pause_text = None
        self.pause_rect = None
        self.overlay = None
        self.is_visible = False
        self.setup_ui()
        self.hide()  # Hide UI elements initially
        
    def setup_ui(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        scale = get_scale_factor(screen_width, screen_height)

        # Store current visibility state
        was_visible = self.is_visible

        # Kill old elements if they exist
        if self.resume_button:
            self.resume_button.kill()
        if self.quit_button:
            self.quit_button.kill()
        
        # Calculate scaled dimensions
        button_width = int(BUTTON_WIDTH * scale)
        button_height = int(BUTTON_HEIGHT * scale)
        button_spacing = int(BUTTON_SPACING * scale)
        
        # Calculate center positions
        center_x = screen_width // 2
        center_y = screen_height // 2

        # Pause text
        font_size = int(TITLE_FONT_SIZE * scale)
        font = load_font(font_size)
        self.pause_text = font.render("MISSION PAUSED", True, WHITE)
        self.pause_rect = self.pause_text.get_rect(center=(center_x, center_y - int(100 * scale)))
        
        # Create resume button
        self.resume_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width//2,
                                    self.pause_rect.bottom + int(50 * scale),
                                    button_width, button_height),
            text="Resume Mission",
            manager=self.manager
        )
        
        # Create quit button
        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width//2,
                                     self.resume_button.relative_rect.bottom + button_spacing,
                                     button_width, button_height),
            text="Abort Mission",
            manager=self.manager
        )

        # Create overlay
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.fill(BLACK)
        self.overlay.set_alpha(128)  # Semi-transparent

        # Restore visibility state
        if was_visible:
            self.show()
        else:
            self.hide()
        
    def show(self):
        if self.resume_button:
            self.resume_button.show()
        if self.quit_button:
            self.quit_button.show()
        self.is_visible = True
            
    def hide(self):
        if self.resume_button:
            self.resume_button.hide()
        if self.quit_button:
            self.quit_button.hide()
        self.is_visible = False
        
    def draw(self, surface, game_state):
        if not self.is_visible:
            return
        # Draw semi-transparent overlay
        if self.overlay:
            surface.blit(self.overlay, (0, 0))
        
        # Draw "MISSION PAUSED" text
        if self.pause_text:
            surface.blit(self.pause_text, self.pause_rect)
        
    def handle_event(self, event, game_state):
        if not self.is_visible:
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.resume_button:
                game_state.change_state(STATE_PLAYING)
            elif event.ui_element == self.quit_button:
                game_state.change_state(STATE_TITLE)
        return True 