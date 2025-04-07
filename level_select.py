import pygame
import pygame_gui
from constants import *

class LevelSelect:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.level_buttons = []
        self.back_button = None
        self.title_text = None
        self.title_rect = None
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
        for button in self.level_buttons:
            button.kill()
        self.level_buttons = []
        if self.back_button:
            self.back_button.kill()
        
        # Title text
        title_font_size = int(TITLE_FONT_SIZE * scale)
        font = load_font(title_font_size)
        self.title_text = font.render("SELECT LEVEL", True, WHITE)
        self.title_rect = self.title_text.get_rect(centerx=screen_width//2, y=int(50 * scale))

        # Calculate scaled dimensions
        button_size = int(LEVEL_BUTTON_SIZE * scale)
        spacing = int(LEVEL_BUTTON_SPACING * scale)
        
        # Calculate total grid size
        grid_width = LEVEL_COLS * button_size + (LEVEL_COLS - 1) * spacing
        grid_height = LEVEL_ROWS * button_size + (LEVEL_ROWS - 1) * spacing
        
        # Calculate starting position to center the grid
        start_x = (screen_width - grid_width) // 2
        start_y = self.title_rect.bottom + int(50 * scale) # Position below title
        
        # Create level buttons in a grid
        level_num = 1
        for row in range(LEVEL_ROWS):
            for col in range(LEVEL_COLS):
                if level_num <= 5:  # We have 5 levels
                    x = start_x + col * (button_size + spacing)
                    y = start_y + row * (button_size + spacing)
                    button = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect(x, y, button_size, button_size),
                        text=f'Level {level_num}',
                        manager=self.manager
                    )
                    self.level_buttons.append(button)
                    level_num += 1
        
        # Create back button
        back_width = int(BUTTON_WIDTH * scale)
        back_height = int(BUTTON_HEIGHT * scale)
        back_margin = int(20 * scale)
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(back_margin, screen_height - back_height - back_margin,
                                    back_width, back_height),
            text='Back',
            manager=self.manager
        )

        # Restore visibility state
        if was_visible:
            self.show()
        else:
            self.hide()
        
    def show(self):
        for button in self.level_buttons:
            button.show()
        if self.back_button:
            self.back_button.show()
        self.is_visible = True
            
    def hide(self):
        for button in self.level_buttons:
            button.hide()
        if self.back_button:
            self.back_button.hide()
        self.is_visible = False
        
    def draw(self, surface, game_state):
        if not self.is_visible:
            return
        # Draw level select title
        if self.title_text:
            surface.blit(self.title_text, self.title_rect)
        
        # Update button appearances based on unlock status
        for i, button in enumerate(self.level_buttons):
            level = i + 1
            if not game_state.is_level_unlocked(level):
                button.disable()
                # Add a semi-transparent overlay
                rect = button.relative_rect
                overlay = pygame.Surface((rect.width, rect.height))
                overlay.fill(DARK_GRAY)
                overlay.set_alpha(128)
                surface.blit(overlay, rect)
            else:
                button.enable()
        
    def handle_event(self, event, game_state):
        if not self.is_visible:
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_button:
                game_state.change_state(STATE_TITLE)
            elif event.ui_element in self.level_buttons:
                level = self.level_buttons.index(event.ui_element) + 1
                if game_state.is_level_unlocked(level):
                    game_state.current_level = level
                    game_state.change_state(STATE_PLAYING)
        return True 