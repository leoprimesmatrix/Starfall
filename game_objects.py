import pygame
import math
import random
from constants import *

class Star:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = random.randint(1, 3)
        
    def update(self, screen_width, screen_height):
        self.y += self.speed
        if self.y > screen_height:
            self.y = 0
            self.x = random.randint(0, screen_width)
            
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size)

class Nebula:
    def __init__(self):
        self.base_color = (0, 0, 0) # Default, will be set
        self.y_pos = 0
        self.speed = 0.5 # Slow scroll speed
        self.surface = None

    def set_color_for_level(self, level):
        level_index = max(0, min(level - 1, len(NEBULA_COLORS) - 1))
        rgb_color = NEBULA_COLORS[level_index]
        self.base_color = rgb_color + (NEBULA_ALPHA,) # Add alpha
        self.surface = None # Force redraw with new color

    def update(self, screen_height):
        self.y_pos = (self.y_pos + self.speed) % screen_height

    def draw(self, surface):
        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Create the nebula surface if it doesn't exist or screen size changed
        if self.surface is None or self.surface.get_size() != (screen_width, screen_height * 2):
            self.surface = pygame.Surface((screen_width, screen_height * 2), pygame.SRCALPHA) # Use SRCALPHA for per-pixel alpha
            self.surface.fill(self.base_color) # Fill with the semi-transparent color
            # Optional: Add more complex drawing here later if needed

        # Draw the scrolling nebula
        surface.blit(self.surface, (0, self.y_pos - screen_height))
        surface.blit(self.surface, (0, self.y_pos))

