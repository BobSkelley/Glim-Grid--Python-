import pygame
from settings import (WELLSPRING_INCOME_AMOUNT, WELLSPRING_INCOME_INTERVAL, 
                      WELLSPRING_COLOR_PRIMARY, WELLSPRING_COLOR_SECONDARY, TILE_SIZE, 
                      BEACON_COLOR_PRIMARY, BEACON_COLOR_SECONDARY,
                      STOMPER_POST_COLOR_PRIMARY, STOMPER_POST_COLOR_SECONDARY,
                      STOMPER_TRAINING_TIME, STOMPER_POST_CAPACITY, UI_TEXT_COLOR)

class Structure:
    def __init__(self, tile):
        self.tile = tile
        self.tile.set_structure(self)
        self.rect = tile.rect.copy()
        self.name = self.__class__.__name__.lower()
    
    def update(self, delta_time):
        return 0, None
    
    def draw(self, screen, camera_offset_x):
        on_screen_rect = self.rect.copy()
        on_screen_rect.x -= camera_offset_x
        screen.blit(self.surface, on_screen_rect)

class Wellspring(Structure):
    def __init__(self, tile):
        super().__init__(tile)
        self.passive_timer = 0
        self.surface = self._create_surface()

    def _create_surface(self):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surface, WELLSPRING_COLOR_PRIMARY, (8, 12, 16, 20), border_radius=3)
        pygame.draw.rect(surface, WELLSPRING_COLOR_SECONDARY, (4, 8, 24, 4), border_radius=2)
        pygame.draw.circle(surface, WELLSPRING_COLOR_SECONDARY, (16, 18), 5)
        return surface

    @staticmethod
    def get_preview_surface():
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surface, WELLSPRING_COLOR_PRIMARY, (8, 12, 16, 20), border_radius=3)
        pygame.draw.rect(surface, WELLSPRING_COLOR_SECONDARY, (4, 8, 24, 4), border_radius=2)
        pygame.draw.circle(surface, WELLSPRING_COLOR_SECONDARY, (16, 18), 5)
        return surface
    
    def update(self, delta_time):
        self.passive_timer += delta_time
        if self.passive_timer >= WELLSPRING_INCOME_INTERVAL:
            self.passive_timer -= WELLSPRING_INCOME_INTERVAL
            return WELLSPRING_INCOME_AMOUNT, {'x': self.rect.centerx, 'y': self.rect.y, 'text': f"+{WELLSPRING_INCOME_AMOUNT}"}
        return 0, None

class Beacon(Structure):
    def __init__(self, tile):
        super().__init__(tile)
        self.surface = self._create_surface()
    
    def _create_surface(self):
        surface = pygame.Surface((TILE_SIZE, int(TILE_SIZE * 1.5)), pygame.SRCALPHA)
        pygame.draw.rect(surface, BEACON_COLOR_PRIMARY, (12, 12, 8, TILE_SIZE * 2))
        pygame.draw.circle(surface, BEACON_COLOR_SECONDARY, (16, 8), 8)
        return surface
    
    @staticmethod
    def get_preview_surface():
        surface = pygame.Surface((TILE_SIZE, int(TILE_SIZE * 1.5)), pygame.SRCALPHA)
        pygame.draw.rect(surface, BEACON_COLOR_PRIMARY, (12, 12, 8, TILE_SIZE * 2))
        pygame.draw.circle(surface, BEACON_COLOR_SECONDARY, (16, 8), 8)
        return surface

    def draw(self, screen, camera_offset_x):
        on_screen_rect = self.surface.get_rect(midbottom=self.tile.rect.midtop)
        on_screen_rect.x -= camera_offset_x
        screen.blit(self.surface, on_screen_rect)

class StomperTrainingPost(Structure):
    def __init__(self, tile):
        super().__init__(tile)
        self.surface = self._create_surface()
        self.is_training = False
        self.training_timer = 0.0
        self.glim_to_train = None
        self.trained_count = 0
        self.capacity = STOMPER_POST_CAPACITY
        self.font = pygame.font.SysFont("Arial", 12, bold=True)

    def _create_surface(self):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surface, STOMPER_POST_COLOR_PRIMARY, (2, 10, 28, 22), border_radius=4)
        pygame.draw.rect(surface, STOMPER_POST_COLOR_SECONDARY, (8, 4, 16, 6))
        pygame.draw.rect(surface, (0,0,0), (12, 16, 8, 8)) # Anvil-like shape
        return surface

    @staticmethod
    def get_preview_surface():
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surface, STOMPER_POST_COLOR_PRIMARY, (2, 10, 28, 22), border_radius=4)
        pygame.draw.rect(surface, STOMPER_POST_COLOR_SECONDARY, (8, 4, 16, 6))
        pygame.draw.rect(surface, (0,0,0), (12, 16, 8, 8))
        return surface

    def start_training(self, glim):
        if not self.is_training and self.trained_count < self.capacity:
            self.is_training = True
            self.glim_to_train = glim
            self.training_timer = STOMPER_TRAINING_TIME
            return True
        return False

    def update(self, delta_time):
        if self.is_training:
            self.training_timer -= delta_time
            if self.training_timer <= 0:
                if self.glim_to_train:
                    self.glim_to_train.convert_to_stomper()
                    self.trained_count += 1
                self.is_training = False
                self.glim_to_train = None
                # Return a special message to be caught by main loop
                return 0, {'type': 'notification', 'text': 'Stomper training complete!'}
        return 0, None

    def draw(self, screen, camera_offset_x):
        super().draw(screen, camera_offset_x)
        on_screen_rect = self.rect.copy()
        on_screen_rect.x -= camera_offset_x
        
        # Draw training progress bar
        if self.is_training:
            progress = 1 - (self.training_timer / STOMPER_TRAINING_TIME)
            bar_width = int(progress * self.rect.width)
            progress_rect = pygame.Rect(on_screen_rect.left, on_screen_rect.bottom - 5, bar_width, 5)
            pygame.draw.rect(screen, (255, 255, 0), progress_rect)

        # Draw capacity counter
        count_text = f"{self.trained_count}/{self.capacity}"
        text_surf = self.font.render(count_text, True, UI_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(on_screen_rect.centerx, on_screen_rect.top - 8))
        screen.blit(text_surf, text_rect)
