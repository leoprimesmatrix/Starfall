import pygame
import pygame_gui
import math
import random
from constants import *
from game_objects import Star, Nebula, PlayerShip, Laser, Enemy, EnemyProjectile, PowerUp, BossEnemy, Explosion
from utils import load_font, get_scale_factor, load_image
from pygame_gui.elements import UIButton

class PlayingScreen:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.pause_button = None
        self.is_visible = False
        self.height = screen.get_height() # Screen height for convenience

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
        self.frame_count = 0 # For timing certain effects
        
        # Boss Intro State
        self.show_boss_intro = False
        self.boss_intro_timer = 0
        
        # Notification system
        self.notification_active = False
        self.notification_timer = 0
        self.notification_text = None
        self.notification_rect = None
        
        # Visual effects
        self.particles = []
        self.explosions = []
        
        # Background
        self.background_image = None # To hold the level-specific background

        self.setup_ui() # Create UI elements
        self.hide()  # Hide UI elements initially

    def reset(self, game_state):
        """Resets the playing screen state for the current level in game_state."""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.height = screen_height # Update height property

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
        self.enemy_spawn_timer = ENEMY_SPAWN_RATE # Make sure timer is initialized with constant
        self.power_up_spawn_timer = 0
        self.game_over = False
        self.level_complete_timer = -1
        self.show_boss_intro = False # Reset boss intro flag
        self.boss_intro_timer = 0

        # Set nebula color for the level
        self.nebula.set_color_for_level(game_state.current_level)

        # Initialize stars for the current screen size
        self.init_stars()

        # Spawn boss if it's the boss level
        if game_state.is_boss_level():
            self.boss = BossEnemy(screen_width)
            
        # Generate procedural background for the level
        self.background_image = self.generate_background(game_state.current_level, screen_width, screen_height)

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
        self.height = screen_height # Update height property
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
        # Clear the screen with a black background
        surface.fill(BLACK)
        
        # Draw nebula (if used instead of background image)
        # self.nebula.draw(surface)
        
        # --- Add Red Tint Based on Player Health --- 
        if self.player and self.player.health < self.player.max_health:
            health_percentage = max(0, self.player.health / self.player.max_health)
            # Alpha increases as health decreases (max alpha around 120 for visibility)
            alpha = int((1 - health_percentage) * 120) 
            if alpha > 0:
                red_tint_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                red_tint_surface.fill((255, 0, 0, alpha))
                surface.blit(red_tint_surface, (0, 0))
        # --- End of Red Tint --- 

        # Draw stars in the background
        for star in self.stars:
            star.draw(surface)
        
        # Draw player
        if self.player:
            self.player.draw(surface)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface)
        
        # Draw boss
        if self.boss:
            self.boss.draw(surface)
        
        # Draw projectiles
        for proj in self.player_lasers:
            proj.draw(surface)
        
        for proj in self.enemy_projectiles:
            proj.draw(surface)
            
            # Special drawing for mine type projectiles
            if hasattr(proj, 'proj_type') and proj.proj_type == "mine":
                # Add spikes to mines
                for i in range(8):  # 8 spikes around the mine
                    angle = i * (math.pi/4)
                    spike_length = 8
                    end_x = proj.x + math.cos(angle) * spike_length
                    end_y = proj.y + math.sin(angle) * spike_length
                    pygame.draw.line(surface, RED, (proj.x, proj.y), (end_x, end_y), 2)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(surface)
        
        # Draw beam attack if active
        if self.boss and hasattr(self.boss, 'beam_active') and self.boss.beam_active:
            # Beam is already drawn in the boss's draw method
            # Add additional particles along beam path
            beam_start_x = self.boss.x
            beam_start_y = self.boss.y + self.boss.height//2 + 20
            beam_target_x = self.boss.beam_target_x
            beam_end_y = self.height
            
            # Calculate angle and length for beam
            angle = math.atan2(beam_end_y - beam_start_y, beam_target_x - beam_start_x)
            beam_length = math.sqrt((beam_end_y - beam_start_y)**2 + (beam_target_x - beam_start_x)**2)
            
            # Add particles along beam
            num_particles = int(beam_length / 20)  # One particle every 20 pixels
            for i in range(num_particles):
                # Calculate position along beam
                t = i / num_particles
                particle_x = beam_start_x + t * (beam_target_x - beam_start_x)
                particle_y = beam_start_y + t * (beam_end_y - beam_start_y)
                
                # Random offset perpendicular to beam
                perpendicular_angle = angle + math.pi/2
                offset = random.randint(-5, 5)
                particle_x += math.cos(perpendicular_angle) * offset
                particle_y += math.sin(perpendicular_angle) * offset
                
                # Draw particle
                size = random.randint(2, 5)
                color_intensity = random.randint(150, 255)
                color = (color_intensity, 50, 0)
                pygame.draw.circle(surface, color, (int(particle_x), int(particle_y)), size)
        
        # Draw UI
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        scale = get_scale_factor(screen_width, screen_height)
        
        # Draw current mission name - center at the very top
        mission_font_size = int(20 * scale)
        mission_font = load_font(mission_font_size)
        mission_name = f"Mission: {game_state.current_level} - {list(MISSION_DESCRIPTIONS.values())[game_state.current_level-1].split('.')[0]}"
        mission_text = mission_font.render(mission_name, True, LIGHT_GRAY)
        mission_rect = mission_text.get_rect(midtop=(screen_width // 2, int(10 * scale)))
        surface.blit(mission_text, mission_rect)

        # Draw score in top-left (but below mission text)
        score_font_size = int(24 * scale)
        score_font = load_font(score_font_size)
        score_text = score_font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(topleft=(int(20 * scale), int(40 * scale)))
        # Score text is now invisible but still calculated for future use
        # surface.blit(score_text, score_rect)
        
        # Get pause button area to avoid text overlap
        pause_button_area_width = self.pause_button.relative_rect.width + int(40 * scale)
        
        # Draw ship info if player exists
        if self.player:
            ship_font_size = int(16 * scale)
            ship_font = load_font(ship_font_size)
            ship_text = ship_font.render(f"Ship: {self.player.ship_name}", True, BLUE)
            ship_rect = ship_text.get_rect(midbottom=(screen_width // 2, screen_height - int(10 * scale)))
            surface.blit(ship_text, ship_rect)
        
        # Draw remaining enemies / Boss Health
        if game_state.is_boss_level() and self.boss:
            # Boss health bar instead of text
            bar_width = int(300 * scale)
            bar_height = int(20 * scale)
            bar_x = (screen_width - bar_width) // 2
            # Position boss health bar below mission name
            bar_y = int(120 * scale) 
            
            # Calculate health percentage and determine color
            health_percent = self.boss.health / self.boss.max_health
            if health_percent > 0.6:
                bar_color = GREEN
            elif health_percent > 0.3:
                bar_color = YELLOW
            else:
                bar_color = RED
                
            # Draw boss name centered above the bar
            boss_name_font = score_font
            boss_name_text = boss_name_font.render(f"{self.boss.name}", True, RED)
            # Position boss name above health bar
            boss_name_rect = boss_name_text.get_rect(midbottom=(bar_x + bar_width // 2, bar_y - int(5 * scale)))
            surface.blit(boss_name_text, boss_name_rect)
            
            # Draw background bar (empty)
            pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Draw filled portion of the bar
            filled_width = int(bar_width * health_percent)
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, filled_width, bar_height))
            
            # Draw border
            pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Optionally show numerical health values
            health_text = score_font.render(f"{self.boss.health}/{self.boss.max_health}", True, WHITE)
            health_text_rect = health_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
            surface.blit(health_text, health_text_rect)
        else:
            # Non-boss levels: Draw Enemies Remaining text in top-right
            enemies_remaining = game_state.get_enemies_remaining()
            remaining_text_str = f"Enemies Remaining: {enemies_remaining}"
            remaining_color = WHITE
            remaining_text = score_font.render(remaining_text_str, True, remaining_color)
            remaining_rect = remaining_text.get_rect(topright=(screen_width - pause_button_area_width, int(40 * scale)))
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
                    topright=(screen_width - int(20 * scale), int(70 * scale)))
            
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

        # Handle game over state - Simplified check
        if self.game_over:
            self.hide()  # Hide pause button
            game_state.score = self.score # Pass score before changing state
            game_state.change_state(STATE_GAME_OVER)

    def spawn_enemy(self, game_state):
        screen_width = self.screen.get_width()
        
        # Determine available enemy types based on current level
        available_types = []
        available_weights = []
        
        # Filter enemy types based on current level using ENEMY_LEVEL_PROGRESSION
        for enemy_type, min_level in ENEMY_LEVEL_PROGRESSION.items():
            if game_state.current_level >= min_level:
                available_types.append(enemy_type)
                
                # Add corresponding weight from original weights list
                if enemy_type in ENEMY_TYPES:
                    index = ENEMY_TYPES.index(enemy_type)
                    weight = ENEMY_SPAWN_WEIGHTS[index]
                    
                    # Adjust weights based on level progression
                    # Lower-tier enemies become less common in higher levels
                    level_difference = game_state.current_level - min_level
                    if level_difference > 0:
                        weight = max(0.1, weight - (level_difference * 0.1))
                        
                    available_weights.append(weight)
                else:
                    available_weights.append(0.1)  # Default weight if not found
        
        # If somehow no enemies are available, default to Swarmer
        if not available_types:
            available_types = ["Swarmer"]
            available_weights = [1.0]
            
        # Normalize weights to sum to 1
        weight_sum = sum(available_weights)
        if weight_sum > 0:
            available_weights = [w / weight_sum for w in available_weights]
            
        # Choose from available enemy types with their weights
        enemy_type = random.choices(available_types, weights=available_weights)[0]
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

        # Increment frame counter
        self.frame_count += 1
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Update background
        for star in self.stars:
            star.update(screen_width, screen_height)
        self.nebula.update(screen_height)

        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)
                
        # Handle all projectile collisions and explosions
        self.handle_projectiles()

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
            if self.boss.shoot_cooldown_laser <= 0:
                self.boss.shoot_cooldown_laser = BOSS_SHOOT_COOLDOWN_LASER
                # Create laser projectiles in a pattern
                self.create_boss_projectiles()
                
            if self.boss.shoot_cooldown_plasma <= 0:
                self.boss.shoot_cooldown_plasma = BOSS_SHOOT_COOLDOWN_PLASMA
                # Create plasma projectiles in a different pattern
                self.create_boss_plasma()
                
            self.boss.shoot_cooldown_laser -= 1
            self.boss.shoot_cooldown_plasma -= 1
        
        # Spawn enemies according to level
        if not game_state.is_boss_level() and len(self.enemies) < game_state.get_max_enemies() and not game_state.check_level_complete():
            self.enemy_spawn_timer -= 1
            if self.enemy_spawn_timer <= 0:
                self.spawn_enemy(game_state)
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
                self.show_boss_intro = True
                self.boss_intro_timer = 180 # Show for 3 seconds (60 FPS * 3)
                
        # Update boss intro timer
        if self.show_boss_intro:
            self.boss_intro_timer -= 1
            if self.boss_intro_timer <= 0:
                self.show_boss_intro = False
        
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
            
        # Create an Explosion object and add it to explosions list
        explosion = Explosion(x, y, size * 20, duration=30, color=color)
        self.explosions.append(explosion)
        
        # Still create particles for additional effect if wanted
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
                    # Call take_damage instead of directly modifying health
                    self.boss.take_damage(laser.damage) 
                    
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
                        game_state.score = self.score # Update final score in game_state
                        game_state.boss_defeated = True # Ensure this is set
                        # Don't complete level here, transition to victory screen
                        if hasattr(game_state.game, 'change_state_with_transition'):
                            game_state.game.change_state_with_transition(STATE_VICTORY)
                        else:
                            game_state.change_state(STATE_VICTORY)
                        self.boss = None # Remove boss object
                    
                    if not laser.piercing:
                        break # Laser is gone

        # Player lasers with enemies
        for laser in self.player_lasers[:]:
            for enemy in self.enemies[:]:
                if (abs(laser.x - enemy.x) < enemy.width//2 and
                    abs(laser.y - enemy.y) < enemy.height//2):
                    
                    # Call take_damage and check if enemy was killed
                    enemy_killed = enemy.take_damage(laser.damage)
                    
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
                    
                    # Only record defeat if enemy was actually killed by laser
                    if enemy_killed:
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
                    
                    # Check if the hit depletes health
                    player_killed = self.player.take_damage(projectile.damage)
                    
                    # Create hit effect on player
                    if ANIMATION_ENABLED:
                        self.create_explosion(projectile.x, projectile.y, 0.7, (255, 50, 50))
                    
                    self.enemy_projectiles.remove(projectile)
                    
                    # Set game_over flag if player health depleted
                    if player_killed:
                        self.game_over = True
                        # Create large explosion for player defeat
                        if ANIMATION_ENABLED:
                            self.create_explosion(self.player.x, self.player.y, 2.0, (255, 100, 100))
                    break

        # Enemies with player
        if self.player:
            for enemy in self.enemies[:]:
                if (abs(enemy.x - self.player.x) < (enemy.width + self.player.width)//2 and
                    abs(enemy.y - self.player.y) < (enemy.height + self.player.height)//2):
                    
                    # Check if the hit depletes health
                    player_killed = self.player.take_damage(1) # Enemy collision damage
                    
                    # Create collision effect
                    if ANIMATION_ENABLED:
                        self.create_explosion(
                            (enemy.x + self.player.x) / 2,
                            (enemy.y + self.player.y) / 2,
                            1.5,
                            (255, 150, 150)
                        )
                    
                    # Remove the enemy that collided
                    self.enemies.remove(enemy) 
                    
                    # Record defeat when enemy collides with player
                    game_state.record_enemy_defeat()
                    # Check for level completion after this defeat
                    if not game_state.is_boss_level() and game_state.check_level_complete():
                        game_state.complete_current_level()
                        self.level_complete_timer = 180
                    
                    # Set game_over flag if player health depleted
                    if player_killed:
                        self.game_over = True
                        # Create large explosion for player defeat
                        if ANIMATION_ENABLED:
                            self.create_explosion(self.player.x, self.player.y, 2.0, (255, 100, 100))
                    break # Enemy hit player, stop checking this enemy
                    
        # Boss with player
        if self.player and self.boss:
            if (abs(self.boss.x - self.player.x) < (self.boss.width + self.player.width)//2 and
                abs(self.boss.y - self.player.y) < (self.boss.height + self.player.height)//2):
                
                # Check if the hit depletes health
                player_killed = self.player.take_damage(3) # Boss collision damage
                
                # Create heavy collision effect
                if ANIMATION_ENABLED:
                    self.create_explosion(
                        (self.boss.x + self.player.x) / 2,
                        (self.boss.y + self.player.y) / 2,
                        2.0,
                        (255, 100, 50)
                    )
                
                # Set game_over flag if player health depleted
                if player_killed:
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

    def generate_background(self, level, width, height):
        """Generate a procedural background based on the level"""
        # Create a base surface for the background
        bg_surface = pygame.Surface((width, height))
        
        # Choose color scheme based on level
        if level == 1:  # Blue nebula theme
            bg_color = (0, 0, 40)
            shape_colors = [(20, 40, 100), (30, 60, 120), (40, 80, 150)]
        elif level == 2:  # Red nebula theme
            bg_color = (40, 0, 0)
            shape_colors = [(100, 20, 20), (130, 30, 30), (150, 40, 40)]
        elif level == 3:  # Green nebula theme
            bg_color = (0, 30, 0)
            shape_colors = [(20, 80, 20), (30, 100, 30), (40, 120, 40)]
        elif level == 4:  # Purple nebula theme
            bg_color = (30, 0, 30)
            shape_colors = [(60, 20, 60), (80, 30, 80), (100, 40, 100)]
        elif level == 5:  # Boss level - dark ominous theme
            bg_color = (20, 0, 10)
            shape_colors = [(60, 0, 30), (80, 10, 40), (100, 20, 50)]
        else:
            bg_color = (0, 0, 0)
            shape_colors = [(30, 30, 30), (40, 40, 40), (50, 50, 50)]
            
        # Fill background with base color
        bg_surface.fill(bg_color)
        
        # Draw procedural shapes based on level
        # Level 1: Circles
        if level == 1:
            for _ in range(20):
                x = random.randint(0, width)
                y = random.randint(0, height)
                radius = random.randint(50, 200)
                color = random.choice(shape_colors)
                # Apply transparency to the circle
                circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                alpha = random.randint(30, 80)
                pygame.draw.circle(circle_surface, color + (alpha,), (radius, radius), radius)
                bg_surface.blit(circle_surface, (x - radius, y - radius))
                
        # Level 2: Swirls (approximated with circles)
        elif level == 2:
            for i in range(5):
                center_x = random.randint(width // 4, 3 * width // 4)
                center_y = random.randint(height // 4, 3 * height // 4)
                max_radius = random.randint(100, 300)
                color = random.choice(shape_colors)
                
                # Create a spiral effect with circles
                for j in range(15):
                    angle = j * 0.5
                    radius = 10 + j * 10
                    if radius > max_radius:
                        break
                    x = center_x + int(math.cos(angle) * radius)
                    y = center_y + int(math.sin(angle) * radius)
                    alpha = random.randint(40, 90)
                    
                    circle_surface = pygame.Surface((radius, radius), pygame.SRCALPHA)
                    pygame.draw.circle(circle_surface, color + (alpha,), (radius // 2, radius // 2), radius // 2)
                    bg_surface.blit(circle_surface, (x - radius // 2, y - radius // 2))
                    
        # Level 3: Grid pattern
        elif level == 3:
            grid_size = 100
            line_thickness = 2
            for x in range(0, width, grid_size):
                for y in range(0, height, grid_size):
                    color = random.choice(shape_colors)
                    alpha = random.randint(20, 60)
                    pygame.draw.rect(bg_surface, color + (alpha,), 
                                     pygame.Rect(x, y, grid_size, grid_size), line_thickness)
                    
        # Level 4: Diagonal lines
        elif level == 4:
            for _ in range(30):
                start_x = random.randint(-width // 2, width)
                start_y = random.randint(-height // 2, height)
                length = random.randint(300, 800)
                thickness = random.randint(2, 8)
                color = random.choice(shape_colors)
                alpha = random.randint(30, 70)
                
                end_x = start_x + length
                end_y = start_y + length
                
                line_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.line(line_surface, color + (alpha,), (start_x, start_y), (end_x, end_y), thickness)
                bg_surface.blit(line_surface, (0, 0))
                
        # Level 5: Boss level - ominous triangles
        elif level == 5:
            for _ in range(15):
                points = []
                center_x = random.randint(0, width)
                center_y = random.randint(0, height)
                
                # Generate triangle points
                size = random.randint(100, 350)
                for i in range(3):
                    angle = i * (2*math.pi/3) + random.uniform(0, 0.5)
                    x = center_x + int(math.cos(angle) * size)
                    y = center_y + int(math.sin(angle) * size)
                    points.append((x, y))
                
                color = random.choice(shape_colors)
                alpha = random.randint(30, 90)
                
                # Draw the triangle with alpha
                triangle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.polygon(triangle_surface, color + (alpha,), points)
                bg_surface.blit(triangle_surface, (0, 0))
                
        return bg_surface 

    def handle_projectiles(self):
        # Make sure we have a valid height property
        if not hasattr(self, 'height') or self.height is None:
            self.height = self.screen.get_height()
            
        # Keep track of explosions to add
        new_explosions = []
        
        # Update and check player projectiles
        for proj in self.player_lasers[:]:
            proj.update()
            
            # Check if hit any enemy
            for enemy in self.enemies[:]:
                if self.check_collision(proj, enemy):
                    # Damage the enemy and remove projectile
                    enemy.take_damage(proj.damage)
                    if enemy.health <= 0:
                        # Create explosion
                        explosion = Explosion(enemy.x, enemy.y, enemy.width)
                        new_explosions.append(explosion)
                        self.enemies.remove(enemy)
                        # Add to score
                        self.score += 100
                    # Create small explosion for projectile
                    small_explosion = Explosion(proj.x, proj.y, 20)
                    new_explosions.append(small_explosion)
                    if proj in self.player_lasers:
                        self.player_lasers.remove(proj)
                    break
            
            # Check if hit boss
            if self.boss and self.check_collision(proj, self.boss):
                # Damage boss
                self.boss.take_damage(proj.damage)
                # Create small explosion for projectile
                explosion = Explosion(proj.x, proj.y, 20)
                new_explosions.append(explosion)
                if proj in self.player_lasers:
                    self.player_lasers.remove(proj)
            
            # Remove if off screen
            if proj.y < 0:
                if proj in self.player_lasers:
                    self.player_lasers.remove(proj)
        
        # Update and check enemy projectiles
        for proj in self.enemy_projectiles[:]:
            proj.update()
            
            # Check if hit player
            if self.player and self.check_collision(proj, self.player) and not self.player.is_invulnerable():
                # Damage player
                self.player.take_damage(proj.damage)
                # Create explosion
                explosion = Explosion(proj.x, proj.y, 20)
                new_explosions.append(explosion)
                # Remove projectile
                if proj.type == "plasma":
                    # Plasma has health and can survive hits
                    proj.take_damage(1)
                    if proj.health <= 0 and proj in self.enemy_projectiles:
                        self.enemy_projectiles.remove(proj)
                elif proj.type == "mine":
                    # Mines explode on contact creating a larger explosion
                    big_explosion = Explosion(proj.x, proj.y, 50)
                    new_explosions.append(big_explosion)
                    # Extra damage to player from mine explosion
                    self.player.take_damage(2)
                    if proj in self.enemy_projectiles:
                        self.enemy_projectiles.remove(proj)
                else:
                    # Regular projectiles are removed on hit
                    if proj in self.enemy_projectiles:
                        self.enemy_projectiles.remove(proj)
            
            # Special handling for mine projectiles
            if proj.type == "mine":
                # Make mines hover in place after reaching a certain Y position
                if proj.y > self.height * 0.6:
                    proj.speed = 0
                    # Mines pulse to alert player
                    if random.random() < 0.05:  # 5% chance each frame
                        mine_pulse = Explosion(proj.x, proj.y, 15, duration=20, color=(255, 100, 0))
                        new_explosions.append(mine_pulse)
            
            # Remove if off screen
            if proj.y > self.height:
                if proj in self.enemy_projectiles:
                    self.enemy_projectiles.remove(proj)
        
        # Add new explosions
        self.explosions.extend(new_explosions)
        
        # Handle beam attack if boss is active
        if self.boss and hasattr(self.boss, 'beam_active') and self.boss.beam_active:
            # Calculate beam path and check for player collision
            beam_start_x = self.boss.x
            beam_start_y = self.boss.y + self.boss.height//2 + 20
            beam_target_x = self.boss.beam_target_x
            beam_end_y = self.height
            
            # Calculate angle of beam in radians
            angle = math.atan2(beam_end_y - beam_start_y, beam_target_x - beam_start_x)
            
            # Check if player is in beam path
            if self.player and not self.player.is_invulnerable():
                # Calculate player distance from beam line
                # Line is from (beam_start_x, beam_start_y) to (beam_target_x, beam_end_y)
                # Using point-line distance formula
                x0, y0 = self.player.x, self.player.y
                x1, y1 = beam_start_x, beam_start_y
                x2, y2 = beam_target_x, beam_end_y
                
                # Distance from point to line calculation
                numerator = abs((x2-x1)*(y1-y0) - (x1-x0)*(y2-y1))
                denominator = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                distance = numerator/denominator if denominator != 0 else float('inf')
                
                # If player is close enough to beam and beyond the start point
                beam_width = 10  # Width of beam for collision
                player_in_beam_path = distance < (beam_width + self.player.width/2)
                
                # Check if player is beyond start point in beam direction
                player_beyond_start = False
                if angle < math.pi/2:  # Beam goes right and down
                    player_beyond_start = (self.player.x > beam_start_x and self.player.y > beam_start_y)
                else:  # Beam goes left and down
                    player_beyond_start = (self.player.x < beam_start_x and self.player.y > beam_start_y)
                
                if player_in_beam_path and player_beyond_start:
                    # Player hit by beam, apply damage every few frames
                    if self.frame_count % 5 == 0:  # Every 5 frames
                        self.player.take_damage(1)
                        # Small explosion effect
                        hit_effect = Explosion(self.player.x, self.player.y, 15, duration=10, color=(255, 50, 0))
                        self.explosions.append(hit_effect)

    def check_collision(self, proj, obj):
        """Check if a projectile hits an object"""
        if isinstance(proj, Laser):
            if isinstance(obj, Enemy):
                return (abs(proj.x - obj.x) < obj.width//2 and
                        abs(proj.y - obj.y) < obj.height//2)
            elif isinstance(obj, BossEnemy):
                return (abs(proj.x - obj.x) < obj.width//2 and
                        abs(proj.y - obj.y) < obj.height//2)
        elif isinstance(proj, EnemyProjectile):
            if isinstance(obj, PlayerShip):
                return (abs(proj.x - obj.x) < obj.width//2 and
                        abs(proj.y - obj.y) < obj.height//2)
        return False 

    def spawn_boss(self):
        """Create the boss enemy for the boss level"""
        screen_width = self.screen.get_width()
        self.boss = BossEnemy(screen_width)
        # Add dramatic effect
        for _ in range(5):
            explosion = Explosion(
                random.randint(0, screen_width),
                random.randint(0, self.height // 3), 
                size=random.randint(30, 80),
                color=(255, 0, 0)
            )
            self.explosions.append(explosion) 