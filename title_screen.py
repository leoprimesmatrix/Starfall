import pygame
import pygame_gui
import random
import math
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
        self.title_font = None
        self.subtitle_font = None
        self.title_rect = None
        self.subtitle_rect = None
        self.is_visible = False
        self.stars = []
        
        # Animation properties
        self.title_scale = 1.0
        self.title_min_scale = 0.95
        self.title_max_scale = 1.05
        self.title_direction = 0.002
        
        # Debug hint text
        self.debug_hint_text = None
        self.debug_hint_rect = None
        
        self.setup_stars()
        self.setup_ui()
        self.hide() # Hide UI elements initially
        
    def setup_stars(self):
        # Create animated stars in the background
        self.stars = []
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        for _ in range(50):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            size = random.uniform(0.5, 3)
            speed = random.uniform(0.2, 1.0)
            pulse_speed = random.uniform(0.02, 0.05)
            
            # Randomly select a star color (white with slight tints)
            brightness = random.randint(200, 255)
            blue_tint = random.randint(0, 30)  # Some stars have slight blue tint
            yellow_tint = random.randint(0, 20)  # Some stars have slight yellow tint
            color = (brightness, brightness - yellow_tint, brightness - blue_tint)
            
            self.stars.append({
                'x': x,
                'y': y,
                'size': size,
                'base_size': size,
                'speed': speed,
                'pulse': 0,
                'pulse_speed': pulse_speed,
                'color': color
            })

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
        
        # Debug hint text (only if DEBUG_MODE is enabled)
        if DEBUG_MODE:
            debug_font_size = int(16 * scale)
            debug_font = load_font(debug_font_size)
            self.debug_hint_text = debug_font.render("Press G for Debug Menu", True, GRAY)
            self.debug_hint_rect = self.debug_hint_text.get_rect(bottomright=(screen_width - int(10 * scale), screen_height - int(10 * scale)))
        else:
            self.debug_hint_text = None
            self.debug_hint_rect = None
        
        # Setup star animations again for the new size
        self.setup_stars()

        # Restore visibility state
        if was_visible:
            self.show()
        else:
            self.hide()

    def update_animation(self):
        if not self.is_visible:
            return
            
        # Animate title scale
        self.title_scale += self.title_direction
        if self.title_scale > self.title_max_scale:
            self.title_scale = self.title_max_scale
            self.title_direction = -abs(self.title_direction)
        elif self.title_scale < self.title_min_scale:
            self.title_scale = self.title_min_scale
            self.title_direction = abs(self.title_direction)
            
        # Animate background stars
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        for star in self.stars:
            # Move stars slowly upward
            star['y'] -= star['speed']
            if star['y'] < 0:
                star['y'] = screen_height
                star['x'] = random.randint(0, screen_width)
                
            # Make stars pulse
            star['pulse'] += star['pulse_speed']
            if star['pulse'] > 2 * math.pi:
                star['pulse'] -= 2 * math.pi
                
            # Calculate current size based on pulse
            star['size'] = star['base_size'] * (1 + 0.3 * math.sin(star['pulse']))

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
        
        # Fill the background with black
        surface.fill(BLACK)
        
        # Draw animated background stars
        for star in self.stars:
            pygame.draw.circle(
                surface, 
                star['color'], 
                (int(star['x']), int(star['y'])), 
                int(star['size'])
            )
        
        # Draw animated title text with pulsing scale
        if self.title_text:
            # Create scaled version of the title
            scaled_width = int(self.title_text.get_width() * self.title_scale)
            scaled_height = int(self.title_text.get_height() * self.title_scale)
            scaled_title = pygame.transform.scale(self.title_text, (scaled_width, scaled_height))
            
            # Update the rect to center the scaled title
            scaled_rect = scaled_title.get_rect(center=self.title_rect.center)
            surface.blit(scaled_title, scaled_rect)
            
        # Draw subtitle with glow effect
        if self.subtitle_text:
            # Draw a subtle glow around the subtitle
            glow_surf = pygame.Surface((self.subtitle_text.get_width() + 10, self.subtitle_text.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (100, 100, 200, 20), glow_surf.get_rect(), border_radius=5)
            glow_rect = glow_surf.get_rect(center=self.subtitle_rect.center)
            surface.blit(glow_surf, glow_rect)
            
            # Draw the actual subtitle
            surface.blit(self.subtitle_text, self.subtitle_rect)
        
        # Draw debug hint if enabled
        if self.debug_hint_text and DEBUG_MODE:
            surface.blit(self.debug_hint_text, self.debug_hint_rect)

    def handle_event(self, event, game_state):
        if not self.is_visible:
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.begin_button:
                # Use transition when changing to level select
                if hasattr(game_state.game, 'change_state_with_transition'):
                    game_state.game.change_state_with_transition(STATE_LEVEL_SELECT)
                else:
                    game_state.change_state(STATE_LEVEL_SELECT)
            elif event.ui_element == self.gallery_button:
                # Use transition for enemy gallery
                if hasattr(game_state.game, 'change_state_with_transition'):
                    game_state.game.change_state_with_transition(STATE_ENEMY_GALLERY, "wipe_left")
                else:
                    game_state.change_state(STATE_ENEMY_GALLERY)
            elif event.ui_element == self.exit_button:
                return False # Signal to quit the game
        return True
