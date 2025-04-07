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
            return

        # Then check regular shield health
        if self.shield > 0:
            # Shield takes the damage first
            if amount <= self.shield:
                self.shield -= amount
                # Add visual/sound effect for shield damage here
                return
            else:
                # Damage exceeds shield, shield is depleted
                # and remaining damage goes to health
                remaining_damage = amount - self.shield
                self.shield = 0
                self.health -= remaining_damage
                self.damage_flash_timer = 10  # Flash for 10 frames
                # Add visual/sound effect for shield break here
                return

        # No shield, damage goes directly to health
        self.health -= amount
        self.damage_flash_timer = 10  # Flash for 10 frames
        # Add visual/sound effect for taking damage here
        
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

class Laser:
    def __init__(self, x, y, angle, piercing=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.damage = 1
        self.piercing = piercing
        
    def update(self):
        rad_angle = math.radians(self.angle)
        self.x += math.cos(rad_angle) * self.speed
        self.y += math.sin(rad_angle) * self.speed
        
    def draw(self, surface):
        pygame.draw.line(surface, WHITE, (self.x, self.y), (self.x, self.y - 10), 2)
        
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
            if self.type == "Swarmer":
                self.shoot_cooldown = 60
                return [EnemyProjectile(self.x, self.y, "small")]
            elif self.type == "Striker":
                self.shoot_cooldown = 90
                return [EnemyProjectile(self.x, self.y, "plasma")]
            elif self.type == "Destroyer":
                self.shoot_cooldown = 120
                return [
                    EnemyProjectile(self.x - 20, self.y, "laser"),
                    EnemyProjectile(self.x + 20, self.y, "laser")
                ]
            elif self.type == "Harvester":
                self.shoot_cooldown = 150
                return [EnemyProjectile(self.x, self.y, "small")]
            elif self.type == "SporeLauncher":
                self.shoot_cooldown = 180
                return [EnemyProjectile(self.x, self.y, "spore")]
        self.shoot_cooldown -= 1
        return []

class EnemyProjectile:
    def __init__(self, x, y, projectile_type):
        self.x = x
        self.y = y
        self.type = projectile_type
        self.speed = self.get_speed()
        self.damage = self.get_damage()
        self.width = int(self.get_width() * 1.25)  # Increased size by 25%
        self.height = int(self.get_height() * 1.25)  # Increased size by 25%
        self.health = self.get_health()
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
            
    def get_speed(self):
        if self.type == "small":
            return 5
        elif self.type == "plasma":
            return 3
        elif self.type == "laser":
            return 7
        elif self.type == "spore":
            return 2
            
    def get_damage(self):
        if self.type == "small":
            return 1
        elif self.type == "plasma":
            return 2
        elif self.type == "laser":
            return 1
        elif self.type == "spore":
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
            
    def get_height(self):
        if self.type == "small":
            return 8
        elif self.type == "plasma":
            return 12
        elif self.type == "laser":
            return 15
        elif self.type == "spore":
            return 6
            
    def update(self):
        self.y += self.speed
        if self.type == "spore":
            self.x += math.sin(self.y * 0.1) * 2  # Arc movement
            
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
        self.shoot_cooldown_spread = 0  # New attack type
        self.direction = 1 # 1 for right, -1 for left
        self.entry_complete = False
        self.screen_width = screen_width # Store for movement bounds
        self.attack_phase = 1  # Boss will have multiple attack phases
        self.phase_timer = 0   # Timer for phase transitions
        self.phase_duration = 600  # 10 seconds per phase
        self.flash_timer = 0   # For damage visual

    def update(self):
        # Entry sequence
        if not self.entry_complete:
            self.y += self.speed * 2 # Move down faster initially
            if self.y >= self.height // 2:
                self.y = self.height // 2
                self.entry_complete = True
            return # Don't move sideways or shoot during entry

        # Phase management
        self.phase_timer += 1
        if self.phase_timer >= self.phase_duration:
            self.phase_timer = 0
            self.attack_phase = min(3, self.attack_phase + 1)  # Up to 3 phases

        # Movement behavior changes based on phase
        if self.attack_phase == 1:
            # Simple left-right movement in phase 1
            self.x += self.speed * self.direction
            if self.x <= self.width // 2 or self.x >= self.screen_width - self.width // 2:
                self.direction *= -1 # Reverse direction at edges
        elif self.attack_phase == 2:
            # More aggressive movement in phase 2
            self.x += (self.speed * 1.5) * self.direction
            if self.x <= self.width // 2 or self.x >= self.screen_width - self.width // 2:
                self.direction *= -1
            # Small vertical movement
            self.y += math.sin(self.phase_timer * 0.05) * 0.5
        elif self.attack_phase == 3:
            # Erratic movement in final phase
            self.x += (self.speed * 2) * self.direction
            if self.x <= self.width // 2 or self.x >= self.screen_width - self.width // 2:
                self.direction *= -1
            # More pronounced vertical movement
            self.y += math.sin(self.phase_timer * 0.1) * 1.0
            
        # Clamp position to screen bounds
        self.x = max(self.width // 2, min(self.screen_width - self.width // 2, self.x))

        # Update cooldowns
        if self.shoot_cooldown_laser > 0:
            self.shoot_cooldown_laser -= 1
        if self.shoot_cooldown_plasma > 0:
            self.shoot_cooldown_plasma -= 1
        if self.shoot_cooldown_spread > 0:
            self.shoot_cooldown_spread -= 1
            
        # Update damage flash
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def shoot(self):
        projectiles = []
        # Attack pattern changes based on phase
        
        # Phase 1: Basic attacks
        if self.attack_phase >= 1:
            # Laser attack
            if self.shoot_cooldown_laser <= 0:
                cooldown_multiplier = 1.0
                if self.attack_phase == 3:
                    cooldown_multiplier = 0.7  # Faster in last phase
                
                self.shoot_cooldown_laser = int(BOSS_SHOOT_COOLDOWN_LASER * cooldown_multiplier)
                # Fire multiple lasers
                for offset in [-self.width//4, 0, self.width//4]:
                    projectiles.append(EnemyProjectile(self.x + offset, self.y + self.height//2, "laser"))

        # Phase 2: Add plasma attacks
        if self.attack_phase >= 2:
            # Plasma attack
            if self.shoot_cooldown_plasma <= 0:
                cooldown_multiplier = 1.0
                if self.attack_phase == 3:
                    cooldown_multiplier = 0.7  # Faster in last phase
                
                self.shoot_cooldown_plasma = int(BOSS_SHOOT_COOLDOWN_PLASMA * cooldown_multiplier)
                # Fire plasma
                projectiles.append(EnemyProjectile(self.x, self.y + self.height//2, "plasma"))
                
                # Add side shots in later phases
                if self.attack_phase == 3:
                    projectiles.append(EnemyProjectile(self.x - self.width//3, self.y + self.height//3, "plasma"))
                    projectiles.append(EnemyProjectile(self.x + self.width//3, self.y + self.height//3, "plasma"))

        # Phase 3: Add spread attack
        if self.attack_phase == 3:
            if self.shoot_cooldown_spread <= 0:
                self.shoot_cooldown_spread = 180  # 3 seconds
                # Create a spread of small projectiles
                num_projectiles = 8
                for i in range(num_projectiles):
                    angle = (i / num_projectiles) * 180  # Spread in semicircle down
                    rad_angle = math.radians(angle)
                    offset_x = math.cos(rad_angle) * 30
                    projectile = EnemyProjectile(self.x + offset_x, self.y + self.height//2, "small")
                    projectile.angle = angle - 90  # Adjust angle to point downward
                    projectiles.append(projectile)

        return projectiles

    def take_damage(self, amount):
        self.health -= amount
        self.flash_timer = 5  # Flash for 5 frames when damaged
        # Increase attack phase if health drops below thresholds
        if self.health <= self.max_health * 0.66 and self.attack_phase < 2:
            self.attack_phase = 2
        elif self.health <= self.max_health * 0.33 and self.attack_phase < 3:
            self.attack_phase = 3

    def draw(self, surface):
        # Base color changes based on phase
        if self.attack_phase == 1:
            base_color = PURPLE
        elif self.attack_phase == 2:
            base_color = (150, 0, 150)  # Brighter purple
        else:
            base_color = (200, 0, 100)  # Magenta/red
            
        # Flash white when damaged
        if self.flash_timer > 0:
            if self.flash_timer % 2 == 0:  # Alternate frames for flashing effect
                base_color = WHITE

        # Draw boss body - more complex shape based on phase
        if self.attack_phase == 1:
            # Phase 1: Simple shape
            pygame.draw.rect(surface, base_color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
            
            # Add some details
            pygame.draw.rect(surface, RED, 
                           (self.x - self.width//3, self.y - self.height//2, self.width//6, self.height//6))
            pygame.draw.rect(surface, RED, 
                           (self.x + self.width//6, self.y - self.height//2, self.width//6, self.height//6))
        
        elif self.attack_phase == 2:
            # Phase 2: More detailed shape
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
            
        else:
            # Phase 3: Full detailed shape with "aura"
            # Create aura effect
            aura_width = self.width + 20
            aura_height = self.height + 20
            aura_surface = pygame.Surface((aura_width, aura_height), pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surface, (255, 0, 0, 100), (0, 0, aura_width, aura_height))
            surface.blit(aura_surface, (self.x - aura_width//2, self.y - aura_height//2))
            
            # Main body
            pygame.draw.rect(surface, base_color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
            
            # Extended wings
            pygame.draw.polygon(surface, base_color, [
                (self.x - self.width//2, self.y - 10),
                (self.x - self.width//2 - 30, self.y + 20),
                (self.x - self.width//2, self.y + 50),
            ])
            pygame.draw.polygon(surface, base_color, [
                (self.x + self.width//2, self.y - 10),
                (self.x + self.width//2 + 30, self.y + 20),
                (self.x + self.width//2, self.y + 50),
            ])
            
            # Glowing "eyes" and other details
            eye_color = (255, 255, 0)  # Yellow in final phase
            pygame.draw.circle(surface, eye_color, (int(self.x - self.width//4), int(self.y)), 10)
            pygame.draw.circle(surface, eye_color, (int(self.x + self.width//4), int(self.y)), 10)
            
            # Weapon ports
            pygame.draw.rect(surface, BLUE, 
                           (self.x - self.width//4 - 5, self.y + self.height//2 - 5, 10, 10))
            pygame.draw.rect(surface, BLUE, 
                           (self.x + self.width//4 - 5, self.y + self.height//2 - 5, 10, 10))

        # Draw health bar
        health_bar_width = self.width * 1.2  # Wider for visibility
        health_bar_height = 12
        health_bar_x = self.x - health_bar_width//2
        health_bar_y = self.y - self.height//2 - 20 # Above the boss

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