class PlayerShip:
    def __init__(self):
        self.x = DEFAULT_WIDTH // 2 # Start relative to default size
        self.y = DEFAULT_HEIGHT * 2 // 3 # Start relative to default size
        self.speed = PLAYER_SPEED # Use constant
        self.width = 40
        self.height = 30
        self.health = PLAYER_HEALTH # Use constant
        self.max_health = PLAYER_HEALTH # Use constant
        self.shield = PLAYER_SHIELD_MAX  # Shield health
        self.max_shield = PLAYER_SHIELD_MAX  # Maximum shield health
        self.shoot_cooldown = 0
        self.damage_flash_timer = 0
        self.ship_name = "SF-22 Valiant" # Federation pilot ship name

        # Ability specific attributes
        self.active_ability = None
        self.ability_timer = 0
        self.has_shield = False  # This is for the ability shield (one-hit protection)
        self.piercing_active = False

        # Old PowerUp compatibility (can be removed if powerups are replaced by abilities)
        self.power_up_active = False
        self.power_up_timer = 0

    def move(self, dx, dy, screen_width, screen_height):
        # Use current screen dimensions for bounds
        self.x = max(self.width//2, min(screen_width - self.width//2, self.x + dx))
        self.y = max(self.height//2, min(screen_height - self.height//2, self.y + dy))
        
    def activate_ability(self, ability_id):
        if ability_id not in ABILITIES:
            return

        self.active_ability = ability_id
        ability_data = ABILITIES[ability_id]
        duration = ability_data['duration']

        if ability_id == ABILITY_RAPID_FIRE:
            self.ability_timer = duration
        elif ability_id == ABILITY_SHIELD:
            self.has_shield = True
            self.ability_timer = 0 # Shield doesn't use timer, but reset just in case
        elif ability_id == ABILITY_PIERCING:
            self.piercing_active = True
            self.ability_timer = duration

    def shoot(self):
        cooldown = LASER_COOLDOWN
        if self.active_ability == ABILITY_RAPID_FIRE:
            cooldown = LASER_COOLDOWN // 2 # Fire twice as fast

        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = cooldown # Apply potentially modified cooldown
            # PowerUp compatibility (can be removed/refactored)
            if self.power_up_active:
                return [
                    Laser(self.x - 10, self.y, -90, self.piercing_active),
                    Laser(self.x, self.y, -90, self.piercing_active),
                    Laser(self.x + 10, self.y, -90, self.piercing_active)
                ]
            else:
                return [Laser(self.x, self.y, -90, self.piercing_active)] # Pass piercing status
        return []
        
    def take_damage(self, amount):
        # First check for ability shield (complete damage negation)
        if self.has_shield:
            self.has_shield = False # Shield absorbs one hit
            self.active_ability = None # Deactivate shield ability
            # Add visual/sound effect for shield break here
            return False

        # Then check regular shield health
        if self.shield > 0:
            # Shield takes the damage first
            if amount <= self.shield:
                self.shield -= amount
                # Add visual/sound effect for shield damage here
                return False
            else:
                # Damage exceeds shield, shield is depleted
                # and remaining damage goes to health
                remaining_damage = amount - self.shield
                self.shield = 0
                self.health -= remaining_damage
                self.damage_flash_timer = 10  # Flash for 10 frames
                # Add visual/sound effect for shield break here
                return self.health <= 0

        # No shield, damage goes directly to health
        self.health -= amount
        self.damage_flash_timer = 10  # Flash for 10 frames
        # Add visual/sound effect for taking damage here
        
        # Return True if player is killed (health depleted), False otherwise
        return self.health <= 0
        
    def update(self):
        # Cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1

        # Ability Timer
        if self.ability_timer > 0:
            self.ability_timer -= 1
            if self.ability_timer <= 0:
                # Deactivate timed abilities
                if self.active_ability == ABILITY_RAPID_FIRE:
                    pass # Effect ends automatically via cooldown check
                elif self.active_ability == ABILITY_PIERCING:
                    self.piercing_active = False
                self.active_ability = None # Clear active ability

        # PowerUp compatibility
        if self.power_up_timer > 0:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.power_up_active = False
                
    def draw(self, surface):
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        scale = get_scale_factor(screen_width, screen_height)

        # Draw ship body
        points = [
            (self.x, self.y - self.height//2),  # Nose
            (self.x - self.width//2, self.y + self.height//2),  # Left wing
            (self.x + self.width//2, self.y + self.height//2)   # Right wing
        ]
        pygame.draw.polygon(surface, WHITE, points)

        # Draw ability Shield visual if active
        if self.has_shield:
            shield_radius = max(self.width, self.height) // 2 + 5
            pygame.draw.circle(surface, (100, 100, 255, 100), (int(self.x), int(self.y)), shield_radius, 2) # Thin blue circle
            
        # Draw regular shield glow based on shield amount
        if self.shield > 0:
            shield_alpha = min(150, int(100 * (self.shield / self.max_shield)) + 50)  # 50-150 alpha based on shield amount
            shield_radius = max(self.width, self.height) // 2 + 3
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 150, 255, shield_alpha), (shield_radius, shield_radius), shield_radius)
            surface.blit(shield_surface, (int(self.x - shield_radius), int(self.y - shield_radius)))

        # Draw health bar in top-left, below score
        bar_spacing = int(12 * scale)  # Space between bars
        bar_max_width = int(100 * scale)
        bar_height = int(8 * scale)
        health_bar_x = int(20 * scale)
        health_bar_y = int(50 * scale)  # Position below score

        # Draw health background and bar
        pygame.draw.rect(surface, DARK_GRAY, (health_bar_x, health_bar_y, bar_max_width, bar_height))
        current_health_width = int((self.health / self.max_health) * bar_max_width)
        if current_health_width > 0:
            pygame.draw.rect(surface, GREEN, (health_bar_x, health_bar_y, current_health_width, bar_height))
            
        # Draw shield background and bar
        shield_bar_y = health_bar_y - bar_spacing  # Position shield bar above health
        pygame.draw.rect(surface, DARK_GRAY, (health_bar_x, shield_bar_y, bar_max_width, bar_height))
        current_shield_width = int((self.shield / self.max_shield) * bar_max_width)
        if current_shield_width > 0:
            pygame.draw.rect(surface, BLUE, (health_bar_x, shield_bar_y, current_shield_width, bar_height))
            
        # Draw labels for the bars
        font_size = int(14 * scale)
        font = load_font(font_size)
        health_label = font.render("HULL", True, GREEN)
        shield_label = font.render("SHIELD", True, BLUE)
        
        # Position labels to the right of the bars
        label_x = health_bar_x + bar_max_width + int(5 * scale)
        health_label_y = health_bar_y
        shield_label_y = shield_bar_y
        
        surface.blit(health_label, (label_x, health_label_y))
        surface.blit(shield_label, (label_x, shield_label_y))

    def draw_damage_flash(self, surface):
        if self.damage_flash_timer > 0:
            # Use current surface dimensions
            screen_width = surface.get_width()
            screen_height = surface.get_height()
            flash_surface = pygame.Surface((screen_width, screen_height))
            flash_surface.fill(RED)
            flash_surface.set_alpha(100)  # Semi-transparent
            surface.blit(flash_surface, (0, 0))
            
    def is_invulnerable(self):
        """Check if the player is currently invulnerable"""
        # Player is invulnerable during damage flash
        return self.damage_flash_timer > 0

class Laser:
    def __init__(self, x, y, angle, piercing=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.damage = 1
        self.piercing = piercing
        
    def update(self):
        # Calculate movement based on angle
        angle_rad = math.radians(self.angle)
        dx = math.cos(angle_rad) * self.speed  # Standard calculation for X
        dy = math.sin(angle_rad) * self.speed  # Standard calculation for Y (Pygame: +y is down)
        
        self.x += dx
        self.y += dy
        
    def draw(self, surface):
        # Player lasers (angle -90) should draw vertically upward
        # Other projectiles should follow their angle
        
        # Calculate endpoint based on angle - SAME calculation as in update()
        angle_rad = math.radians(self.angle)
        dx = math.cos(angle_rad) * 10  # Length of 10 pixels
        dy = math.sin(angle_rad) * 10
        
        end_x = self.x + dx
        end_y = self.y + dy
        
        # Draw the laser as a line from current position to calculated endpoint
        pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 2)
        
        # Add a small glow effect if this is a piercing laser
        if self.piercing:
            pygame.draw.circle(surface, (100, 100, 255, 150), (int(self.x), int(self.y)), 3)
        
    def is_off_screen(self, screen_height):
        # Only need to check top boundary for player lasers
        return self.y < 0

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.health = self.get_health()
        self.max_health = self.health
        self.speed = self.get_speed()
        self.shoot_cooldown = 0
        self.width = int(self.get_width() * 1.2)  # Increased size by 20%
        self.height = int(self.get_height() * 1.2)  # Increased size by 20%
        self.is_hovered = False
        self.info_panel = self.create_info_panel()
        
    def get_health(self):
        if self.type == "Swarmer":
            return 1
        elif self.type == "Striker":
            return 3
        elif self.type == "Destroyer":
            return 10
        elif self.type == "Harvester":
            return 5
        elif self.type == "SporeLauncher":
            return 4
            
    def get_speed(self):
        if self.type == "Swarmer":
            return 3
        elif self.type == "Striker":
            return 2
        elif self.type == "Destroyer":
            return 1
        elif self.type == "Harvester":
            return 1.5
        elif self.type == "SporeLauncher":
            return 0.5
            
    def get_width(self):
        if self.type == "Swarmer":
            return 20
        elif self.type == "Striker":
            return 30
        elif self.type == "Destroyer":
            return 60
        elif self.type == "Harvester":
            return 40
        elif self.type == "SporeLauncher":
            return 35
            
    def get_height(self):
        if self.type == "Swarmer":
            return 20
        elif self.type == "Striker":
            return 25
        elif self.type == "Destroyer":
            return 50
        elif self.type == "Harvester":
            return 35
        elif self.type == "SporeLauncher":
            return 30
            
    def get_damage(self):
        if self.type == "Swarmer":
            return 1
        elif self.type == "Striker":
            return 2
        elif self.type == "Destroyer":
            return 3
        elif self.type == "Harvester":
            return 2
        elif self.type == "SporeLauncher":
            return 1
            
    def get_abilities(self):
        if self.type == "Swarmer":
            return "Rapid Fire"
        elif self.type == "Striker":
            return "Plasma Shot"
        elif self.type == "Destroyer":
            return "Twin Laser"
        elif self.type == "Harvester":
            return "Drone Deployer"
        elif self.type == "SporeLauncher":
            return "Spore Cloud"
            
    def get_description(self):
        if self.type == "Swarmer":
            return "Fast attack craft from the outer Kryll colonies"
        elif self.type == "Striker":
            return "Heavily armed assault ship"
        elif self.type == "Destroyer":
            return "Massive capital ship with devastating firepower"
        elif self.type == "Harvester":
            return "Resource gathering vessel with drone support"
        elif self.type == "SporeLauncher":
            return "Biological warfare specialist"
            
    def create_info_panel(self):
        font = pygame.font.Font(None, 24)
        name = font.render(f"Name: Kryll {self.type}", True, WHITE)
        health = font.render(f"Health: {self.health}/{self.max_health}", True, WHITE)
        damage = font.render(f"Damage: {self.get_damage()}", True, WHITE)
        abilities = font.render(f"Abilities: {self.get_abilities()}", True, WHITE)
        description = font.render(self.get_description(), True, WHITE)
        
        panel_width = max(name.get_width(), health.get_width(), damage.get_width(), 
                         abilities.get_width(), description.get_width()) + 20
        panel_height = name.get_height() * 5 + 30
        
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill((0, 0, 0, 200))
        panel.set_alpha(200)
        
        y_offset = 10
        panel.blit(name, (10, y_offset))
        y_offset += name.get_height() + 5
        panel.blit(health, (10, y_offset))
        y_offset += health.get_height() + 5
        panel.blit(damage, (10, y_offset))
        y_offset += damage.get_height() + 5
        panel.blit(abilities, (10, y_offset))
        y_offset += abilities.get_height() + 5
        panel.blit(description, (10, y_offset))
        
        return panel
            
    def update(self):
        self.y += self.speed
        if self.type == "Swarmer":
            self.x += math.sin(self.y * 0.1) * 2  # Erratic movement
            
    def take_damage(self, amount):
        """Reduce enemy health by the given amount"""
        self.health -= amount
        # Update info panel with new health
        self.info_panel = self.create_info_panel()
        return self.health <= 0
            
    def draw(self, surface):
        # Draw enemy ship
        if self.type == "Swarmer":
            pygame.draw.polygon(surface, RED, [
                (self.x, self.y - self.height//2),
                (self.x - self.width//2, self.y + self.height//2),
                (self.x + self.width//2, self.y + self.height//2)
            ])
        elif self.type == "Striker":
            pygame.draw.rect(surface, BLUE, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        elif self.type == "Destroyer":
            pygame.draw.polygon(surface, PURPLE, [
                (self.x, self.y - self.height//2),
                (self.x - self.width//2, self.y),
                (self.x - self.width//4, self.y + self.height//2),
                (self.x + self.width//4, self.y + self.height//2),
                (self.x + self.width//2, self.y)
            ])
        elif self.type == "Harvester":
            pygame.draw.rect(surface, GREEN, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        elif self.type == "SporeLauncher":
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.width//2)
            
        # Draw health bar
        health_bar_width = self.width
        health_bar_height = 5
        health_bar_x = self.x - health_bar_width//2
        health_bar_y = self.y - self.height//2 - 10
        
        # Draw background
        pygame.draw.rect(surface, GRAY, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Draw health
        health_width = int((self.health / self.max_health) * health_bar_width)
        if health_width > 0:
            pygame.draw.rect(surface, GREEN, (health_bar_x, health_bar_y, health_width, health_bar_height))
            
        # Draw info panel if hovered
        if self.is_hovered:
            panel_x = self.x - self.info_panel.get_width()//2
            panel_y = self.y - self.height//2 - self.info_panel.get_height() - 10
            surface.blit(self.info_panel, (panel_x, panel_y))
            
        # Reset hover state
        self.is_hovered = False

    def shoot(self):
        if self.shoot_cooldown <= 0:
            # Default angle for enemies shooting down
            shoot_angle = 90 
            
            if self.type == "Swarmer":
                self.shoot_cooldown = 60
                # Pass angle (90) and type ("small") correctly
                return [EnemyProjectile(self.x, self.y, shoot_angle, "small")]
            elif self.type == "Striker":
                self.shoot_cooldown = 90
                 # Pass angle (90) and type ("plasma") correctly
                return [EnemyProjectile(self.x, self.y, shoot_angle, "plasma")]
            elif self.type == "Destroyer":
                self.shoot_cooldown = 120
                # Pass angle (90) and type ("laser") correctly
                return [
                    EnemyProjectile(self.x - 20, self.y, shoot_angle, "laser"),
                    EnemyProjectile(self.x + 20, self.y, shoot_angle, "laser")
                ]
            elif self.type == "Harvester":
                 # NOTE: Harvester might deploy drones instead of shooting? 
                 # For now, assume it shoots 'small' projectiles downwards.
                self.shoot_cooldown = 150
                return [EnemyProjectile(self.x, self.y, shoot_angle, "small")]
            elif self.type == "SporeLauncher":
                self.shoot_cooldown = 180
                 # Pass angle (90) and type ("spore") correctly
                return [EnemyProjectile(self.x, self.y, shoot_angle, "spore")]
        self.shoot_cooldown -= 1
        return []

class EnemyProjectile:
    def __init__(self, x, y, angle, projectile_type, damage=None, speed=None, width=None, height=None, health=None):
        self.x = x
        self.y = y
        self.type = projectile_type
        self.angle = angle
        # Use provided values or get defaults
        self.speed = speed if speed is not None else self.get_speed()
        self.damage = damage if damage is not None else self.get_damage()
        self.width = int(width if width is not None else self.get_width() * 1.25)  # Increased size by 25%
        self.height = int(height if height is not None else self.get_height() * 1.25)  # Increased size by 25%
        self.health = health if health is not None else self.get_health()
        self.max_health = self.health
        self.show_health_bar = False
        self.health_bar_width = 20
        self.health_bar_height = 3
        
    def get_health(self):
        if self.type == "small":
            return 1
        elif self.type == "plasma":
            return 2
        elif self.type == "laser":
            return 1
        elif self.type == "spore":
            return 1
        elif self.type == "bullet":  # Add new projectile type
            return 1
            
    def get_speed(self):
        if self.type == "small":
            return 5
        elif self.type == "plasma":
            return 3
        elif self.type == "laser":
            return 7
        elif self.type == "spore":
            return 2
        elif self.type == "bullet":  # Add new projectile type
            return 4
            
    def get_damage(self):
        if self.type == "small":
            return 1
        elif self.type == "plasma":
            return 2
        elif self.type == "laser":
            return 1
        elif self.type == "spore":
            return 1
        elif self.type == "bullet":  # Add new projectile type
            return 1
            
    def get_width(self):
        if self.type == "small":
            return 4
        elif self.type == "plasma":
            return 8
        elif self.type == "laser":
            return 3
        elif self.type == "spore":
            return 6
        elif self.type == "bullet":  # Add new projectile type
            return 5
            
    def get_height(self):
        if self.type == "small":
            return 8
        elif self.type == "plasma":
            return 12
        elif self.type == "laser":
            return 15
        elif self.type == "spore":
            return 6
        elif self.type == "bullet":  # Add new projectile type
            return 5
            
    def update(self):
        # Calculate movement based on angle
        angle_rad = math.radians(self.angle)
        dx = math.cos(angle_rad) * self.speed  # Standard calculation for X
        dy = math.sin(angle_rad) * self.speed  # Standard calculation for Y (Pygame: +y is down)
        
        self.x += dx
        self.y += dy
        
        # Special movement for spore type
        if self.type == "spore":
            self.x += math.sin(self.y * 0.1) * 2  # Additional arc movement
            
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
            
    def draw(self, surface):
        if self.type == "small":
            pygame.draw.rect(surface, RED, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        elif self.type == "plasma":
            pygame.draw.rect(surface, BLUE, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        elif self.type == "laser":
            pygame.draw.line(surface, PURPLE, (self.x, self.y), (self.x, self.y - self.height), 2)
        elif self.type == "spore":
            pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.width//2)
        elif self.type == "bullet":
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), self.width//2)
            
        # Draw health bar if active
        if self.show_health_bar:
            # Draw background
            health_bar_x = self.x - self.health_bar_width//2
            health_bar_y = self.y - self.height//2 - 5
            pygame.draw.rect(surface, GRAY, (health_bar_x, health_bar_y, self.health_bar_width, self.health_bar_height))
            
            # Draw health
            health_width = int((self.health / self.max_health) * self.health_bar_width)
            if health_width > 0:
                pygame.draw.rect(surface, GREEN, (health_bar_x, health_bar_y, health_width, self.health_bar_height))
                
        # Reset health bar visibility
        self.show_health_bar = False

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 2
        
    def update(self):
        self.y += self.speed
        
    def draw(self, surface):
        pygame.draw.polygon(surface, YELLOW, [
            (self.x, self.y - self.height//2),
            (self.x - self.width//2, self.y + self.height//2),
            (self.x + self.width//2, self.y + self.height//2)
        ])

class BossEnemy:
    def __init__(self, screen_width):
        self.x = screen_width // 2
        self.y = -BOSS_HEIGHT # Start off-screen top
        self.width = BOSS_WIDTH
        self.height = BOSS_HEIGHT
        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.speed = BOSS_SPEED
        self.shoot_cooldown_laser = 0
        self.shoot_cooldown_plasma = 0
        self.shoot_cooldown_spread = 0  # Spread attack
        self.shoot_cooldown_beam = 0    # Death beam attack
        self.shoot_cooldown_mines = 0   # Mine deployment
        self.direction = 1 # 1 for right, -1 for left
        self.entry_complete = False
        self.screen_width = screen_width # Store for movement bounds
        self.attack_phase = 1  # Start with phase 1
        self.phase_timer = 0   # Timer for phase-specific patterns
        self.phase_transition_time = 0  # Timer for phase transition effects
        self.flash_timer = 0   # For damage visual
        self.name = BOSS_NAME  # Kryll Command Carrier
        
        # Beam attack state
        self.beam_active = False
        self.beam_target_x = 0
        self.beam_charge_time = 0
        self.beam_duration = 0
        
        # Mine deployment state
        self.mines = []

    def update(self):
        # Entry sequence
        if not self.entry_complete:
            self.y += self.speed * 2 # Move down faster initially
            if self.y >= self.height // 2:
                self.y = self.height // 2
                self.entry_complete = True
            return # Don't move sideways or shoot during entry
        
        # Update phase transition timer
        if self.phase_transition_time > 0:
            self.phase_transition_time -= 1
            # Don't move or attack during transition
            return
            
        # Update phase timer (used for movement patterns)
        self.phase_timer += 1
            
        # Movement behavior changes based on phase
        if self.attack_phase == 1:
            # Phase 1: Simple left-right movement
            self.x += self.speed * self.direction
            if self.x <= self.width // 2 or self.x >= self.screen_width - self.width // 2:
                self.direction *= -1 # Reverse direction at edges
        elif self.attack_phase == 2:
            # Phase 2: Faster movement with slight vertical oscillation
            self.x += (self.speed * 1.5) * self.direction
            if self.x <= self.width // 2 or self.x >= self.screen_width - self.width // 2:
                self.direction *= -1
            # Small vertical movement
            self.y += math.sin(self.phase_timer * 0.05) * 0.5
        elif self.attack_phase == 3:
            # Phase 3: More aggressive movement pattern
            self.x += (self.speed * 1.8) * self.direction
            if self.x <= self.width // 2 or self.x >= self.screen_width - self.width // 2:
                self.direction *= -1
            # More pronounced vertical movement
            self.y += math.sin(self.phase_timer * 0.08) * 0.8
            # Occasional quick dashes
            if self.phase_timer % 120 == 0:  # Every 2 seconds
                self.x += self.direction * 20  # Quick dash
        elif self.attack_phase == 4:
            # Phase 4: Erratic movement with beam attack preparation
            self.x += (self.speed * 1.5) * self.direction
            if self.x <= self.width // 2 or self.x >= self.screen_width - self.width // 2:
                self.direction *= -1
            
            # More complex vertical movement
            vertical_offset = (
                math.sin(self.phase_timer * 0.05) * 1.0 + 
                math.sin(self.phase_timer * 0.1) * 0.5
            )
            self.y += vertical_offset
            
            # During beam charging, slow down movement
            if self.beam_charge_time > 0:
                self.x -= self.direction * (self.speed * 0.5)  # Slow down and stabilize
        elif self.attack_phase == 5:
            # Phase 5: Desperate final phase with frantic movement
            # Faster, more erratic movement
            self.x += (self.speed * 2.5) * self.direction
            if self.x <= self.width // 2 or self.x >= self.screen_width - self.width // 2:
                self.direction *= -1
            
            # Chaotic movement pattern
            vertical_movement = (
                math.sin(self.phase_timer * 0.1) * 1.2 + 
                math.sin(self.phase_timer * 0.2) * 0.8 +
                math.cos(self.phase_timer * 0.15) * 0.5
            )
            self.y += vertical_movement
            
            # Random direction changes
            if random.random() < 0.01:  # 1% chance per frame
                self.direction *= -1
            
        # Clamp position to screen bounds
        self.x = max(self.width // 2, min(self.screen_width - self.width // 2, self.x))
        # Clamp vertical position to keep boss in top half of screen
        max_y = self.height // 2 + 100  # Some room to move vertically
        min_y = self.height // 2        # Minimum height
        self.y = max(min_y, min(max_y, self.y))

        # Update cooldowns
        if self.shoot_cooldown_laser > 0:
            self.shoot_cooldown_laser -= 1
        if self.shoot_cooldown_plasma > 0:
            self.shoot_cooldown_plasma -= 1
        if self.shoot_cooldown_spread > 0:
            self.shoot_cooldown_spread -= 1
        if self.shoot_cooldown_beam > 0:
            self.shoot_cooldown_beam -= 1
        if self.shoot_cooldown_mines > 0:
            self.shoot_cooldown_mines -= 1
            
        # Beam attack state management
        if self.beam_charge_time > 0:
            self.beam_charge_time -= 1
            if self.beam_charge_time <= 0:
                self.beam_active = True
                self.beam_duration = 90  # Beam lasts for 1.5 seconds
        
        if self.beam_duration > 0:
            self.beam_duration -= 1
            if self.beam_duration <= 0:
                self.beam_active = False
                
        # Update damage flash
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def shoot(self):
        # Don't shoot during phase transitions
        if self.phase_transition_time > 0:
            return []
            
        projectiles = []
        
        # Phase 1: Basic laser attacks
        if self.attack_phase >= 1:
            # Laser attack
            if self.shoot_cooldown_laser <= 0:
                cooldown_multiplier = 1.0
                if self.attack_phase >= 3:
                    cooldown_multiplier = 0.8  # Faster in later phases
                
                self.shoot_cooldown_laser = int(BOSS_SHOOT_COOLDOWN_LASER * cooldown_multiplier)
                
                # Basic laser pattern
                if self.attack_phase == 1:
                    # Simple 3-way laser spread
                    for offset in [-self.width//4, 0, self.width//4]:
                        projectiles.append(EnemyProjectile(
                            self.x + offset, 
                            self.y + self.height//2, 
                            90, 
                            "laser",
                            damage=1,
                            speed=7
                        ))
                else:
                    # Enhanced laser pattern for higher phases
                    num_lasers = 3 + self.attack_phase  # More lasers in higher phases
                    spread = 40 + (self.attack_phase * 10)  # Wider spread in higher phases
                    
                    for i in range(num_lasers):
                        angle = 90 - spread/2 + (spread / (num_lasers-1)) * i
                        projectiles.append(EnemyProjectile(
                            self.x, 
                            self.y + self.height//2, 
                            angle, 
                            "laser",
                            damage=1,
                            speed=7
                        ))

        # Phase 2+: Add plasma attacks
        if self.attack_phase >= 2:
            # Plasma attack
            if self.shoot_cooldown_plasma <= 0:
                cooldown_multiplier = 1.0
                if self.attack_phase >= 4:
                    cooldown_multiplier = 0.7  # Faster in last phases
                
                self.shoot_cooldown_plasma = int(BOSS_SHOOT_COOLDOWN_PLASMA * cooldown_multiplier)
                
                # Basic plasma shot
                projectiles.append(EnemyProjectile(
                    self.x, 
                    self.y + self.height//2, 
                    90, 
                    "plasma",
                    damage=2,
                    speed=4,
                    width=15,
                    height=15,
                    health=2 + self.attack_phase  # Stronger in higher phases
                ))
                
                # Add side shots in later phases
                if self.attack_phase >= 3:
                    for offset in [-self.width//3, self.width//3]:
                        projectiles.append(EnemyProjectile(
                            self.x + offset, 
                            self.y + self.height//3, 
                            90, 
                            "plasma",
                            damage=2,
                            speed=4,
                            width=15,
                            height=15,
                            health=2
                        ))

        # Phase 3+: Add spread attack
        if self.attack_phase >= 3:
            if self.shoot_cooldown_spread <= 0:
                self.shoot_cooldown_spread = BOSS_SHOOT_COOLDOWN_SPREAD
                
                # Create a spread of small projectiles
                num_projectiles = 6 + (self.attack_phase - 3) * 2  # More projectiles in higher phases
                for i in range(num_projectiles):
                    angle = (i / num_projectiles) * 180  # Spread in semicircle down
                    rad_angle = math.radians(angle)
                    offset_x = math.cos(rad_angle) * 30
                    projectile = EnemyProjectile(
                        self.x + offset_x, 
                        self.y + self.height//2, 
                        angle - 90, 
                        "small",
                        damage=1,
                        speed=5
                    )
                    projectiles.append(projectile)

        # Phase 4+: Add death beam attack
        if self.attack_phase >= 4:
            if self.shoot_cooldown_beam <= 0 and not self.beam_active and self.beam_charge_time <= 0:
                self.shoot_cooldown_beam = BOSS_SHOOT_COOLDOWN_BEAM
                # Start charging the beam
                self.beam_charge_time = 60  # 1 second charge time
                # Pick a target point (to be used when the beam activates)
                self.beam_target_x = random.randint(
                    int(self.width), 
                    int(self.screen_width - self.width)
                )

        # Phase 5: Add mine deployment
        if self.attack_phase >= 5:
            if self.shoot_cooldown_mines <= 0:
                self.shoot_cooldown_mines = BOSS_SHOOT_COOLDOWN_MINES
                
                # Deploy mines in a pattern
                num_mines = 3
                spacing = self.screen_width // (num_mines + 1)
                
                for i in range(num_mines):
                    x_pos = spacing * (i + 1)
                    projectiles.append(EnemyProjectile(
                        x_pos, 
                        self.y + self.height//2, 
                        90, 
                        "mine",
                        damage=3,
                        speed=2,
                        width=20,
                        height=20,
                        health=5
                    ))

        return projectiles

    def take_damage(self, amount):
        old_health_percentage = self.health / self.max_health
        
        # Apply damage
        self.health -= amount
        self.flash_timer = 5  # Flash for 5 frames when damaged
        
        # Current health percentage
        new_health_percentage = self.health / self.max_health
        
        # Check if we need to change phases
        # Find which health threshold we're below now but weren't before
        for i in range(len(BOSS_PHASE_THRESHOLDS) - 1):
            threshold = BOSS_PHASE_THRESHOLDS[i+1]
            if old_health_percentage > threshold and new_health_percentage <= threshold:
                # Transition to the new phase (add one because phases are 1-indexed)
                self.attack_phase = i + 2  # Skip to this phase
                self.phase_transition_time = 60  # 1 second transition time
                break

    def draw(self, surface):
        # Base color changes based on phase
        if self.attack_phase == 1:
            base_color = (100, 100, 100)  # Gray for phase 1
        elif self.attack_phase == 2:
            base_color = (150, 100, 100)  # Reddish for phase 2
        elif self.attack_phase == 3:
            base_color = (180, 80, 80)    # More red for phase 3
        elif self.attack_phase == 4:
            base_color = (220, 60, 60)    # Even more red for phase 4
        elif self.attack_phase == 5:
            base_color = (250, 30, 30)    # Bright red for final phase
        
        # Modify color based on flash (damage indicator)
        if self.flash_timer > 0:
            # Flash bright white when damaged
            flash_intensity = self.flash_timer / 5  # 5 is max flash timer
            base_color = (
                min(255, int(base_color[0] + (255 - base_color[0]) * flash_intensity)),
                min(255, int(base_color[1] + (255 - base_color[1]) * flash_intensity)),
                min(255, int(base_color[2] + (255 - base_color[2]) * flash_intensity))
            )
        
        # Phase transition effect
        if self.phase_transition_time > 0:
            # Pulse/flicker during transition
            if self.phase_transition_time % 10 < 5:  # Alternate every 5 frames
                base_color = (255, 255, 0)  # Bright yellow during transition
        
        # Different visual appearance based on phase
        if self.attack_phase == 1:
            # Phase 1: Simple rectangular ship
            pygame.draw.rect(surface, base_color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
            
            # Engine exhaust
            pygame.draw.polygon(surface, (255, 100, 0), [
                (self.x - self.width//4, self.y + self.height//2),
                (self.x, self.y + self.height//2 + 20),
                (self.x + self.width//4, self.y + self.height//2)
            ])
            
            # Basic details
            pygame.draw.line(surface, (80, 80, 80), 
                             (self.x - self.width//2, self.y), 
                             (self.x + self.width//2, self.y), 
                             3)
        
        elif self.attack_phase == 2:
            # Phase 2: More detailed ship with wings
            # Main body
            pygame.draw.rect(surface, base_color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
            
            # Wing extensions
            pygame.draw.polygon(surface, base_color, [
                (self.x - self.width//2, self.y),
                (self.x - self.width//2 - 20, self.y + 20),
                (self.x - self.width//2, self.y + 40),
            ])
            pygame.draw.polygon(surface, base_color, [
                (self.x + self.width//2, self.y),
                (self.x + self.width//2 + 20, self.y + 20),
                (self.x + self.width//2, self.y + 40),
            ])
            
            # Glowing "eyes"
            eye_color = RED
            pygame.draw.circle(surface, eye_color, (int(self.x - self.width//4), int(self.y)), 8)
            pygame.draw.circle(surface, eye_color, (int(self.x + self.width//4), int(self.y)), 8)
            
        elif self.attack_phase == 3:
            # Phase 3: More aggressive looking with spikes
            # Main body
            pygame.draw.rect(surface, base_color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
            
            # Wing extensions with spikes
            pygame.draw.polygon(surface, base_color, [
                (self.x - self.width//2, self.y - self.height//4),
                (self.x - self.width//2 - 30, self.y),
                (self.x - self.width//2 - 20, self.y + 20),
                (self.x - self.width//2, self.y + self.height//4),
            ])
            pygame.draw.polygon(surface, base_color, [
                (self.x + self.width//2, self.y - self.height//4),
                (self.x + self.width//2 + 30, self.y),
                (self.x + self.width//2 + 20, self.y + 20),
                (self.x + self.width//2, self.y + self.height//4),
            ])
            
            # Multiple glowing spots
            glow_color = (255, 50, 0)  # Orange-red glow
            for i in range(3):
                offset = (i - 1) * self.width//4
                pygame.draw.circle(surface, glow_color, (int(self.x + offset), int(self.y)), 10)
                
            # Engine exhaust (stronger)
            pygame.draw.polygon(surface, (255, 150, 0), [
                (self.x - self.width//3, self.y + self.height//2),
                (self.x, self.y + self.height//2 + 30),
                (self.x + self.width//3, self.y + self.height//2)
            ])
            
        elif self.attack_phase == 4:
            # Phase 4: Transformed with more weapons
            # Main body (larger)
            pygame.draw.rect(surface, base_color, (self.x - self.width//2 - 10, self.y - self.height//2, self.width + 20, self.height))
            
            # Cannon extensions
            cannon_color = (50, 50, 50)
            pygame.draw.rect(surface, cannon_color, (self.x - self.width//3, self.y + self.height//2, 20, 30))
            pygame.draw.rect(surface, cannon_color, (self.x + self.width//3 - 20, self.y + self.height//2, 20, 30))
            
            # Central weapon
            pygame.draw.rect(surface, (100, 0, 0), (self.x - 15, self.y + self.height//2 - 5, 30, 40))
            
            # Glowing parts (more intense)
            for i in range(4):
                x_offset = (i - 1.5) * self.width//3
                y_offset = (i % 2) * 10  # Alternating height
                glow_radius = 8 + (i % 2) * 4  # Alternating size
                pygame.draw.circle(surface, (255, 50, 0), (int(self.x + x_offset), int(self.y - 10 + y_offset)), glow_radius)
                
            # Beam charging/firing effect
            if self.beam_charge_time > 0:
                # Charging animation
                charge_progress = 1 - (self.beam_charge_time / 60)  # 0 to 1
                charge_color = (255, 255 * (1 - charge_progress), 0)  # Yellow to red
                charge_radius = 5 + 10 * charge_progress
                
                pygame.draw.circle(surface, charge_color, (int(self.x), int(self.y + self.height//2 + 20)), int(charge_radius))
            
            if self.beam_active and self.beam_duration > 0:
                # Draw the actual beam
                beam_color = (255, 50, 0, 150)  # Semi-transparent red
                beam_surface = pygame.Surface((10, 1000), pygame.SRCALPHA)
                pygame.draw.rect(beam_surface, beam_color, (0, 0, 10, 1000))
                
                # Rotate beam to point at target
                beam_end_y = 1000  # Far end of screen
                angle = math.degrees(math.atan2(beam_end_y, self.beam_target_x - self.x))
                rotated_beam = pygame.transform.rotate(beam_surface, -angle)
                
                # Position the beam origin at the cannon
                beam_rect = rotated_beam.get_rect(center=(self.x, self.y + self.height//2 + 20))
                surface.blit(rotated_beam, beam_rect)
                
        elif self.attack_phase == 5:
            # Phase 5: Final form, damaged but dangerous
            # Irregular, damaged ship shape
            points = [
                (self.x - self.width//2 - 15, self.y - self.height//2),
                (self.x - self.width//3, self.y - self.height//2 - 20),
                (self.x + self.width//3, self.y - self.height//2 - 10),
                (self.x + self.width//2 + 15, self.y - self.height//2),
                (self.x + self.width//2 + 25, self.y + self.height//4),
                (self.x + self.width//3, self.y + self.height//2 + 10),
                (self.x - self.width//3, self.y + self.height//2 + 5),
                (self.x - self.width//2 - 25, self.y + self.height//4)
            ]
            pygame.draw.polygon(surface, base_color, points)
            
            # Damage effects (holes and cracks)
            # Holes
            pygame.draw.circle(surface, BLACK, (int(self.x - self.width//4), int(self.y + self.height//4)), 12)
            pygame.draw.circle(surface, BLACK, (int(self.x + self.width//3), int(self.y - self.height//6)), 8)
            
            # Glowing core exposed
            core_color = (255, 200, 0)
            pygame.draw.circle(surface, core_color, (int(self.x), int(self.y)), 20)
            
            # Sparks and damage effects
            if random.random() < 0.3:  # 30% chance each frame
                spark_offset_x = random.randint(-self.width//2, self.width//2)
                spark_offset_y = random.randint(-self.height//2, self.height//2)
                spark_color = (255, 200, 0)
                pygame.draw.circle(surface, spark_color, (int(self.x + spark_offset_x), int(self.y + spark_offset_y)), 3)
                
        # Always draw health bar above the boss
        health_bar_width = 100
        health_bar_height = 8
        health_bar_x = self.x - health_bar_width//2
        health_bar_y = self.y - self.height//2 - 20

        # Draw background
        pygame.draw.rect(surface, DARK_GRAY, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health color changes based on amount
        if self.health > self.max_health * 0.6:
            health_color = GREEN
        elif self.health > self.max_health * 0.3:
            health_color = YELLOW
        else:
            health_color = RED
            
        # Draw health
        health_width = int((self.health / self.max_health) * health_bar_width)
        if health_width > 0:
            pygame.draw.rect(surface, health_color, (health_bar_x, health_bar_y, health_width, health_bar_height))
            
        # Draw phase indicator
        phase_text = f"PHASE {self.attack_phase}"
        font = load_font(16)
        phase_surface = font.render(phase_text, True, WHITE)
        surface.blit(phase_surface, (health_bar_x, health_bar_y - 20))

    def is_defeated(self):
        return self.health <= 0 

class Explosion:
    def __init__(self, x, y, size, duration=30, color=None):
        self.x = x
        self.y = y
        self.size = size
        self.max_size = size
        self.current_frame = 0
        self.max_frames = duration
        self.color = color or (255, 165, 0)  # Default orange if no color provided
        self.particles = []
        
        # Create explosion particles
        num_particles = int(size / 2)
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': 0,
                'y': 0,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(1, 4),
                'color': self.get_random_color()
            })
            
    def get_random_color(self):
        # Create variations of the base color for particles
        r, g, b = self.color
        variation = 50
        r = max(0, min(255, r + random.randint(-variation, variation)))
        g = max(0, min(255, g + random.randint(-variation, variation)))
        b = max(0, min(255, b + random.randint(-variation, variation)))
        return (r, g, b)
    
    def update(self):
        self.current_frame += 1
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
    def draw(self, surface):
        # Calculate alpha based on lifetime
        progress = self.current_frame / self.max_frames
        alpha = int(255 * (1 - progress))
        size_factor = 1 - progress * 0.5  # Explosion grows a bit then shrinks
        
        # Draw each particle
        for particle in self.particles:
            particle_x = int(self.x + particle['x'] * progress * self.size / 2)
            particle_y = int(self.y + particle['y'] * progress * self.size / 2)
            particle_size = int(particle['size'] * size_factor * (self.size / 10))
            
            # Create a surface with per-pixel alpha for the particle
            if particle_size > 0:
                particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
                color_with_alpha = particle['color'] + (alpha,)
                pygame.draw.circle(
                    particle_surface, 
                    color_with_alpha, 
                    (particle_size, particle_size), 
                    particle_size
                )
                surface.blit(
                    particle_surface, 
                    (particle_x - particle_size, particle_y - particle_size)
                )
        
        # Draw central glow
        center_size = int(self.size * (1.0 - progress * 0.8))
        if center_size > 0:
            glow_surface = pygame.Surface((center_size * 2, center_size * 2), pygame.SRCALPHA)
            center_color = self.color + (alpha,)
            pygame.draw.circle(
                glow_surface, 
                center_color, 
                (center_size, center_size), 
                center_size
            )
            surface.blit(
                glow_surface,
                (int(self.x - center_size), int(self.y - center_size))
            )
            
    def is_finished(self):
        return self.current_frame >= self.max_frames 