import pygame

# Initialize pygame to get display info
pygame.init()
info = pygame.display.Info()
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
WINDOW_WIDTH = DEFAULT_WIDTH
WINDOW_HEIGHT = DEFAULT_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)

# Game states
STATE_TITLE = 0
STATE_LEVEL_SELECT = 1
STATE_PLAYING = 2
STATE_PAUSED = 3
STATE_GAME_OVER = 4
STATE_ABILITY_SELECT = 5 # New state

# Game settings
FPS = 60
PLAYER_SPEED = 5
PLAYER_HEALTH = 5
PLAYER_SHIELD_MAX = 7  # Reduced shield health to absorb about 5 bullets
LASER_COOLDOWN = 15
POWER_UP_DURATION = 300  # 5 seconds at 60 FPS
ABILITY_ENEMY_KILL_THRESHOLD = 2 # Enemies to kill before ability select

# Ability Definitions
ABILITY_RAPID_FIRE = 'rapid_fire'
ABILITY_SHIELD = 'shield'
ABILITY_PIERCING = 'piercing'

ABILITIES = {
    ABILITY_RAPID_FIRE: {
        'name': "Rapid Fire",
        'description': "Fire twice as fast for 5 seconds.",
        'duration': 300 # 5 seconds * 60 FPS
    },
    ABILITY_SHIELD: {
        'name': "Energy Shield",
        'description': "Absorbs the next hit.",
        'duration': -1 # Duration not applicable, it's one hit
    },
    ABILITY_PIERCING: {
        'name': "Piercing Shot",
        'description': "Lasers pierce enemies for 5 seconds.",
        'duration': 300 # 5 seconds * 60 FPS
    }
}

# Enemy spawn settings
ENEMY_SPAWN_RATE = 60  # Frames between spawns
ENEMY_TYPES = ["Swarmer", "Striker", "Destroyer", "Harvester", "SporeLauncher"]
ENEMY_SPAWN_WEIGHTS = [0.4, 0.2, 0.1, 0.2, 0.1]  # Probability weights for each type

# Power-up settings
POWER_UP_SPAWN_RATE = 300  # Frames between spawns
POWER_UP_CHANCE = 0.2  # Chance to spawn when enemy is destroyed

# Boss Settings (Level 5)
BOSS_HEALTH = 150  # Increased from 100 for a more challenging fight
BOSS_SPEED = 1
BOSS_WIDTH = 150
BOSS_HEIGHT = 100
BOSS_SHOOT_COOLDOWN_LASER = 90
BOSS_SHOOT_COOLDOWN_PLASMA = 150

# Nebula Colors per Level (RGB, alpha added later)
# Getting progressively more red/brown
NEBULA_COLORS = [
    (10, 10, 30),  # Level 1 - Deep Blue/Purple
    (20, 10, 30),  # Level 2 - More Purple
    (30, 15, 20),  # Level 3 - Hint of Brown/Red
    (40, 20, 10),  # Level 4 - Brownish
    (50, 10, 10)   # Level 5 - Reddish/Brown
]
NEBULA_ALPHA = 100 # Base alpha for nebula color

# Asset paths
# Comment out the custom font path if you haven't downloaded the font yet
# FONT_PATH = "assets/fonts/galaxy_font.ttf"
FONT_PATH = None  # Using default font for now

# Font loading helper
def load_font(size):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except pygame.error:
        print(f"Warning: Font {FONT_PATH} not found or failed to load. Using default font.")
        return pygame.font.Font(None, size) # Fallback to default

# UI Scale settings
def get_scale_factor(current_width, current_height):
    width_scale = current_width / DEFAULT_WIDTH
    height_scale = current_height / DEFAULT_HEIGHT
    return min(width_scale, height_scale)

def get_centered_rect(width, height, screen_width, screen_height):
    return pygame.Rect(
        (screen_width - width) // 2,
        (screen_height - height) // 2,
        width,
        height
    )

# Title screen settings
TITLE_FONT_SIZE = 64
SUBTITLE_FONT_SIZE = 32
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_SPACING = 40

# Level select settings
LEVEL_BUTTON_SIZE = 150
LEVEL_BUTTON_SPACING = 40
LEVEL_ROWS = 2
LEVEL_COLS = 3

# Pause button settings
PAUSE_BUTTON_WIDTH = 100
PAUSE_BUTTON_HEIGHT = 40
PAUSE_BUTTON_MARGIN = 20
