import pygame
from settings import (WELLSPRING_INCOME_AMOUNT, WELLSPRING_INCOME_INTERVAL, 
                      WELLSPRING_COLOR_PRIMARY, WELLSPRING_COLOR_SECONDARY, TILE_SIZE, 
                      BEACON_COLOR_PRIMARY, BEACON_COLOR_SECONDARY,
                      STOMPER_POST_COLOR_PRIMARY, STOMPER_POST_COLOR_SECONDARY)

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
