import pygame
import os
from constants import DEFAULT_WIDTH, DEFAULT_HEIGHT, FONT_PATH

# Font loading helper
def load_font(size):
    try:
        # Use constants.FONT_PATH if available, otherwise use default
        font_path = pygame.font.get_default_font()
        if FONT_PATH is not None:
            font_path = FONT_PATH
        return pygame.font.Font(font_path, size)
    except pygame.error:
        print(f"Warning: Font {font_path} not found or failed to load. Using default font.")
        return pygame.font.Font(None, size)  # Fallback to default

# UI Scale settings
def get_scale_factor(current_width, current_height):
    width_scale = current_width / DEFAULT_WIDTH
    height_scale = current_height / DEFAULT_HEIGHT
    return min(width_scale, height_scale)

# Image loading function
def load_image(filename, scale=1.0, convert_alpha=True):
    """Load an image and return a pygame surface.
    
    Args:
        filename: Path to the image file relative to assets/images
        scale: Scale factor for the image (default 1.0)
        convert_alpha: Whether to convert the image for alpha transparency
    
    Returns:
        Pygame surface with the loaded image
    """
    # Check if assets directory exists
    base_path = "assets/images"
    if not os.path.exists(base_path):
        os.makedirs(base_path, exist_ok=True)
        
    try:
        full_path = os.path.join(base_path, filename)
        if not os.path.exists(full_path):
            # If file doesn't exist, create a placeholder surface
            print(f"Warning: Image {full_path} not found. Using placeholder.")
            surface = pygame.Surface((64, 64))
            surface.fill((255, 0, 255))  # Magenta for missing textures
            if convert_alpha:
                surface = surface.convert_alpha()
            return surface
            
        image = pygame.image.load(full_path)
        if convert_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
            
        # Scale if necessary
        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
            
        return image
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        # Return placeholder on error
        surface = pygame.Surface((64, 64))
        surface.fill((255, 0, 255))  # Magenta for missing textures
        if convert_alpha:
            surface = surface.convert_alpha()
        return surface 