import pygame
import pygame_gui
from constants import *

class GameOverScreen:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.play_again_button = None
        self.menu_button = None
        self.game_over_text = None
        self.game_over_rect = None
        self.score_text = None
        self.score_rect = None
        self.hint_text = None
        self.hint_rect = None
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
        if self.play_again_button:
            self.play_again_button.kill()
        if self.menu_button:
            self.menu_button.kill()
        
        # Calculate scaled dimensions
        button_width = int(BUTTON_WIDTH * scale)
        button_height = int(BUTTON_HEIGHT * scale)
        button_spacing = int(BUTTON_SPACING * scale)
        
        # Calculate center positions
        center_x = screen_width // 2
        center_y = screen_height // 2

        # Game Over text
        go_font_size = int(TITLE_FONT_SIZE * scale)
        go_font = load_font(go_font_size)
        self.game_over_text = go_font.render("MISSION FAILED", True, RED)
        self.game_over_rect = self.game_over_text.get_rect(center=(center_x, center_y - int(150 * scale)))

        # Score text (needs game_state, will update in draw)
        self.score_font = load_font(int(SUBTITLE_FONT_SIZE * scale))
        self.score_rect = pygame.Rect(center_x, self.game_over_rect.bottom + int(20 * scale), 0, 0)
        
        # Create play again button
        self.play_again_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     self.score_rect.bottom + int(80 * scale),
                                     button_width, button_height),
            text='Retry Mission',
            manager=self.manager
        )
        
        # Create menu button
        self.menu_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     self.play_again_button.relative_rect.bottom + button_spacing,
                                     button_width, button_height),
            text='Return to Command',
            manager=self.manager
        )

        # Hint text
        hint_font_size = int(24 * scale)
        hint_font = load_font(hint_font_size)
        self.hint_text = hint_font.render("Press R to restart", True, WHITE)
        self.hint_rect = self.hint_text.get_rect(center=(center_x, self.menu_button.relative_rect.bottom + int(50 * scale)))

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
        if self.play_again_button:
            self.play_again_button.show()
        if self.menu_button:
            self.menu_button.show()
        self.is_visible = True
            
    def hide(self):
        if self.play_again_button:
            self.play_again_button.hide()
        if self.menu_button:
            self.menu_button.hide()
        self.is_visible = False
        
    def draw(self, surface, game_state):
        if not self.is_visible:
            return
        # Draw semi-transparent overlay
        if self.overlay:
            surface.blit(self.overlay, (0, 0))
        
        # Draw "GAME OVER" text
        if self.game_over_text:
            surface.blit(self.game_over_text, self.game_over_rect)
        
        # Update and draw score
        self.score_text = self.score_font.render(f"Final Score: {game_state.score}", True, WHITE)
        score_actual_rect = self.score_text.get_rect(center=self.score_rect.center)
        surface.blit(self.score_text, score_actual_rect)
        
        # Draw restart hint
        if self.hint_text:
            surface.blit(self.hint_text, self.hint_rect)
        
    def handle_event(self, event, game_state):
        if not self.is_visible:
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.play_again_button:
                game_state.reset_game()
                game_state.change_state(STATE_PLAYING)
            elif event.ui_element == self.menu_button:
                game_state.change_state(STATE_TITLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game_state.reset_game()
                game_state.change_state(STATE_PLAYING)
        return True 