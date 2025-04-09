import pygame
import pygame_gui
from constants import *

class DebugMenu:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.is_visible = False
        self.heal_button = None
        self.shield_button = None
        self.unlock_all_button = None
        self.mute_button = None
        self.close_button = None
        self.rapid_fire_button = None
        self.title_text = None
        self.title_rect = None
        self.overlay = None
        self.setup_ui()
        self.hide()  # Hide UI elements initially
        
        # Debug state
        self.muted = False
        self.rapid_fire = False
        
    def setup_ui(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        scale = get_scale_factor(screen_width, screen_height)

        # Store current visibility state
        was_visible = self.is_visible

        # Kill old elements if they exist
        if self.heal_button:
            self.heal_button.kill()
        if self.shield_button:
            self.shield_button.kill()
        if self.unlock_all_button:
            self.unlock_all_button.kill()
        if self.mute_button:
            self.mute_button.kill()
        if self.close_button:
            self.close_button.kill()
        if self.rapid_fire_button:
            self.rapid_fire_button.kill()
        
        # Calculate scaled dimensions
        button_width = int(BUTTON_WIDTH * scale)
        button_height = int(BUTTON_HEIGHT * scale)
        button_spacing = int(BUTTON_SPACING * 0.7 * scale)  # Less spacing for debug menu
        
        # Calculate center positions
        center_x = screen_width // 2
        center_y = screen_height // 2

        # Debug Menu title
        title_font_size = int(TITLE_FONT_SIZE * 0.8 * scale)  # Slightly smaller than title
        title_font = load_font(title_font_size)
        self.title_text = title_font.render("DEBUG MENU", True, GREEN)
        self.title_rect = self.title_text.get_rect(center=(center_x, center_y - int(150 * scale)))

        # Create buttons
        y_position = self.title_rect.bottom + int(30 * scale)
        
        # Heal button
        self.heal_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     y_position,
                                     button_width, button_height),
            text='Heal Player',
            manager=self.manager
        )
        
        # Shield button
        y_position += button_height + button_spacing
        self.shield_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     y_position,
                                     button_width, button_height),
            text='Replenish Shield',
            manager=self.manager
        )
        
        # Unlock all levels button
        y_position += button_height + button_spacing
        self.unlock_all_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     y_position,
                                     button_width, button_height),
            text='Unlock All Levels',
            manager=self.manager
        )
        
        # Rapid Fire button
        y_position += button_height + button_spacing
        self.rapid_fire_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     y_position,
                                     button_width, button_height),
            text='Toggle Rapid Fire',
            manager=self.manager
        )
        
        # Mute button
        y_position += button_height + button_spacing
        self.mute_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     y_position,
                                     button_width, button_height),
            text='Toggle Sound',
            manager=self.manager
        )
        
        # Close button
        y_position += button_height + button_spacing
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - button_width // 2,
                                     y_position,
                                     button_width, button_height),
            text='Close Menu',
            manager=self.manager
        )

        # Create overlay
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.fill(BLACK)
        self.overlay.set_alpha(192)  # Darker than pause menu

        # Restore visibility state
        if was_visible:
            self.show()
        else:
            self.hide()
        
    def show(self):
        if self.heal_button:
            self.heal_button.show()
        if self.shield_button:
            self.shield_button.show()
        if self.unlock_all_button:
            self.unlock_all_button.show()
        if self.mute_button:
            self.mute_button.show()
        if self.rapid_fire_button:
            self.rapid_fire_button.show()
        if self.close_button:
            self.close_button.show()
        self.is_visible = True
            
    def hide(self):
        if self.heal_button:
            self.heal_button.hide()
        if self.shield_button:
            self.shield_button.hide()
        if self.unlock_all_button:
            self.unlock_all_button.hide()
        if self.mute_button:
            self.mute_button.hide()
        if self.rapid_fire_button:
            self.rapid_fire_button.hide()
        if self.close_button:
            self.close_button.hide()
        self.is_visible = False
        
    def draw(self, surface):
        if not self.is_visible:
            return
            
        # Draw semi-transparent overlay
        if self.overlay:
            surface.blit(self.overlay, (0, 0))
        
        # Draw debug menu title
        if self.title_text:
            surface.blit(self.title_text, self.title_rect)
        
    def handle_event(self, event, game_state, playing_screen):
        if not self.is_visible:
            return True
            
        # Store the previous state to know where to return
        previous_state = game_state.previous_state if hasattr(game_state, 'previous_state') else STATE_PLAYING
            
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Heal player
            if event.ui_element == self.heal_button and playing_screen.player:
                playing_screen.player.health = PLAYER_HEALTH
                
            # Replenish shield
            elif event.ui_element == self.shield_button and playing_screen.player:
                playing_screen.player.shield = PLAYER_SHIELD_MAX
                
            # Unlock all levels
            elif event.ui_element == self.unlock_all_button:
                for level in range(1, 6):  # Levels 1-5
                    game_state.unlock_level(level)
                    
            # Toggle rapid fire
            elif event.ui_element == self.rapid_fire_button:
                self.rapid_fire = not self.rapid_fire
                # Update button text
                if self.rapid_fire:
                    self.rapid_fire_button.set_text("Disable Rapid Fire")
                else:
                    self.rapid_fire_button.set_text("Enable Rapid Fire")
                    
            # Toggle mute
            elif event.ui_element == self.mute_button:
                self.muted = not self.muted
                self.toggle_mute()
                # Update button text
                if self.muted:
                    self.mute_button.set_text("Unmute Sound")
                else:
                    self.mute_button.set_text("Mute Sound")
                    
            # Close menu
            elif event.ui_element == self.close_button:
                # Return to the previous state (either title or playing)
                if previous_state == STATE_TITLE:
                    game_state.change_state(STATE_TITLE)
                else:
                    game_state.change_state(STATE_PLAYING)
                
        # Also close with Escape key
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Return to the previous state (either title or playing)
            if previous_state == STATE_TITLE:
                game_state.change_state(STATE_TITLE)
            else:
                game_state.change_state(STATE_PLAYING)
            
        return True
        
    def toggle_mute(self):
        if self.muted:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause() 