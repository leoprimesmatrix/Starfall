import pygame
import pygame_gui
from constants import *

class TitleScreen:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.title_text = None
        self.subtitle_text = None
        self.begin_button = None
        self.gallery_button = None
        self.exit_button = None
        self.is_visible = False
        self.setup_ui()
        self.hide() # Hide UI elements initially

    def setup_ui(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        scale = get_scale_factor(screen_width, screen_height)

        # Store current visibility state
        was_visible = self.is_visible

        # Kill old elements if they exist
        if self.begin_button:
            self.begin_button.kill()
        if self.gallery_button:
            self.gallery_button.kill()
        if self.exit_button:
            self.exit_button.kill()

        # Calculate scaled dimensions and positions
        button_width = int(BUTTON_WIDTH * scale)
        button_height = int(BUTTON_HEIGHT * scale)
        button_spacing = int(BUTTON_SPACING * scale)
        center_x = screen_width // 2
        center_y = screen_height // 2

        # Title text
        title_font_size = int(TITLE_FONT_SIZE * scale)
        self.title_font = load_font(title_font_size)
        self.title_text = self.title_font.render("STARFALL", True, WHITE)
        self.title_rect = self.title_text.get_rect(center=(center_x, center_y - int(100 * scale)))

        # Subtitle text
        subtitle_font_size = int(SUBTITLE_FONT_SIZE * scale)
        self.subtitle_font = load_font(subtitle_font_size)
        self.subtitle_text = self.subtitle_font.render("THE KRYLL INVASION", True, LIGHT_GRAY)
        self.subtitle_rect = self.subtitle_text.get_rect(center=(center_x, self.title_rect.bottom + int(10 * scale)))

        # Create buttons
        button_y = self.subtitle_rect.bottom + int(50 * scale)
        
        # Begin button
        self.begin_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                    button_y,
                                    button_width, button_height),
            text='Begin Game',
            manager=self.manager
        )
        
        # Enemy Gallery button
        button_y += button_height + button_spacing
        self.gallery_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                    button_y,
                                    button_width, button_height),
            text='Enemy Intelligence',
            manager=self.manager
        )
        
        # Exit button
        button_y += button_height + button_spacing
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                    button_y,
                                    button_width, button_height),
            text='Exit Game',
            manager=self.manager
        )

        # Restore visibility state
        if was_visible:
            self.show()
        else:
            self.hide()

    def show(self):
        if self.begin_button:
            self.begin_button.show()
        if self.gallery_button:
            self.gallery_button.show()
        if self.exit_button:
            self.exit_button.show()
        self.is_visible = True

    def hide(self):
        if self.begin_button:
            self.begin_button.hide()
        if self.gallery_button:
            self.gallery_button.hide()
        if self.exit_button:
            self.exit_button.hide()
        self.is_visible = False

    def draw(self, surface):
        if not self.is_visible:
             return
        # Draw text
        if self.title_text:
             surface.blit(self.title_text, self.title_rect)
        if self.subtitle_text:
             surface.blit(self.subtitle_text, self.subtitle_rect)

    def handle_event(self, event, game_state):
        if not self.is_visible:
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.begin_button:
                game_state.change_state(STATE_LEVEL_SELECT)
            elif event.ui_element == self.gallery_button:
                game_state.change_state(STATE_ENEMY_GALLERY)
            elif event.ui_element == self.exit_button:
                return False # Signal to quit the game
        return True
