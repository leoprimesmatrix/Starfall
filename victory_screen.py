import pygame
import pygame_gui
from constants import *

class VictoryScreen:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.menu_button = None
        self.victory_text = None
        self.victory_rect = None
        self.score_text = None
        self.score_rect = None
        self.congrats_text = None
        self.congrats_rect = None
        self.overlay = None
        self.is_visible = False
        self.setup_ui()
        self.hide()  # Hide UI elements initially
        
    def setup_ui(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        scale = get_scale_factor(screen_width, screen_height)

        was_visible = self.is_visible

        if self.menu_button:
            self.menu_button.kill()
        
        button_width = int(BUTTON_WIDTH * scale)
        button_height = int(BUTTON_HEIGHT * scale)
        
        center_x = screen_width // 2
        center_y = screen_height // 2

        # Victory text
        vic_font_size = int(TITLE_FONT_SIZE * scale)
        vic_font = load_font(vic_font_size)
        self.victory_text = vic_font.render("VICTORY ACHIEVED", True, YELLOW)
        self.victory_rect = self.victory_text.get_rect(center=(center_x, center_y - int(150 * scale)))

        # Congratulations text
        congrats_font_size = int(SUBTITLE_FONT_SIZE * scale)
        congrats_font = load_font(congrats_font_size)
        self.congrats_text = congrats_font.render("The Kryll Command Carrier is destroyed. Earth is safe... for now.", True, WHITE)
        self.congrats_rect = self.congrats_text.get_rect(center=(center_x, self.victory_rect.bottom + int(30 * scale)))

        # Score text (needs game_state, will update in draw)
        self.score_font = load_font(int(SUBTITLE_FONT_SIZE * scale))
        self.score_rect = pygame.Rect(center_x, self.congrats_rect.bottom + int(20 * scale), 0, 0)
        
        # Create menu button
        self.menu_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     self.score_rect.bottom + int(80 * scale),
                                     button_width, button_height),
            text='Return to Command',
            manager=self.manager
        )

        # Create overlay (subtle, maybe blue)
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.fill(BLUE) 
        self.overlay.set_alpha(64)  # Very subtle blue overlay

        if was_visible:
            self.show()
        else:
            self.hide()
        
    def show(self):
        if self.menu_button:
            self.menu_button.show()
        self.is_visible = True
            
    def hide(self):
        if self.menu_button:
            self.menu_button.hide()
        self.is_visible = False
        
    def draw(self, surface, game_state):
        if not self.is_visible:
            return
        # Draw overlay
        if self.overlay:
            surface.blit(self.overlay, (0, 0))
        
        # Draw "VICTORY ACHIEVED" text
        if self.victory_text:
            surface.blit(self.victory_text, self.victory_rect)
            
        # Draw Congrats text
        if self.congrats_text:
            surface.blit(self.congrats_text, self.congrats_rect)
        
        # Update and draw score
        self.score_text = self.score_font.render(f"Final Score: {game_state.score}", True, WHITE)
        score_actual_rect = self.score_text.get_rect(center=self.score_rect.center)
        surface.blit(self.score_text, score_actual_rect)
        
    def handle_event(self, event, game_state):
        if not self.is_visible:
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.menu_button:
                game_state.reset_game() # Reset game when returning to title after victory
                game_state.change_state(STATE_TITLE)
        return True 