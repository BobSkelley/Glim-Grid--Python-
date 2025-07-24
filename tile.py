import pygame
import random
import math
from settings import TILE_SIZE, DIRT_BROWN, GRASS_GREEN, DARK_GRASS_GREEN, WHITE, GRID_LINE_COLOR, TILE_TEXT_COLOR, PASSIVE_INCOME_AMOUNT, PASSIVE_INCOME_INTERVAL, LANDMARK_COLOR_PRIMARY, LANDMARK_COLOR_SECONDARY, MOUNTAIN_COLOR_DARK, MOUNTAIN_COLOR_LIGHT, CORE_TILE_COLOR

class Tile:
    def __init__(self, x_pos, y_pos, toughness, state='barren', is_center=False, is_core=False):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.max_toughness = toughness
        self.current_toughness = toughness
        self.state = state
        self.is_center = is_center
        self.is_core = is_core
        self.rect = pygame.Rect(self.x_pos, self.y_pos, TILE_SIZE, TILE_SIZE)
        self.structure = None
        
        self.living_surface = self._create_living_surface()
        self.landmark_surface = self._create_landmark_surface() if is_center else None
        self.mountain_surface = self._create_mountain_surface() if state == 'mountain' else None

        self.font = pygame.font.SysFont("Arial", 14)
        self.passive_timer = 0
        self.pulse_timer = 0

    def _create_living_surface(self):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surface.fill(DIRT_BROWN)
        pygame.draw.rect(surface, GRASS_GREEN, (0, 0, TILE_SIZE, TILE_SIZE // 3))
        for i in range(TILE_SIZE // 4):
            x = (i * 13) % TILE_SIZE
            y = (i * 7) % (TILE_SIZE // 3)
            pygame.draw.rect(surface, DARK_GRASS_GREEN, (x, y, 2, 2))
        return surface
    
    def _create_mountain_surface(self):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE * 4), pygame.SRCALPHA)
        height = random.randint(int(TILE_SIZE * 1.5), TILE_SIZE * 4)
        points = [
            (0, TILE_SIZE * 4),
            (0, random.randint(height // 2, height)),
            (TILE_SIZE // 2, random.randint(0, height // 3)),
            (TILE_SIZE, random.randint(height // 2, height)),
            (TILE_SIZE, TILE_SIZE * 4)
        ]
        pygame.draw.polygon(surface, MOUNTAIN_COLOR_DARK, points)
        pygame.draw.polygon(surface, MOUNTAIN_COLOR_LIGHT, points, 2)
        return surface

    def _create_landmark_surface(self):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE * 2), pygame.SRCALPHA)
        points = [(TILE_SIZE // 2, 0), (TILE_SIZE - 4, TILE_SIZE), (4, TILE_SIZE)]
        pygame.draw.polygon(surface, LANDMARK_COLOR_PRIMARY, points)
        pygame.draw.polygon(surface, LANDMARK_COLOR_SECONDARY, points, 3)
        return surface

    def set_structure(self, structure):
        self.structure = structure

    def is_buildable(self):
        return self.state == 'living' and not self.is_center and self.structure is None

    def take_damage(self, amount):
        if self.state == 'barren':
            self.current_toughness -= amount
            if self.current_toughness <= 0:
                self.current_toughness = 0
                self.state = 'living'
                if self.is_core:
                    return "core_cultivated"
            return amount
        return 0
    
    def update(self, delta_time):
        if self.is_core and self.state == 'barren':
            self.pulse_timer += delta_time * 5

        if self.state == 'living' and not self.is_center and self.structure is None:
            self.passive_timer += delta_time
            if self.passive_timer >= PASSIVE_INCOME_INTERVAL:
                self.passive_timer -= PASSIVE_INCOME_INTERVAL
                return PASSIVE_INCOME_AMOUNT
        return 0

    def draw(self, screen, camera_offset_x):
        on_screen_rect = self.rect.copy()
        on_screen_rect.x -= camera_offset_x

        if self.state == 'barren':
            color = WHITE
            if self.is_core:
                pulse = (math.sin(self.pulse_timer) + 1) / 2
                color = WHITE.lerp(CORE_TILE_COLOR, pulse)
            pygame.draw.rect(screen, color, on_screen_rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, on_screen_rect, 1)
            
            if self.current_toughness > 0:
                text_surf = self.font.render(str(self.current_toughness), True, TILE_TEXT_COLOR)
                text_rect = text_surf.get_rect(center=on_screen_rect.center)
                screen.blit(text_surf, text_rect)
        elif self.state == 'mountain':
            if self.mountain_surface:
                mountain_rect = self.mountain_surface.get_rect(bottomleft=on_screen_rect.bottomleft)
                screen.blit(self.mountain_surface, mountain_rect)
        else: # living
            screen.blit(self.living_surface, on_screen_rect)
            if self.is_center and self.landmark_surface:
                landmark_rect = self.landmark_surface.get_rect(midbottom=on_screen_rect.midtop)
                screen.blit(self.landmark_surface, landmark_rect)