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

        # Draw game objects
        for power_up in self.power_ups:
            power_up.draw(surface)
        # Draw Boss if it exists
        if self.boss:
            self.boss.draw(surface)
        # Draw regular enemies
        for enemy in self.enemies:
            enemy.draw(surface)
        for projectile in self.enemy_projectiles:
            projectile.draw(surface)
        for laser in self.player_lasers:
            laser.draw(surface)
        if self.player:
            self.player.draw(surface)

        # Draw UI (Score, Player Health Bar, Remaining Enemies)
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        scale = get_scale_factor(screen_width, screen_height)

        font_size = int(36 * scale)
        font = load_font(font_size) # Use helper

        # Score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(topleft=(int(20 * scale), int(20 * scale)))
        surface.blit(score_text, score_rect)

        # Remaining Enemies / Boss Health
        if game_state.is_boss_level() and self.boss:
            remaining_text_str = f"Boss Health: {self.boss.health}/{self.boss.max_health}"
            remaining_color = RED
        else:
            remaining = game_state.get_enemies_remaining()
            remaining_text_str = f"Enemies Remaining: {remaining}"
            remaining_color = WHITE

        remaining_text = font.render(remaining_text_str, True, remaining_color)
        # Calculate position based on pause button area
        pause_button_area_width = int((PAUSE_BUTTON_WIDTH + PAUSE_BUTTON_MARGIN * 2) * scale)
        remaining_rect = remaining_text.get_rect(topright=(screen_width - pause_button_area_width, int(20 * scale)))
        surface.blit(remaining_text, remaining_rect)

        # Player health bar is drawn by player.draw()

        # Level Completion Message
        if self.level_complete_timer > 0:
            complete_font_size = int(48 * scale)
            complete_font = load_font(complete_font_size) # Use helper
            next_level = game_state.current_level + 1
            if next_level <= 5:
                msg = f"Level {game_state.current_level} Complete! Unlocked Level {next_level}!"
            else:
                 msg = f"CONGRATULATIONS! Final Boss Defeated!"

            complete_text = complete_font.render(msg, True, YELLOW)
            complete_rect = complete_text.get_rect(center=(screen_width // 2, screen_height // 2))
            surface.blit(complete_text, complete_rect)

        # Draw damage flash
        if self.player:
            self.player.draw_damage_flash(surface)

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

    def spawn_power_up(self, x, y):
        self.power_ups.append(PowerUp(x, y))
        
    def update(self, game_state):
        if self.game_over or self.level_complete_timer > 0: # Pause updates during completion message
            if self.level_complete_timer > 0:
                self.level_complete_timer -= 1
                if self.level_complete_timer == 0:
                    game_state.change_state(STATE_LEVEL_SELECT)
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Update background
        for star in self.stars:
            star.update(screen_width, screen_height)
        self.nebula.update(screen_height)

        # Update player (Check added for player existence)
        if self.player:
            keys = pygame.key.get_pressed()
            dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
            dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * PLAYER_SPEED
            self.player.move(dx, dy, screen_width, screen_height)
            self.player.update()
            if self.player.health <= 0:
                self.game_over = True

        # Update Boss if it exists
        if self.boss:
            self.boss.update()
            new_projectiles = self.boss.shoot()
            self.enemy_projectiles.extend(new_projectiles)
        # Spawn regular enemies if not boss level
        elif not game_state.is_boss_level():
            if self.enemy_spawn_timer <= 0:
                self.spawn_enemy()
                self.enemy_spawn_timer = ENEMY_SPAWN_RATE
            else:
                self.enemy_spawn_timer -= 1

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            new_projectiles = enemy.shoot()
            self.enemy_projectiles.extend(new_projectiles)
            if enemy.y > screen_height + enemy.height:
                self.enemies.remove(enemy)

        # Update projectiles
        for projectile in self.enemy_projectiles[:]:
            projectile.update()
            if projectile.y > screen_height + projectile.height: # Check against projectile height
                 self.enemy_projectiles.remove(projectile)

        # Update lasers
        for laser in self.player_lasers[:]:
            laser.update()
            if laser.is_off_screen(screen_height):
                self.player_lasers.remove(laser)

        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.y > screen_height:
                self.power_ups.remove(power_up)

        # --- Check Collisions --- #
        # Player lasers with Boss
        if self.boss:
            for laser in self.player_lasers[:]:
                 if (abs(laser.x - self.boss.x) < self.boss.width//2 and
                     abs(laser.y - self.boss.y) < self.boss.height//2):
                     self.boss.health -= laser.damage
                     if not laser.piercing:
                         try:
                             self.player_lasers.remove(laser)
                         except ValueError: pass # Already removed (e.g., hit projectile first)
                     if self.boss.is_defeated():
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
                    laser_removed = False
                    if not laser.piercing:
                        try:
                            self.player_lasers.remove(laser)
                            laser_removed = True
                        except ValueError: pass # Already removed
                    if enemy.health <= 0:
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
                    laser_removed = False
                    if not laser.piercing:
                        try:
                            self.player_lasers.remove(laser)
                            laser_removed = True
                        except ValueError: pass

                    if should_remove_projectile:
                        try:
                           self.enemy_projectiles.remove(projectile)
                        except ValueError: pass # Already removed

                    if laser_removed:
                        break # Laser is gone

        # Enemy projectiles with player (Check added for player existence)
        if self.player:
            for projectile in self.enemy_projectiles[:]:
                 if (abs(projectile.x - self.player.x) < self.player.width//2 and
                     abs(projectile.y - self.player.y) < self.player.height//2):
                     self.player.take_damage(projectile.damage)
                     self.enemy_projectiles.remove(projectile)
                     # Game over check moved to player update section
                     break

        # Power-ups with player (Check added for player existence)
        if self.player:
            for power_up in self.power_ups[:]:
                 if (abs(power_up.x - self.player.x) < self.player.width//2 and
                     abs(power_up.y - self.player.y) < self.player.height//2):
                     self.player.power_up_active = True
                     self.player.power_up_timer = POWER_UP_DURATION
                     self.power_ups.remove(power_up)
                     break

        # Enemies with player (Check added for player existence)
        if self.player:
            for enemy in self.enemies[:]:
                 if (abs(enemy.x - self.player.x) < (enemy.width + self.player.width)//2 and
                     abs(enemy.y - self.player.y) < (enemy.height + self.player.height)//2):
                     self.player.take_damage(1)
                     self.enemies.remove(enemy)
                     # Game over check moved to player update section
                     break
        # Boss with player (Check added for player and boss existence)
        if self.player and self.boss:
            if (abs(self.boss.x - self.player.x) < (self.boss.width + self.player.width)//2 and
                abs(self.boss.y - self.player.y) < (self.boss.height + self.player.height)//2):
                self.player.take_damage(3) # Boss collision is more damaging
                # Don't remove boss on collision
                # Game over check moved to player update section

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
        elif event.type == pygame.MOUSEMOTION and not self.game_over:
            # Check for enemy hover
            mouse_x, mouse_y = event.pos
            for enemy in self.enemies:
                if (abs(mouse_x - enemy.x) < enemy.width//2 and
                    abs(mouse_y - enemy.y) < enemy.height//2):
                    enemy.is_hovered = True
        return True 