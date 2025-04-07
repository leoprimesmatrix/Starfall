import pygame
import pygame_gui
import random
import math
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
        
        # Animation properties
        self.title_scale = 1.0
        self.title_direction = 0.001
        self.title_max_scale = 1.05
        self.title_min_scale = 0.95
        
        # Background stars
        self.stars = []
        self.setup_stars()
        
        self.setup_ui()
        self.hide()  # Hide UI elements initially
        
    def setup_stars(self):
        """Setup animated background stars"""
        self.stars = []
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        for _ in range(40):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            size = random.uniform(0.5, 3)
            speed = random.uniform(0.2, 1.0)
            pulse_speed = random.uniform(0.02, 0.05)
            self.stars.append({
                'x': x,
                'y': y,
                'size': size,
                'base_size': size,
                'speed': speed,
                'pulse': random.uniform(0, 2 * math.pi),
                'pulse_speed': pulse_speed
            })
        
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
        self.title_text = font.render("SELECT MISSION", True, WHITE)
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
        # Mission names corresponding to the new storyline
        mission_names = [
            "Evacuation Protocol",
            "Mining Colony Defense",
            "Orbital Station Rescue",
            "Supply Line Protection",
            "Final Stand"
        ]
        
        for row in range(LEVEL_ROWS):
            for col in range(LEVEL_COLS):
                if level_num <= 5:  # We have 5 levels/missions
                    x = start_x + col * (button_size + spacing)
                    y = start_y + row * (button_size + spacing)
                    button = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect(x, y, button_size, button_size),
                        text=f'{mission_names[level_num-1]}',
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
        
        # Setup star animations for new size
        self.setup_stars()

        # Restore visibility state
        if was_visible:
            self.show()
        else:
            self.hide()
    
    def update_animation(self):
        """Update all animations"""
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
            
        # Draw animated background stars
        for star in self.stars:
            pygame.draw.circle(
                surface, 
                WHITE, 
                (int(star['x']), int(star['y'])), 
                star['size']
            )
        
        # Draw animated title
        if self.title_text:
            # Create scaled version of the title
            scaled_width = int(self.title_text.get_width() * self.title_scale)
            scaled_height = int(self.title_text.get_height() * self.title_scale)
            scaled_title = pygame.transform.scale(self.title_text, (scaled_width, scaled_height))
            
            # Update the rect to center the scaled title
            scaled_rect = scaled_title.get_rect(center=self.title_rect.center)
            surface.blit(scaled_title, scaled_rect)
        
        # Draw level availability indicators
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        scale = get_scale_factor(screen_width, screen_height)
        
        for i, button in enumerate(self.level_buttons):
            level_num = i + 1
            is_available = game_state.is_level_available(level_num)
            
            rect = button.relative_rect
            
            # Draw availability indicator
            indicator_color = GREEN if is_available else RED
            indicator_radius = int(10 * scale)
            indicator_x = rect.right - indicator_radius // 2
            indicator_y = rect.top + indicator_radius // 2
            
            # Draw a pulsing glow for available levels
            if is_available and ANIMATION_ENABLED:
                # Create a pulsing glow effect
                pulse_value = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.003)
                glow_radius = int(indicator_radius * 1.5 * pulse_value) + indicator_radius
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                
                # Draw the glow as a gradient circle
                for r in range(glow_radius, 0, -1):
                    alpha = max(0, int(100 * (1 - r / glow_radius)))
                    pygame.draw.circle(glow_surface, (*indicator_color, alpha), 
                                     (glow_radius, glow_radius), r)
                                     
                glow_rect = glow_surface.get_rect(center=(indicator_x, indicator_y))
                surface.blit(glow_surface, glow_rect)
            
            # Draw a solid indicator in all cases
            pygame.draw.circle(surface, indicator_color, (indicator_x, indicator_y), indicator_radius)
    
    def handle_event(self, event, game_state):
        if not self.is_visible:
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_button:
                # Use transition when returning to title
                if hasattr(game_state.game, 'change_state_with_transition'):
                    game_state.game.change_state_with_transition(STATE_TITLE)
                else:
                    game_state.change_state(STATE_TITLE)
            else:
                for i, button in enumerate(self.level_buttons):
                    if event.ui_element == button:
                        level_num = i + 1
                        if game_state.is_level_available(level_num):
                            game_state.set_current_level(level_num)
                            # Use transition when starting a level
                            if hasattr(game_state.game, 'change_state_with_transition'):
                                game_state.game.change_state_with_transition(STATE_PLAYING)
                            else:
                                game_state.change_state(STATE_PLAYING)
                        break
        return True 