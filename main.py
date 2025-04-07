import pygame
import pygame_gui
import sys
import math
from constants import *
from game_state import GameState
from title_screen import TitleScreen
from level_select import LevelSelect
from playing_screen import PlayingScreen
from pause_screen import PauseScreen
from game_over_screen import GameOverScreen
from ability_selection_screen import AbilitySelectionScreen
from debug_menu import DebugMenu
from enemy_gallery import EnemyGallery

class TransitionSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_active = False
        self.timer = 0
        self.duration = SCREEN_TRANSITION_DURATION
        self.transition_type = "fade"  # Default transition type
        self.from_state = None
        self.to_state = None
        self.callback = None
        
        # Create fade surface
        self.fade_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.fade_surface.fill(BLACK)
        
    def start_transition(self, from_state, to_state, transition_type="fade", callback=None):
        self.is_active = True
        self.timer = 0
        self.from_state = from_state
        self.to_state = to_state
        self.transition_type = transition_type
        self.callback = callback
        
    def update(self):
        if not self.is_active:
            return False
            
        self.timer += 1
        
        # Check if transition completed
        if self.timer >= self.duration:
            self.is_active = False
            self.timer = 0
            # Execute callback if provided
            if self.callback:
                self.callback()
            return True
            
        return False
        
    def draw(self, surface):
        if not self.is_active:
            return
            
        progress = self.timer / self.duration
        
        if self.transition_type == "fade":
            # First half: fade out, second half: fade in
            if progress < 0.5:
                # Fade out (0 to 255)
                alpha = int(ease_in_out(progress * 2) * 255)
            else:
                # Fade in (255 to 0)
                alpha = int(255 - ease_in_out((progress - 0.5) * 2) * 255)
                
            self.fade_surface.set_alpha(alpha)
            surface.blit(self.fade_surface, (0, 0))
            
        elif self.transition_type == "wipe_left":
            if progress < 0.5:
                # Wipe from right to left (covering old screen)
                width = int(self.screen_width * ease_in_out(progress * 2))
                pygame.draw.rect(surface, BLACK, (self.screen_width - width, 0, width, self.screen_height))
            else:
                # Wipe from left to right (revealing new screen)
                width = int(self.screen_width * (1 - ease_in_out((progress - 0.5) * 2)))
                pygame.draw.rect(surface, BLACK, (0, 0, width, self.screen_height))
    
    def resize(self, new_width, new_height):
        self.screen_width = new_width
        self.screen_height = new_height
        self.fade_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.fade_surface.fill(BLACK)

