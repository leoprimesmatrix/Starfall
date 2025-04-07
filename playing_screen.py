import pygame
import pygame_gui
import math
import random
from constants import *
from game_objects import Star, Nebula, PlayerShip, Laser, Enemy, EnemyProjectile, PowerUp, BossEnemy

class PlayingScreen:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.pause_button = None
        self.is_visible = False

        # Game objects - initialize empty
        self.player = None
        self.stars = []
        self.nebula = Nebula()
        self.enemies = []
        self.player_lasers = []
        self.enemy_projectiles = []
        self.power_ups = []
        self.boss = None

        # Game state
        self.score = 0
        self.enemy_spawn_timer = 0
        self.power_up_spawn_timer = 0
        self.game_over = False
        self.level_complete_timer = -1 # Timer for showing completion message
        
        # Notification system
        self.notification_active = False
        self.notification_timer = 0
        self.notification_text = None
        self.notification_rect = None
        
        # Visual effects
        self.particles = []
        self.explosions = []

        self.setup_ui() # Create UI elements
        self.hide()  # Hide UI elements initially

    def reset(self, game_state):
        """Resets the playing screen state for the current level in game_state."""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        self.player = PlayerShip()
        self.player.x = screen_width // 2 # Center player horizontally
        self.player.y = screen_height * 2 // 3 # Position player vertically

        self.stars = []
        self.enemies = []
        self.player_lasers = []
        self.enemy_projectiles = []
        self.power_ups = []
        self.boss = None

        self.score = 0
        self.enemy_spawn_timer = 0
        self.power_up_spawn_timer = 0
        self.game_over = False
        self.level_complete_timer = -1

        # Set nebula color for the level
        self.nebula.set_color_for_level(game_state.current_level)

        # Initialize stars for the current screen size
        self.init_stars()

        # Spawn boss if it's the boss level
        if game_state.is_boss_level():
            self.boss = BossEnemy(screen_width)

        self.show() # Make sure UI (like pause button) is visible

    def init_stars(self):
        self.stars = []
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        for _ in range(100):
            self.stars.append(Star(
                random.randint(0, screen_width),
                random.randint(0, screen_height),
                random.uniform(1, 3)
            ))

    def setup_ui(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        scale = get_scale_factor(screen_width, screen_height)

        # Store current visibility state
        was_visible = self.is_visible

        # Kill old button if it exists
        if self.pause_button:
            self.pause_button.kill()

        # Create pause button in top-right corner
        button_width = int(PAUSE_BUTTON_WIDTH * scale)
        button_height = int(PAUSE_BUTTON_HEIGHT * scale)
        margin = int(PAUSE_BUTTON_MARGIN * scale)

        self.pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(screen_width - button_width - margin,
                                    margin,
                                    button_width, button_height),
            text="Pause",
            manager=self.manager
        )

        # Restore visibility state (don't show if hidden)
        if was_visible and not self.game_over:
            self.show()
        else:
            self.hide()

        # Reinitialize stars for new screen size if player exists (avoids error on first init)
        if hasattr(self, 'player') and self.player:
            self.init_stars()
            # Keep player within new screen bounds
            self.player.x = min(max(self.player.width//2, self.player.x), screen_width - self.player.width//2)
            self.player.y = min(max(self.player.height//2, self.player.y), screen_height - self.player.height//2)

    def show(self):
        if self.pause_button and not self.game_over:
            self.pause_button.show()
        self.is_visible = True

    def hide(self):
        if self.pause_button:
            self.pause_button.hide()
        self.is_visible = False

    def draw(self, surface, game_state):
        # Draw background
        surface.fill(BLACK) # Fill with black first
        
        # Draw nebula
        self.nebula.draw(surface)
        
        # Draw stars
        for star in self.stars:
            star.draw(surface)
        
        # Draw player
        if self.player:
            self.player.draw(surface)
            
        # Draw player lasers
        for laser in self.player_lasers:
            laser.draw(surface)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface)
            
        # Draw enemy projectiles
        for projectile in self.enemy_projectiles:
            projectile.draw(surface)
            
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(surface)
            
        # Draw boss if it exists
        if self.boss:
            self.boss.draw(surface)
            
        # Draw particles and effects
        self.draw_particles(surface)
            
        # Draw UI elements
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        scale = get_scale_factor(screen_width, screen_height)
        
        # Draw score in top-left
        score_font_size = int(24 * scale)
        score_font = load_font(score_font_size)
        score_text = score_font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(topleft=(int(20 * scale), int(20 * scale)))
        surface.blit(score_text, score_rect)
        
        # Get pause button area to avoid text overlap
        pause_button_area_width = self.pause_button.relative_rect.width + int(40 * scale)
        
        # Draw current mission name
        mission_font_size = int(20 * scale)
        mission_font = load_font(mission_font_size)
        mission_name = f"Mission: {game_state.current_level} - {list(MISSION_DESCRIPTIONS.values())[game_state.current_level-1].split('.')[0]}"
        mission_text = mission_font.render(mission_name, True, LIGHT_GRAY)
        mission_rect = mission_text.get_rect(midtop=(screen_width // 2, int(10 * scale)))
        surface.blit(mission_text, mission_rect)
        
        # Draw ship info if player exists
        if self.player:
            ship_font_size = int(16 * scale)
            ship_font = load_font(ship_font_size)
            ship_text = ship_font.render(f"Ship: {self.player.ship_name}", True, BLUE)
            ship_rect = ship_text.get_rect(midbottom=(screen_width // 2, screen_height - int(10 * scale)))
            surface.blit(ship_text, ship_rect)
        
        # Draw remaining enemies
        if game_state.is_boss_level():
            remaining_text = score_font.render(f"Defeat the {self.boss.name if self.boss else BOSS_NAME}", True, YELLOW)
        else:
            enemies_remaining = game_state.get_enemies_remaining()
            remaining_text = score_font.render(f"Kryll Forces: {enemies_remaining}", True, YELLOW)

        # Draw remaining enemies / Boss Health
        if game_state.is_boss_level() and self.boss:
            remaining_text_str = f"{self.boss.name} Health: {self.boss.health}/{self.boss.max_health}"
            remaining_color = RED
        else:
            remaining_text_str = f"Enemies Remaining: {enemies_remaining}"
            remaining_color = WHITE

        remaining_text = score_font.render(remaining_text_str, True, remaining_color)
        remaining_rect = remaining_text.get_rect(topright=(screen_width - pause_button_area_width, int(20 * scale)))
        surface.blit(remaining_text, remaining_rect)

        # Level Completion Message
        if self.level_complete_timer > 0:
            complete_font_size = int(48 * scale)
            complete_font = load_font(complete_font_size) # Use helper
            next_level = game_state.current_level + 1
            
            if game_state.is_boss_level():
                msg = "VICTORY! The Kryll invasion has been repelled."
                sub_msg = "But Federation intelligence warns... this is only the first wave."
            elif next_level <= 5:
                msg = f"Mission {game_state.current_level} Complete!"
                sub_msg = f"Next mission: {list(MISSION_DESCRIPTIONS.keys())[next_level-1]} - {list(MISSION_DESCRIPTIONS.values())[next_level-1].split('.')[0]}"
            
            # Create a transition effect for the level complete text
            alpha = 255
            if self.level_complete_timer < 60 or self.level_complete_timer > 180:
                # Fade in/out at the beginning and end
                if self.level_complete_timer < 60:
                    alpha = int(255 * (self.level_complete_timer / 60))
                else:
                    alpha = int(255 * (1 - (self.level_complete_timer - 180) / 60))
            
            # Create surfaces with alpha
            complete_text = complete_font.render(msg, True, YELLOW)
            complete_alpha = pygame.Surface(complete_text.get_size(), pygame.SRCALPHA)
            complete_alpha.fill((255, 255, 255, alpha))
            complete_text.blit(complete_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            complete_rect = complete_text.get_rect(center=(screen_width // 2, screen_height // 2))
            surface.blit(complete_text, complete_rect)
            
            # Draw subtitle message
            sub_font_size = int(24 * scale)
            sub_font = load_font(sub_font_size)
            sub_text = sub_font.render(sub_msg, True, LIGHT_GRAY)
            sub_alpha = pygame.Surface(sub_text.get_size(), pygame.SRCALPHA)
            sub_alpha.fill((255, 255, 255, alpha))
            sub_text.blit(sub_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            sub_rect = sub_text.get_rect(center=(screen_width // 2, complete_rect.bottom + int(20 * scale)))
            surface.blit(sub_text, sub_rect)

        # Draw damage flash
        if self.player:
            self.player.draw_damage_flash(surface)
            
        # Draw notification if active
        if self.notification_active:
            # Calculate alpha for fade effect
            alpha = 255
            if self.notification_timer < NOTIFICATION_FADE_TIME:
                alpha = int(255 * (self.notification_timer / NOTIFICATION_FADE_TIME))
            
            # Ensure notification text is created
            if not self.notification_text:
                notification_font_size = int(20 * scale)
                notification_font = load_font(notification_font_size)
                self.notification_text = notification_font.render("Systems Override Ready! (Press O)", True, YELLOW)
                self.notification_rect = self.notification_text.get_rect(
                    topright=(screen_width - int(20 * scale), int(60 * scale)))
            
            # Create a copy with adjusted alpha
            text_surface = self.notification_text.copy()
            # Create a surface with per pixel alpha
            alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            # Fill with color and alpha
            alpha_surface.fill((255, 255, 255, alpha))
            # Blit using the alpha surface as a mask
            text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw notification with glow effect for visibility
            glow_surface = pygame.Surface((self.notification_rect.width + 10, self.notification_rect.height + 10), 
                                           pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 0, min(100, alpha // 2)), 
                             pygame.Rect(0, 0, glow_surface.get_width(), glow_surface.get_height()), 
                             border_radius=5)
            glow_rect = glow_surface.get_rect(center=self.notification_rect.center)
            surface.blit(glow_surface, glow_rect)
            surface.blit(text_surface, self.notification_rect)

        # Handle game over state (Check added for player existence)
        if self.game_over and self.player and self.player.health <= 0:
            self.hide()  # Hide pause button
            game_state.score = self.score # Pass score before changing state
            game_state.change_state(STATE_GAME_OVER)

    def spawn_enemy(self):
        screen_width = self.screen.get_width()
        enemy_type = random.choices(ENEMY_TYPES, weights=ENEMY_SPAWN_WEIGHTS)[0]
        x = random.randint(50, screen_width - 50)
        self.enemies.append(Enemy(x, -50, enemy_type))

    def spawn_power_up(self, x=None, y=None):
        screen_width = self.screen.get_width()
        # If no position is provided, choose a random position
        if x is None:
            x = random.randint(50, screen_width - 50)
        if y is None:
            y = -50  # Start from top of screen
        self.power_ups.append(PowerUp(x, y))
        
    def update(self, game_state):
        if self.game_over or self.level_complete_timer > 0: # Pause updates during completion message
            if self.level_complete_timer > 0:
                self.level_complete_timer -= 1
                if self.level_complete_timer == 0:
                    if hasattr(game_state.game, 'change_state_with_transition'):
                        game_state.game.change_state_with_transition(STATE_LEVEL_SELECT)
                    else:
                        game_state.change_state(STATE_LEVEL_SELECT)
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Update background
        for star in self.stars:
            star.update(screen_width, screen_height)
        self.nebula.update(screen_height)

        # Update notification system
        if game_state.ability_kill_counter >= ABILITY_ENEMY_KILL_THRESHOLD and not self.notification_active:
            self.notification_active = True
            self.notification_timer = NOTIFICATION_DURATION
        
        if self.notification_active:
            self.notification_timer -= 1
            if self.notification_timer <= 0:
                self.notification_active = False
                
        # Reset notification if abilities are not ready
        if game_state.ability_kill_counter < ABILITY_ENEMY_KILL_THRESHOLD:
            self.notification_active = False

        # Update player (Check added for player existence)
        if self.player:
            # Handle keyboard inputs
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= self.player.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += self.player.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= self.player.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += self.player.speed
            self.player.move(dx, dy, screen_width, screen_height)
            self.player.update()
            
        # Update player lasers
        for i, laser in enumerate(self.player_lasers[:]):
            laser.update()
            # Add visual effects for lasers
            if ANIMATION_ENABLED and random.random() < 0.1:  # 10% chance each frame
                # Create a visual particle effect behind laser
                self.create_laser_trail(laser)
            if laser.is_off_screen(0) or laser.y < 0:
                if i < len(self.player_lasers):
                    self.player_lasers.remove(laser)

        # Update enemy projectiles
        for projectile in self.enemy_projectiles[:]:
            projectile.update()
            if projectile.y > screen_height:
                self.enemy_projectiles.remove(projectile)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            enemy.is_hovered = False # Reset hover state
            
            # Enemy shooting
            if random.random() < 0.01:  # 1% chance to shoot per frame
                projectile = self.create_enemy_projectile(enemy)
                if projectile:
                    self.enemy_projectiles.append(projectile)
            
            # Enemy offscreen check
            if enemy.y > screen_height:
                self.enemies.remove(enemy)
        
        # Update boss
        if self.boss:
            self.boss.update()
            
            # Boss shooting patterns
            if self.boss.shoot_laser_cooldown <= 0:
                self.boss.shoot_laser_cooldown = BOSS_SHOOT_COOLDOWN_LASER
                # Create laser projectiles in a pattern
                self.create_boss_projectiles()
                
            if self.boss.shoot_plasma_cooldown <= 0:
                self.boss.shoot_plasma_cooldown = BOSS_SHOOT_COOLDOWN_PLASMA
                # Create plasma projectiles in a different pattern
                self.create_boss_plasma()
                
            self.boss.shoot_laser_cooldown -= 1
            self.boss.shoot_plasma_cooldown -= 1
        
        # Spawn enemies according to level
        if not game_state.is_boss_level() and len(self.enemies) < game_state.get_max_enemies() and not game_state.check_level_complete():
            self.enemy_spawn_timer -= 1
            if self.enemy_spawn_timer <= 0:
                self.spawn_enemy()
                self.enemy_spawn_timer = ENEMY_SPAWN_RATE
        
        # Power-Up Spawning
        if self.player:  # Only spawn power-ups if player exists
            self.power_up_spawn_timer -= 1
            if self.power_up_spawn_timer <= 0:
                if random.random() < POWER_UP_CHANCE:
                    self.spawn_power_up()
                self.power_up_spawn_timer = POWER_UP_SPAWN_RATE
        
        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.y > screen_height:
                self.power_ups.remove(power_up)
        
        # Update particles
        self.update_particles()
                
        # Check if we should spawn boss (for level 5)
        if game_state.is_boss_level() and not self.boss and not game_state.check_level_complete():
            enemies_remaining = game_state.get_enemies_remaining()
            if enemies_remaining <= 0:  # Spawn boss when regular enemies are cleared
                self.spawn_boss()
                
        # Check collisions
        self.check_collisions(game_state)
        
        # Check for level completion
        if game_state.check_level_complete() and self.level_complete_timer < 0:
            self.level_complete_timer = 240  # Timer for showing completion message (4 seconds)
            
    def create_explosion(self, x, y, size=1.0, color=None):
        """Create an explosion effect at the given position"""
        if not ANIMATION_ENABLED:
            return
            
        if color is None:
            color = (255, 150, 50)  # Default orange explosion
            
        # Create multiple particles for the explosion
        num_particles = int(20 * size)
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3) * size
            lifetime = random.randint(20, 40)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': color,
                'size': random.uniform(1, 3) * size
            })
    
    def update_particles(self):
        """Update all visual particle effects"""
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['lifetime'] -= 1
            
            # Remove dead particles
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, surface):
        """Draw all visual particle effects"""
        for particle in self.particles:
            # Calculate alpha based on remaining lifetime
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            color = particle['color']
            # If color is a tuple with RGB, add alpha
            if len(color) == 3:
                color = color + (alpha,)
            
            # Draw the particle
            if ANIMATION_ENABLED:
                # Create a surface with per-pixel alpha for the particle
                size = int(particle['size'] * 2)  # Diameter
                particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(
                    particle_surface, 
                    color, 
                    (size // 2, size // 2), 
                    particle['size']
                )
                surface.blit(particle_surface, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
                
    def create_laser_trail(self, laser):
        """Create a trail effect behind the laser"""
        if not ANIMATION_ENABLED:
            return
            
        # Create a few particles for the trail effect
        for _ in range(3):
            offset_x = random.uniform(-2, 2)
            offset_y = random.uniform(5, 10)
            
            self.particles.append({
                'x': laser.x + offset_x,
                'y': laser.y + offset_y,
                'vx': random.uniform(-0.2, 0.2),
                'vy': random.uniform(0.5, 1.5),
                'lifetime': random.randint(5, 15),
                'max_lifetime': 15,
                'color': (100, 100, 255, 200),  # Blueish white
                'size': random.uniform(1, 2)
            })
            
    def check_collisions(self, game_state):
        """Handle all collision detection and responses"""
        # Player lasers with Boss
        if self.boss:
            for laser in self.player_lasers[:]:
                if (abs(laser.x - self.boss.x) < self.boss.width//2 and
                    abs(laser.y - self.boss.y) < self.boss.height//2):
                    self.boss.health -= laser.damage
                    
                    # Create hit effect
                    if ANIMATION_ENABLED:
                        self.create_explosion(laser.x, laser.y, 0.5, (255, 100, 100))
                    
                    if not laser.piercing:
                        try:
                            self.player_lasers.remove(laser)
                        except ValueError: 
                            pass # Already removed (e.g., hit projectile first)
                    
                    if self.boss.is_defeated():
                        # Large explosion for boss defeat
                        self.create_explosion(self.boss.x, self.boss.y, 3.0, (255, 200, 50))
                        self.score += 1000 # Boss bonus score
                        game_state.complete_current_level()
                        self.level_complete_timer = 180
                        self.boss = None
                    
                    if not laser.piercing:
                        break # Laser is gone

        # Player lasers with enemies
        for laser in self.player_lasers[:]:
            for enemy in self.enemies[:]:
                if (abs(laser.x - enemy.x) < enemy.width//2 and
                    abs(laser.y - enemy.y) < enemy.height//2):
                    enemy.health -= laser.damage
                    
                    # Create small hit effect
                    if ANIMATION_ENABLED:
                        self.create_explosion(laser.x, laser.y, 0.3, (200, 200, 255))
                    
                    laser_removed = False
                    if not laser.piercing:
                        try:
                            self.player_lasers.remove(laser)
                            laser_removed = True
                        except ValueError: 
                            pass # Already removed
                    
                    if enemy.health <= 0:
                        # Create explosion effect for enemy defeat
                        self.create_explosion(enemy.x, enemy.y, 1.0)
                        self.enemies.remove(enemy)
                        self.score += 10
                        game_state.record_enemy_defeat()
                        if random.random() < POWER_UP_CHANCE:
                            self.spawn_power_up(enemy.x, enemy.y)
                        if not game_state.is_boss_level() and game_state.check_level_complete():
                            game_state.complete_current_level()
                            self.level_complete_timer = 180
                    
                    if laser_removed:
                        break # Laser hit an enemy and was removed, stop checking this laser
            # If laser wasn't removed (piercing), continue checking against other enemies

        # Player lasers with enemy projectiles
        for laser in self.player_lasers[:]:
            for projectile in self.enemy_projectiles[:]:
                if (abs(laser.x - projectile.x) < projectile.width//2 and
                    abs(laser.y - projectile.y) < projectile.height//2):
                    projectile.show_health_bar = True
                    should_remove_projectile = projectile.take_damage(laser.damage)
                    
                    # Create small hit effect
                    if ANIMATION_ENABLED and random.random() < 0.5:
                        self.create_explosion(laser.x, laser.y, 0.2, (150, 150, 255))
                    
                    laser_removed = False
                    if not laser.piercing:
                        try:
                            self.player_lasers.remove(laser)
                            laser_removed = True
                        except ValueError: 
                            pass

                    if should_remove_projectile:
                        try:
                            self.enemy_projectiles.remove(projectile)
                            # Create small explosion for projectile destruction
                            if ANIMATION_ENABLED:
                                self.create_explosion(projectile.x, projectile.y, 0.5, (100, 100, 255))
                        except ValueError: 
                            pass # Already removed

                    if laser_removed:
                        break # Laser is gone

        # Enemy projectiles with player
        if self.player:
            for projectile in self.enemy_projectiles[:]:
                if (abs(projectile.x - self.player.x) < self.player.width//2 and
                    abs(projectile.y - self.player.y) < self.player.height//2):
                    self.player.take_damage(projectile.damage)
                    
                    # Create hit effect on player
                    if ANIMATION_ENABLED:
                        self.create_explosion(projectile.x, projectile.y, 0.7, (255, 50, 50))
                    
                    self.enemy_projectiles.remove(projectile)
                    if self.player.health <= 0:
                        self.game_over = True
                        # Create large explosion for player defeat
                        if ANIMATION_ENABLED:
                            self.create_explosion(self.player.x, self.player.y, 2.0, (255, 100, 100))
                    break

        # Power-ups with player
        if self.player:
            for power_up in self.power_ups[:]:
                if (abs(power_up.x - self.player.x) < self.player.width//2 and
                    abs(power_up.y - self.player.y) < self.player.height//2):
                    self.player.power_up_active = True
                    self.player.power_up_timer = POWER_UP_DURATION
                    
                    # Create pickup effect
                    if ANIMATION_ENABLED:
                        self.create_explosion(power_up.x, power_up.y, 1.0, (200, 255, 200))
                    
                    self.power_ups.remove(power_up)
                    break

        # Enemies with player
        if self.player:
            for enemy in self.enemies[:]:
                if (abs(enemy.x - self.player.x) < (enemy.width + self.player.width)//2 and
                    abs(enemy.y - self.player.y) < (enemy.height + self.player.height)//2):
                    self.player.take_damage(1)
                    
                    # Create collision effect
                    if ANIMATION_ENABLED:
                        self.create_explosion(
                            (enemy.x + self.player.x) / 2,
                            (enemy.y + self.player.y) / 2,
                            1.5,
                            (255, 150, 150)
                        )
                    
                    self.enemies.remove(enemy)
                    if self.player.health <= 0:
                        self.game_over = True
                        # Create large explosion for player defeat
                        if ANIMATION_ENABLED:
                            self.create_explosion(self.player.x, self.player.y, 2.0, (255, 100, 100))
                    break
                    
        # Boss with player
        if self.player and self.boss:
            if (abs(self.boss.x - self.player.x) < (self.boss.width + self.player.width)//2 and
                abs(self.boss.y - self.player.y) < (self.boss.height + self.player.height)//2):
                self.player.take_damage(3) # Boss collision is more damaging
                
                # Create heavy collision effect
                if ANIMATION_ENABLED:
                    self.create_explosion(
                        (self.boss.x + self.player.x) / 2,
                        (self.boss.y + self.player.y) / 2,
                        2.0,
                        (255, 100, 50)
                    )
                
                if self.player.health <= 0:
                    self.game_over = True
                    # Create large explosion for player defeat
                    if ANIMATION_ENABLED:
                        self.create_explosion(self.player.x, self.player.y, 2.5, (255, 50, 50))

    def handle_event(self, event, game_state):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.pause_button and not self.game_over:
                self.hide()
                game_state.change_state(STATE_PAUSED)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.game_over:
                new_lasers = self.player.shoot()
                if new_lasers:  # Only play sound if lasers were actually created
                    pygame.mixer.Sound.play(game_state.game.shoot_sound)
                self.player_lasers.extend(new_lasers)
            elif event.key == pygame.K_o and not self.game_over:
                # Only open ability selection if abilities are ready
                if game_state.ability_kill_counter >= ABILITY_ENEMY_KILL_THRESHOLD:
                    self.hide()
                    game_state.change_state(STATE_ABILITY_SELECT)
                    self.notification_active = False
                    self.notification_timer = 0
                    return True
        elif event.type == pygame.MOUSEMOTION and not self.game_over:
            # Check for enemy hover
            mouse_x, mouse_y = event.pos
            for enemy in self.enemies:
                if (abs(mouse_x - enemy.x) < enemy.width//2 and
                    abs(mouse_y - enemy.y) < enemy.height//2):
                    enemy.is_hovered = True
        return True 

    def create_boss_projectiles(self):
        """Create a pattern of laser projectiles from the boss"""
        if not self.boss:
            return
            
        # Create a spread of lasers
        num_lasers = 5
        angle_spread = 30  # Total spread in degrees
        start_angle = 90 - angle_spread/2
        
        for i in range(num_lasers):
            angle = start_angle + (angle_spread / (num_lasers-1)) * i
            projectile = EnemyProjectile(
                self.boss.x, 
                self.boss.y + self.boss.height//2,
                angle,
                "laser",
                damage=1,
                speed=7
            )
            self.enemy_projectiles.append(projectile)
            
            # Add visual effect for laser creation
            if ANIMATION_ENABLED:
                self.create_explosion(
                    self.boss.x, 
                    self.boss.y + self.boss.height//2,
                    0.3,
                    (255, 50, 50)
                )
            
    def create_boss_plasma(self):
        """Create homing plasma projectiles from the boss"""
        if not self.boss or not self.player:
            return
            
        # Calculate angle to player
        dx = self.player.x - self.boss.x
        dy = self.player.y - self.boss.y
        angle = math.degrees(math.atan2(dy, dx)) - 90  # Adjust by 90 to match our angle system
        
        # Create a large plasma projectile
        projectile = EnemyProjectile(
            self.boss.x, 
            self.boss.y + self.boss.height//2,
            angle,
            "plasma",
            damage=2,
            speed=4,
            width=15,
            height=15,
            health=3
        )
        self.enemy_projectiles.append(projectile)
        
        # Add visual effect for plasma creation
        if ANIMATION_ENABLED:
            self.create_explosion(
                self.boss.x, 
                self.boss.y + self.boss.height//2,
                1.0,
                (255, 100, 255)
            )
            
    def create_enemy_projectile(self, enemy):
        """Create a projectile from an enemy"""
        # Calculate firing angle (straight down)
        angle = 90
        
        # Different enemies have different projectiles
        if enemy.type == "Swarmer":
            # Swarmers fire small, fast projectiles
            return EnemyProjectile(
                enemy.x, 
                enemy.y + enemy.height//2,
                angle,
                "bullet",
                damage=1,
                speed=6
            )
        elif enemy.type == "Striker":
            # Strikers fire medium projectiles
            return EnemyProjectile(
                enemy.x, 
                enemy.y + enemy.height//2,
                angle,
                "plasma",
                damage=1,
                speed=5,
                width=10,
                height=10
            )
        elif enemy.type == "Destroyer":
            # Destroyers fire large, slow projectiles
            return EnemyProjectile(
                enemy.x, 
                enemy.y + enemy.height//2,
                angle,
                "plasma",
                damage=2,
                speed=3,
                width=15,
                height=15,
                health=2
            )
        elif enemy.type == "Harvester":
            # Harvesters fire medium, spreading projectiles
            angle_offset = random.uniform(-15, 15)
            return EnemyProjectile(
                enemy.x, 
                enemy.y + enemy.height//2,
                angle + angle_offset,
                "bullet",
                damage=1,
                speed=4
            )
        elif enemy.type == "SporeLauncher":
            # SporeLaunchers fire slow, large spore projectiles
            return EnemyProjectile(
                enemy.x, 
                enemy.y + enemy.height//2,
                angle,
                "spore",
                damage=1,
                speed=2,
                width=20,
                height=20,
                health=1
            )
            
        return None 