import pygame
import random
import math
from settings import GLIM_SPEED, GLIM_CULTIVATION_RATE, GLIM_CULTIVATION_STRENGTH, GLIM_COLOR_PALETTE, GLIM_EYE_COLOR, GLIM_PUPIL_COLOR, PI

class Glim:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cultivation_timer = 0
        self.bob_timer = random.uniform(0, 2 * PI)
        self.color = random.choice(GLIM_COLOR_PALETTE)
        self.surface = self._create_surface()

    def _create_surface(self):
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.color, (0, 4, 16, 12), border_radius=4)
        pygame.draw.rect(surface, GLIM_EYE_COLOR, (3, 7, 4, 5), border_radius=2)
        pygame.draw.rect(surface, GLIM_EYE_COLOR, (9, 7, 4, 5), border_radius=2)
        pygame.draw.rect(surface, GLIM_PUPIL_COLOR, (4, 9, 2, 2))
        pygame.draw.rect(surface, GLIM_PUPIL_COLOR, (10, 9, 2, 2))
        return surface

    def update(self, delta_time, target_tile, speed_buff):
        if target_tile is None:
            return 0, None
        
        current_speed = GLIM_SPEED * speed_buff
        target_x, target_y = target_tile.rect.centerx, target_tile.rect.top - 8
        dx, dy = target_x - self.x, target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        self.bob_timer += delta_time * 10

        if dist < 5:
            self.cultivation_timer += delta_time
            if self.cultivation_timer >= GLIM_CULTIVATION_RATE:
                self.cultivation_timer -= GLIM_CULTIVATION_RATE
                essence = target_tile.take_damage(GLIM_CULTIVATION_STRENGTH)
                if essence == "core_cultivated":
                    return "core_cultivated", None
                
                effect = {'x': self.x, 'y': self.y, 'text': f"+{essence}"}
                return essence, effect
        else:
            self.x += (dx / dist) * current_speed * delta_time
            self.y += (dy / dist) * current_speed * delta_time
            
        return 0, None

    def draw(self, screen, camera_offset_x):
        bob_offset = math.sin(self.bob_timer) * 2
        draw_rect = self.surface.get_rect(center=(self.x - camera_offset_x, self.y + bob_offset))
        screen.blit(self.surface, draw_rect)