class StarfallGame:
    def __init__(self):
        pygame.init()
        
        # Initialize sound system
        pygame.mixer.init()
        self.shoot_sound = pygame.mixer.Sound('shoot.wav')
        
        self.screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Starfall: The Kryll Invasion")
        
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.game_state.game = self  # Set reference to this game instance
        self.manager = pygame_gui.UIManager((DEFAULT_WIDTH, DEFAULT_HEIGHT), 'theme.json')
        
        # Initialize transition system
        self.transition = TransitionSystem(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        
        # Initialize screens
        self.title_screen = TitleScreen(self.screen, self.manager)
        self.level_select = LevelSelect(self.screen, self.manager)
        self.playing_screen = PlayingScreen(self.screen, self.manager)
        self.pause_screen = PauseScreen(self.screen, self.manager)
        self.game_over_screen = GameOverScreen(self.screen, self.manager)
        self.ability_selection_screen = AbilitySelectionScreen(self.screen, self.manager)
        self.debug_menu = DebugMenu(self.screen, self.manager)
        self.enemy_gallery = EnemyGallery(self.screen, self.manager)
        
        # Show initial screen
        self.title_screen.show()
        
    def handle_resize(self, event):
        # Store current UI states before recreating
        title_visible = self.game_state.current_state == STATE_TITLE
        level_select_visible = self.game_state.current_state == STATE_LEVEL_SELECT
        playing_visible = self.game_state.current_state == STATE_PLAYING
        pause_visible = self.game_state.current_state == STATE_PAUSED
        game_over_visible = self.game_state.current_state == STATE_GAME_OVER
        ability_select_visible = self.game_state.current_state == STATE_ABILITY_SELECT
        debug_menu_visible = self.game_state.current_state == STATE_DEBUG_MENU
        enemy_gallery_visible = self.game_state.current_state == STATE_ENEMY_GALLERY
        
        # Hide all UI elements before recreating them
        self.title_screen.hide()
        self.level_select.hide()
        self.playing_screen.hide()
        self.pause_screen.hide()
        self.game_over_screen.hide()
        self.ability_selection_screen.hide()
        self.debug_menu.hide()
        self.enemy_gallery.hide()
        
        # Clear all UI elements
        self.manager.clear_and_reset()
        
        # Update screen size
        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        
        # Update transition system
        self.transition.resize(event.w, event.h)
        
        # Update UI manager
        self.manager.set_window_resolution((event.w, event.h))
        
        # Update all screens
        self.title_screen.screen = self.screen
        self.level_select.screen = self.screen
        self.playing_screen.screen = self.screen
        self.pause_screen.screen = self.screen
        self.game_over_screen.screen = self.screen
        self.ability_selection_screen.screen = self.screen
        self.debug_menu.screen = self.screen
        self.enemy_gallery.screen = self.screen
        
        # Recreate UI elements for each screen
        self.title_screen.setup_ui()
        self.level_select.setup_ui()
        self.playing_screen.setup_ui()
        self.pause_screen.setup_ui()
        self.game_over_screen.setup_ui()
        self.ability_selection_screen.setup_ui()
        self.debug_menu.setup_ui()
        self.enemy_gallery.setup_ui()
        
        # Restore visibility states
        if title_visible:
            self.title_screen.show()
        if level_select_visible:
            self.level_select.show()
        if playing_visible:
            self.playing_screen.show()
        if pause_visible:
            self.pause_screen.show()
        if game_over_visible:
            self.game_over_screen.show()
        if ability_select_visible:
            self.ability_selection_screen.show()
        if debug_menu_visible:
            self.debug_menu.show()
        if enemy_gallery_visible:
            self.enemy_gallery.show()
            
    def toggle_fullscreen(self):
        # Store current window state
        current_state = self.game_state.current_state
        
        # Get current display info
        info = pygame.display.Info()
        
        if self.screen.get_flags() & pygame.FULLSCREEN:
            # Switch to windowed mode
            new_screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE)
            self.handle_resize(pygame.event.Event(pygame.VIDEORESIZE, {'w': DEFAULT_WIDTH, 'h': DEFAULT_HEIGHT}))
        else:
            # Switch to fullscreen mode
            new_screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            self.handle_resize(pygame.event.Event(pygame.VIDEORESIZE, {'w': info.current_w, 'h': info.current_h}))
            
    def run(self):
        running = True
        last_state = self.game_state.current_state
        
        while running:
            time_delta = self.clock.tick(FPS)/1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_g and DEBUG_MODE and self.game_state.current_state == STATE_PLAYING:
                        # Toggle debug menu with G key when in playing state
                        self.change_state_with_transition(STATE_DEBUG_MENU)
                    
                # Pass event to the currently active screen's handler
                # The player object is needed for ability selection
                player_obj = self.playing_screen.player if hasattr(self.playing_screen, 'player') else None

                if self.game_state.current_state == STATE_TITLE:
                    if not self.title_screen.handle_event(event, self.game_state):
                        running = False
                elif self.game_state.current_state == STATE_LEVEL_SELECT:
                    if not self.level_select.handle_event(event, self.game_state):
                        running = False
                elif self.game_state.current_state == STATE_PLAYING:
                    # Playing screen doesn't need player passed to its handler
                    if not self.playing_screen.handle_event(event, self.game_state):
                        running = False
                elif self.game_state.current_state == STATE_PAUSED:
                    if not self.pause_screen.handle_event(event, self.game_state):
                        running = False
                elif self.game_state.current_state == STATE_GAME_OVER:
                    if not self.game_over_screen.handle_event(event, self.game_state):
                        running = False
                elif self.game_state.current_state == STATE_ABILITY_SELECT:
                    if player_obj:
                         if not self.ability_selection_screen.handle_event(event, self.game_state, player_obj):
                              running = False # Should not happen, but safety check
                    else:
                         # Should not happen - can't select ability without player
                         self.game_state.change_state(STATE_PLAYING)
                elif self.game_state.current_state == STATE_DEBUG_MENU:
                    if not self.debug_menu.handle_event(event, self.game_state, self.playing_screen):
                        running = False
                elif self.game_state.current_state == STATE_ENEMY_GALLERY:
                    if not self.enemy_gallery.handle_event(event, self.game_state):
                        running = False

                # Always process manager events
                self.manager.process_events(event)
            
            # Update transition system
            transition_complete = self.transition.update()
            
            # Only change screen visibility if not transitioning
            if last_state != self.game_state.current_state and not self.transition.is_active:
                # Handle state changes
                # Hide all screens first
                self.title_screen.hide()
                self.level_select.hide()
                self.playing_screen.hide()
                self.pause_screen.hide()
                self.game_over_screen.hide()
                self.ability_selection_screen.hide()
                self.debug_menu.hide()
                self.enemy_gallery.hide()
                
                # Show only the current screen
                if self.game_state.current_state == STATE_TITLE:
                    self.title_screen.show()
                elif self.game_state.current_state == STATE_LEVEL_SELECT:
                    self.level_select.show()
                elif self.game_state.current_state == STATE_PLAYING:
                    # Reset is only needed when STARTING a level, not resuming
                    if last_state != STATE_PAUSED and last_state != STATE_ABILITY_SELECT and last_state != STATE_DEBUG_MENU:
                         self.playing_screen.reset(self.game_state)
                    self.playing_screen.show()
                elif self.game_state.current_state == STATE_PAUSED:
                    self.pause_screen.show()
                elif self.game_state.current_state == STATE_GAME_OVER:
                    self.game_over_screen.show()
                elif self.game_state.current_state == STATE_ABILITY_SELECT:
                     # setup_ui was called above when state change was detected
                    self.ability_selection_screen.show()
                elif self.game_state.current_state == STATE_DEBUG_MENU:
                    self.debug_menu.show()
                elif self.game_state.current_state == STATE_ENEMY_GALLERY:
                    self.enemy_gallery.show()
                    self.enemy_gallery.update_enemy_display() # Make sure enemy display is updated
                
                last_state = self.game_state.current_state

            # Update game state if playing
            if self.game_state.current_state == STATE_PLAYING:
                self.playing_screen.update(self.game_state)
                # Don't automatically show ability screen anymore - player must press O key
                # This section is now handled in PlayingScreen.handle_event
            
            # Update UI manager
            self.manager.update(time_delta)
            
            # Update animations
            if self.game_state.current_state == STATE_TITLE:
                self.title_screen.update_animation()
            elif self.game_state.current_state == STATE_LEVEL_SELECT:
                self.level_select.update_animation()
            
            # Draw
            self.screen.fill(BLACK)
            
            if self.game_state.current_state == STATE_TITLE:
                self.title_screen.draw(self.screen)
            elif self.game_state.current_state == STATE_LEVEL_SELECT:
                self.level_select.draw(self.screen, self.game_state)
            elif self.game_state.current_state in [STATE_PLAYING, STATE_PAUSED, STATE_ABILITY_SELECT, STATE_DEBUG_MENU]:
                 if self.playing_screen.player: # Check if player exists (after reset)
                    self.playing_screen.draw(self.screen, self.game_state)
            elif self.game_state.current_state == STATE_GAME_OVER:
                # Draw the playing screen first, then the game over overlay
                if self.playing_screen.player:
                    self.playing_screen.draw(self.screen, self.game_state)
                self.game_over_screen.draw(self.screen, self.game_state)
            elif self.game_state.current_state == STATE_ENEMY_GALLERY:
                self.enemy_gallery.draw(self.screen)
            
            # Draw overlays on top
            if self.game_state.current_state == STATE_PAUSED:
                self.pause_screen.draw(self.screen, self.game_state)
            elif self.game_state.current_state == STATE_ABILITY_SELECT:
                 self.ability_selection_screen.draw(self.screen)
            elif self.game_state.current_state == STATE_DEBUG_MENU:
                 self.debug_menu.draw(self.screen)
                 
            # Draw transition effect on top of everything
            self.transition.draw(self.screen)
            
            self.manager.draw_ui(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

    def change_state_with_transition(self, new_state, transition_type="fade"):
        """Change game state with a smooth transition animation"""
        current_state = self.game_state.current_state
        
        # Don't transition if we're already transitioning
        if self.transition.is_active:
            return
            
        # Define a callback function to change the state after the transition
        def change_state_after_transition():
            self.game_state.change_state(new_state)
        
        # Start the transition
        self.transition.start_transition(
            current_state,
            new_state,
            transition_type=transition_type,
            callback=change_state_after_transition
        )

if __name__ == "__main__":
    game = StarfallGame()
    game.run()
