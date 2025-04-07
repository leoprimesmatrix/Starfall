import pygame
import pygame_gui
import random
from constants import *

class AbilitySelectionScreen:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.is_visible = False
        self.ability_buttons = []
        self.chosen_abilities = [] # Store the 3 abilities offered
        self.title_text = None
        self.title_rect = None
        self.overlay = None
        self.setup_ui()
        self.hide()

    def setup_ui(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        scale = get_scale_factor(screen_width, screen_height)
        was_visible = self.is_visible

        # Kill old buttons
        for button in self.ability_buttons:
            button.kill()
        self.ability_buttons = []

        # Title
        title_font_size = int(TITLE_FONT_SIZE * 0.8 * scale) # Slightly smaller title
        title_font = load_font(title_font_size)
        self.title_text = title_font.render("PICK AN ABILITY", True, YELLOW)
        self.title_rect = self.title_text.get_rect(centerx=screen_width//2, y=int(100*scale))

        # Choose 3 distinct random abilities
        available_abilities = list(ABILITIES.keys())
        self.chosen_abilities = random.sample(available_abilities, 3)

        # Button dimensions and positions
        button_width = int(BUTTON_WIDTH * 1.2 * scale)
        button_height = int(BUTTON_HEIGHT * 1.5 * scale) # Taller for description
        button_spacing = int(BUTTON_SPACING * scale)
        total_button_width = 3 * button_width + 2 * button_spacing
        start_x = (screen_width - total_button_width) // 2
        start_y = self.title_rect.bottom + int(80 * scale)

        # Create buttons for the 3 chosen abilities
        desc_font_size = int(18 * scale)
        desc_font = load_font(desc_font_size)

        for i, ability_id in enumerate(self.chosen_abilities):
            ability_data = ABILITIES[ability_id]
            x = start_x + i * (button_width + button_spacing)
            y = start_y
            # Use plain text without HTML tags
            button_text = f"{ability_data['name']}: {ability_data['description']}"
            
            # Create the exact object_id that matches theme.json
            object_id = f"#ability_button_{ability_id}"
            
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(x, y, button_width, button_height),
                text=button_text,
                manager=self.manager,
                object_id=object_id  # Use the exact ID that matches the theme
            )
            self.ability_buttons.append(button)

        # Overlay
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.fill(BLACK)
        self.overlay.set_alpha(200) # Darker overlay

        if was_visible:
            self.show()
        else:
            self.hide()

    def show(self):
        for button in self.ability_buttons:
            button.show()
        self.is_visible = True

    def hide(self):
        for button in self.ability_buttons:
            button.hide()
        self.is_visible = False

    def draw(self, surface):
        if not self.is_visible:
            return

        # Draw overlay
        if self.overlay:
            surface.blit(self.overlay, (0, 0))

        # Draw title
        if self.title_text:
            surface.blit(self.title_text, self.title_rect)

    def handle_event(self, event, game_state, player):
        if not self.is_visible:
            return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for i, button in enumerate(self.ability_buttons):
                if event.ui_element == button:
                    selected_ability_id = self.chosen_abilities[i]
                    player.activate_ability(selected_ability_id)
                    game_state.reset_ability_counter()
                    game_state.change_state(STATE_PLAYING)
                    self.hide() # Hide self after selection
                    return True # Event handled

        # Optional: Add keyboard selection (1, 2, 3)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and len(self.chosen_abilities) > 0:
                player.activate_ability(self.chosen_abilities[0])
                game_state.reset_ability_counter()
                game_state.change_state(STATE_PLAYING)
                self.hide()
                return True
            elif event.key == pygame.K_2 and len(self.chosen_abilities) > 1:
                player.activate_ability(self.chosen_abilities[1])
                game_state.reset_ability_counter()
                game_state.change_state(STATE_PLAYING)
                self.hide()
                return True
            elif event.key == pygame.K_3 and len(self.chosen_abilities) > 2:
                player.activate_ability(self.chosen_abilities[2])
                game_state.reset_ability_counter()
                game_state.change_state(STATE_PLAYING)
                self.hide()
                return True

        return True # Keep processing other events if needed 