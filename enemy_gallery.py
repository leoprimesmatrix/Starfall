import pygame
import pygame_gui
import random
from constants import *
from game_objects import Enemy

class EnemyGallery:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.is_visible = False
        self.back_button = None
        self.prev_button = None
        self.next_button = None
        self.title_text = None
        self.title_rect = None
        self.overlay = None
        
        # Enemy gallery data
        self.current_enemy_index = 0
        self.enemy_types = ENEMY_TYPES
        self.current_enemy = None
        self.enemy_display = None
        
        self.setup_ui()
        self.hide()  # Hide UI elements initially
        self.update_enemy_display()
        
    def setup_ui(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        scale = get_scale_factor(screen_width, screen_height)

        # Store current visibility state
        was_visible = self.is_visible

        # Kill old elements if they exist
        if self.back_button:
            self.back_button.kill()
        if self.prev_button:
            self.prev_button.kill()
        if self.next_button:
            self.next_button.kill()
        
        # Calculate scaled dimensions
        button_width = int(BUTTON_WIDTH * 0.7 * scale)
        button_height = int(BUTTON_HEIGHT * scale)
        arrow_button_size = int(50 * scale)
        
        # Title
        title_font_size = int(TITLE_FONT_SIZE * 0.8 * scale)
        title_font = load_font(title_font_size)
        self.title_text = title_font.render("KRYLL FORCES INTELLIGENCE", True, YELLOW)
        self.title_rect = self.title_text.get_rect(center=(screen_width//2, int(80 * scale)))
        
        # Create back button
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(int(40 * scale), 
                                     screen_height - button_height - int(40 * scale),
                                     button_width, button_height),
            text='Back',
            manager=self.manager
        )
        
        # Create prev/next arrow buttons
        self.prev_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(int(40 * scale),
                                     screen_height // 2 - arrow_button_size // 2,
                                     arrow_button_size, arrow_button_size),
            text='<',
            manager=self.manager
        )
        
        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(screen_width - arrow_button_size - int(40 * scale),
                                     screen_height // 2 - arrow_button_size // 2,
                                     arrow_button_size, arrow_button_size),
            text='>',
            manager=self.manager
        )
        
        # Create overlay
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.fill(BLACK)
        
        # Restore visibility state
        if was_visible:
            self.show()
        else:
            self.hide()
    
    def update_enemy_display(self):
        # Create a sample enemy of the selected type for display
        enemy_type = self.enemy_types[self.current_enemy_index]
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Position the enemy at a fixed position in the display surface (will be drawn there later)
        self.current_enemy = Enemy(250, 150, enemy_type)  # Fixed position within the display surface
        
        # Create display surface
        scale = get_scale_factor(screen_width, screen_height)
        display_width = int(500 * scale)
        display_height = int(400 * scale)
        
        self.enemy_display = pygame.Surface((display_width, display_height), pygame.SRCALPHA)
        
        # Calculate position for the enemy_display
        self.enemy_display_rect = self.enemy_display.get_rect(center=(screen_width // 2, screen_height // 2))
        
    def show(self):
        if self.back_button:
            self.back_button.show()
        if self.prev_button:
            self.prev_button.show()
        if self.next_button:
            self.next_button.show()
        self.is_visible = True
            
    def hide(self):
        if self.back_button:
            self.back_button.hide()
        if self.prev_button:
            self.prev_button.hide()
        if self.next_button:
            self.next_button.hide()
        self.is_visible = False
        
    def draw(self, surface):
        if not self.is_visible:
            return
            
        # Draw overlay background
        if self.overlay:
            surface.fill(BLACK)  # Fill with black
            
            # Draw a fancy background with stars
            for _ in range(100):
                x = random.randint(0, surface.get_width())
                y = random.randint(0, surface.get_height())
                size = random.randint(1, 3)
                brightness = random.randint(100, 255)
                color = (brightness, brightness, brightness)
                pygame.draw.circle(surface, color, (x, y), size)
        
        # Draw title
        if self.title_text:
            surface.blit(self.title_text, self.title_rect)
        
        # Draw enemy info display
        if self.current_enemy and self.enemy_display:
            # Clear the display surface
            self.enemy_display.fill((0, 0, 0, 0))
            
            # Get screen dimensions and scale
            screen_width = surface.get_width()
            screen_height = surface.get_height()
            scale = get_scale_factor(screen_width, screen_height)
            
            # Draw enemy preview
            self.current_enemy.draw(self.enemy_display)
            
            # Draw enemy stats
            font_size = int(24 * scale)
            stat_font = load_font(font_size)
            title_font = load_font(int(32 * scale))
            
            # Name and type at the top
            enemy_name = f"KRYLL {self.current_enemy.type}"
            name_text = title_font.render(enemy_name, True, RED)
            name_rect = name_text.get_rect(center=(self.enemy_display.get_width() // 2, 50))
            self.enemy_display.blit(name_text, name_rect)
            
            # Add description below the name
            description = ENEMY_DESCRIPTIONS.get(self.current_enemy.type, "No description available.")
            description_y = name_rect.bottom + 30
            desc_text = stat_font.render(description, True, LIGHT_GRAY)
            desc_rect = desc_text.get_rect(center=(self.enemy_display.get_width() // 2, description_y))
            self.enemy_display.blit(desc_text, desc_rect)
            
            # Draw a health bar below the description
            health_bar_width = 200
            health_bar_height = 20
            health_bar_x = (self.enemy_display.get_width() - health_bar_width) // 2
            health_bar_y = description_y + 50
            
            # Health bar label
            health_text = stat_font.render("Health", True, WHITE)
            health_text_rect = health_text.get_rect(center=(health_bar_x + health_bar_width // 2, health_bar_y - 20))
            self.enemy_display.blit(health_text, health_text_rect)
            
            # Background of health bar
            pygame.draw.rect(self.enemy_display, DARK_GRAY, 
                           (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
            
            # Filled portion of health bar
            health_percentage = self.current_enemy.health / self.current_enemy.max_health
            current_width = int(health_bar_width * health_percentage)
            pygame.draw.rect(self.enemy_display, RED, 
                           (health_bar_x, health_bar_y, current_width, health_bar_height))
            
            # Draw stats in a more organized layout
            stats_x = int(self.enemy_display.get_width() * 0.1)  # Start at 10% of width
            stats_width = int(self.enemy_display.get_width() * 0.8)  # Use 80% of width
            stats_y = health_bar_y + health_bar_height + 30  # Space after health bar
            
            # Two-column layout for stats
            left_stats = [
                f"Speed: {self.current_enemy.speed}",
                f"Size: {self.current_enemy.width}x{self.current_enemy.height}"
            ]
            
            right_stats = [
                f"Damage: {self.current_enemy.get_damage()}",
                f"Ability: {self.current_enemy.get_abilities()}"
            ]
            
            # Draw left column
            for stat in left_stats:
                stat_text = stat_font.render(stat, True, WHITE)
                self.enemy_display.blit(stat_text, (stats_x, stats_y))
                stats_y += 40
                
            # Reset Y position for right column
            stats_y = health_bar_y + health_bar_height + 30
            
            # Draw right column (starts at center + a bit)
            right_x = stats_x + stats_width // 2 + 20
            for stat in right_stats:
                stat_text = stat_font.render(stat, True, WHITE)
                self.enemy_display.blit(stat_text, (right_x, stats_y))
                stats_y += 40
            
            # Draw enemy counter
            counter_text = load_font(int(18 * scale)).render(
                f"Enemy {self.current_enemy_index + 1} of {len(self.enemy_types)}", 
                True, WHITE)
            counter_rect = counter_text.get_rect(
                center=(self.enemy_display.get_width() // 2, self.enemy_display.get_height() - 30))
            self.enemy_display.blit(counter_text, counter_rect)
            
            # Draw the enemy display surface to the main surface
            surface.blit(self.enemy_display, self.enemy_display_rect)
        
    def handle_event(self, event, game_state):
        if not self.is_visible:
            return True
            
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_button:
                game_state.change_state(STATE_TITLE)
            elif event.ui_element == self.prev_button:
                self.current_enemy_index = (self.current_enemy_index - 1) % len(self.enemy_types)
                self.update_enemy_display()
            elif event.ui_element == self.next_button:
                self.current_enemy_index = (self.current_enemy_index + 1) % len(self.enemy_types)
                self.update_enemy_display()
                
        # Also close with Escape key
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_state.change_state(STATE_TITLE)
            
        return True 