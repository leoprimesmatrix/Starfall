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
ORANGE = (255, 165, 0)

# Game states
STATE_TITLE = 0
STATE_LEVEL_SELECT = 1
STATE_PLAYING = 2
STATE_PAUSED = 3
STATE_GAME_OVER = 4
STATE_ABILITY_SELECT = 5 # New state
STATE_DEBUG_MENU = 6 # Debug menu state
STATE_ENEMY_GALLERY = 7 # Enemy gallery screen
STATE_VICTORY = 8 # New state for winning the game

# Game settings
FPS = 60
PLAYER_SPEED = 5
PLAYER_HEALTH = 5
PLAYER_SHIELD_MAX = 7  # Reduced shield health to absorb about 5 bullets
LASER_COOLDOWN = 15
POWER_UP_DURATION = 300  # 5 seconds at 60 FPS
ABILITY_ENEMY_KILL_THRESHOLD = 5  # Changed from 2 to 5 enemies needed for ability selection

# Notification settings
NOTIFICATION_DURATION = 180  # 3 seconds at 60 FPS
NOTIFICATION_FADE_TIME = 60  # Last second will fade out

# Ability Definitions
ABILITY_RAPID_FIRE = 'rapid_fire'
ABILITY_SHIELD = 'shield'
ABILITY_PIERCING = 'piercing'

ABILITIES = {
    ABILITY_RAPID_FIRE: {
        'name': "Weapons Override",
        'description': "Overclocks weapon systems for double fire rate (5 sec).",
        'duration': 300 # 5 seconds * 60 FPS
    },
    ABILITY_SHIELD: {
        'name': "Energy Barrier",
        'description': "Emergency shield generator absorbs one hit.",
        'duration': -1 # Duration not applicable, it's one hit
    },
    ABILITY_PIERCING: {
        'name': "Plasma Infusion",
        'description': "Modifies laser ammo for target penetration (5 sec).",
        'duration': 300 # 5 seconds * 60 FPS
    }
}

# Enemy spawn settings
ENEMY_SPAWN_RATE = 60  # Frames between spawns
ENEMY_TYPES = ["Swarmer", "Striker", "Destroyer", "Harvester", "SporeLauncher"]
ENEMY_SPAWN_WEIGHTS = [0.4, 0.2, 0.1, 0.2, 0.1]  # Probability weights for each type

# Enemy level progression (which level each enemy first appears in)
ENEMY_LEVEL_PROGRESSION = {
    "Swarmer": 1,      # Available from level 1
    "Striker": 2,      # Available from level 2
    "Harvester": 3,    # Available from level 3
    "Destroyer": 4,    # Available from level 4
    "SporeLauncher": 4 # Available from level 4
}

# Enemy descriptions for the Kryll invasion theme
ENEMY_DESCRIPTIONS = {
    "Swarmer": "Fast Kryll scout unit designed for overwhelming numbers.",
    "Striker": "Medium Kryll fighter with plasma weaponry.",
    "Destroyer": "Heavy Kryll warship with devastating firepower.",
    "Harvester": "Resource collection unit that targets human settlements.",
    "SporeLauncher": "Biological warfare unit that spreads toxic Kryll spores."
}

# Mission/Level context for the Shattered Skies storyline
MISSION_DESCRIPTIONS = {
    1: "Assist with evacuation of New Haven Colony as the Kryll forces attack. Protect civilian transports.",
    2: "Defend the vital mining operations on Asteros-7. These resources are critical for the Federation's war effort.",
    3: "Kryll forces have surrounded the Orbital Research Station. Break through their lines and evacuate scientists.",
    4: "Secure the supply route from Federation shipyards to the front lines. Kryll ambushes must be neutralized.",
    5: "The Kryll command ship has been located. This is our chance to strike a decisive blow and halt their invasion."
}

# Power-up settings
POWER_UP_SPAWN_RATE = 300  # Frames between spawns
POWER_UP_CHANCE = 0.2  # Chance to spawn when enemy is destroyed

# Boss Settings (Level 5)
BOSS_HEALTH = 250  # Increased from 150 for a more challenging multi-phase fight
BOSS_SPEED = 1
BOSS_WIDTH = 150
BOSS_HEIGHT = 100
BOSS_SHOOT_COOLDOWN_LASER = 90
BOSS_SHOOT_COOLDOWN_PLASMA = 150
BOSS_SHOOT_COOLDOWN_SPREAD = 180  # Spread attack cooldown
BOSS_SHOOT_COOLDOWN_BEAM = 300  # New death beam attack (phase 4)
BOSS_SHOOT_COOLDOWN_MINES = 240  # New mine deployment (phase 5)
BOSS_NAME = "Kryll Command Carrier"

# Boss phase health thresholds (percentage of max health)
BOSS_PHASE_THRESHOLDS = [1.0, 0.8, 0.6, 0.4, 0.2]  # 5 phases at 100%, 80%, 60%, 40%, and 20% health

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

# Debug settings
DEBUG_MODE = True # Set to False to disable debug features in production

# Animation and transition settings
FADE_DURATION = 30  # Frames for fade transitions
SCREEN_TRANSITION_DURATION = 45  # Frames for screen transitions
BUTTON_HOVER_ALPHA = 40  # Alpha value for button hover effect
ANIMATION_ENABLED = True  # Can be toggled for performance

# Animation curves
def ease_in_out(t):
    """Smooth ease-in/ease-out function for animations. Input and output are 0.0 to 1.0."""
    return t * t * (3.0 - 2.0 * t)

def ease_out(t):
    """Ease-out function for animations. Input and output are 0.0 to 1.0."""
    return 1.0 - (1.0 - t) * (1.0 - t)
