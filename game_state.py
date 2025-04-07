import pygame
from constants import *

class GameState:
    def __init__(self):
        self.current_state = STATE_TITLE
        self.current_level = 1
        self.level_unlocks = {1: True, 2: False, 3: False, 4: False, 5: False}
        self.score = 0
        # Track enemies needed per level (example values, adjust as needed)
        self.enemies_per_level = {1: 10, 2: 15, 3: 20, 4: 25, 5: 0} # Level 5 has boss, not counter
        self.enemies_defeated_this_level = 0
        self.ability_kill_counter = 0 # Counter for ability screen trigger
        self.boss_defeated = False  # Track if the final boss has been defeated
        self.game = None  # Reference to main game instance, set after initialization
        
    def change_state(self, new_state):
        # Reset level-specific counters when changing state
        if self.current_state == STATE_PLAYING and new_state not in [STATE_PAUSED, STATE_ABILITY_SELECT]:
            self.enemies_defeated_this_level = 0
            self.ability_kill_counter = 0 # Reset ability counter too
        elif self.current_state == STATE_PAUSED and new_state == STATE_PLAYING:
             pass # Don't reset when resuming
        elif new_state == STATE_PLAYING and self.current_state != STATE_ABILITY_SELECT: # Don't reset if coming *from* ability select
             self.enemies_defeated_this_level = 0
             self.ability_kill_counter = 0

        self.current_state = new_state
        
    def unlock_level(self, level):
        if level in self.level_unlocks:
            self.level_unlocks[level] = True
            
    def is_level_unlocked(self, level):
        return self.level_unlocks.get(level, False)
        
    def complete_current_level(self):
        next_level = self.current_level + 1
        if next_level <= 5: # Check bounds
             self.unlock_level(next_level)
        self.enemies_defeated_this_level = 0 # Reset counter
        
        # Set boss_defeated flag if level 5 is completed
        if self.current_level == 5:
            self.boss_defeated = True
        
    def reset_game(self):
        # Reset score but keep unlocks
        self.score = 0
        # Reset to level 1 for play again
        self.current_level = 1
        self.enemies_defeated_this_level = 0
        self.ability_kill_counter = 0
        self.boss_defeated = False  # Reset boss defeated status

    def get_enemies_remaining(self):
        target = self.enemies_per_level.get(self.current_level, 0)
        # For boss level, remaining is 1 (the boss itself) until defeated
        if self.is_boss_level():
             return 1 # Placeholder until boss is implemented properly
        return max(0, target - self.enemies_defeated_this_level)

    def record_enemy_defeat(self):
        if not self.is_boss_level():
             self.enemies_defeated_this_level += 1
             self.ability_kill_counter += 1

    def is_boss_level(self):
        return self.current_level == 5

    def check_level_complete(self):
         if self.is_boss_level():
              # Boss completion logic will be handled elsewhere (when boss health <= 0)
              return False
         else:
              target = self.enemies_per_level.get(self.current_level, 0)
              return self.enemies_defeated_this_level >= target

    def should_show_ability_select(self):
        # Don't show on boss level or if already completed
        if self.is_boss_level() or self.check_level_complete():
            return False
        return self.ability_kill_counter >= ABILITY_ENEMY_KILL_THRESHOLD

    def reset_ability_counter(self):
        self.ability_kill_counter = 0
