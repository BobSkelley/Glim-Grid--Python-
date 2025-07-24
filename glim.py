import pygame
import random
import math
from settings import GLIM_SPEED, GLIM_CULTIVATION_RATE, GLIM_CULTIVATION_STRENGTH, GLIM_MINING_STRENGTH, GLIM_COLOR_PALETTE, GLIM_EYE_COLOR, GLIM_PUPIL_COLOR, PI

class Glim:
    def __init__(self, x, y, glim_type='standard'):
        self.x = x
        self.y = y
        self.cultivation_timer = 0
        self.bob_timer = random.uniform(0, 2 * PI)
        self.color = random.choice(GLIM_COLOR_PALETTE)
        self.glim_type = glim_type
        self.surface = self._create_surface()

    def _create_surface(self):
        is_stomper = self.glim_type == 'stomper'
        size = (24, 24) if is_stomper else (16, 16)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        body_rect = (0, 6, size[0], size[1]-6) if is_stomper else (0, 4, 16, 12)
        eye_y = 10 if is_stomper else 7
        pupil_y = 12 if is_stomper else 9

        pygame.draw.rect(surface, self.color, body_rect, border_radius=5)
        
        # Eyes
        pygame.draw.rect(surface, GLIM_EYE_COLOR, (size[0]*0.18, eye_y, size[0]*0.25, size[1]*0.3), border_radius=2)
        pygame.draw.rect(surface, GLIM_EYE_COLOR, (size[0]*0.56, eye_y, size[0]*0.25, size[1]*0.3), border_radius=2)
        # Pupils
        pygame.draw.rect(surface, GLIM_PUPIL_COLOR, (size[0]*0.25, pupil_y, size[0]*0.125, size[1]*0.125))
        pygame.draw.rect(surface, GLIM_PUPIL_COLOR, (size[0]*0.625, pupil_y, size[0]*0.125, size[1]*0.125))
        return surface

    def convert_to_stomper(self):
        self.glim_type = 'stomper'
        self.surface = self._create_surface()

    def update(self, delta_time, target_tile, speed_buff):
        if target_tile is None:
            return 0, None

        is_stomper = self.glim_type == 'stomper'
        current_speed = GLIM_SPEED * speed_buff
        target_y_offset = 12 if is_stomper else 8
        target_x, target_y = target_tile.rect.centerx, target_tile.rect.top - target_y_offset
        
        dx, dy = target_x - self.x, target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        self.bob_timer += delta_time * 10

        if dist < 5:
            self.cultivation_timer += delta_time
            if self.cultivation_timer >= GLIM_CULTIVATION_RATE:
                self.cultivation_timer -= GLIM_CULTIVATION_RATE
                
                if target_tile.state == 'mountain' and is_stomper:
                    damage = GLIM_MINING_STRENGTH
                    essence_gained = target_tile.take_damage(damage)
                    effect = {'x': self.x, 'y': self.y, 'text': f"-{damage}"}
                    return 0, effect 
                elif target_tile.state == 'barren' and not is_stomper:
                    essence = target_tile.take_damage(GLIM_CULTIVATION_STRENGTH)
                    if essence == "core_cultivated":
                        return "core_cultivated", None
                    if essence > 0:
                        effect = {'x': self.x, 'y': self.y, 'text': f"+{essence}"}
                        return essence, effect
        else:
            if dist > 0:
                self.x += (dx / dist) * current_speed * delta_time
                self.y += (dy / dist) * current_speed * delta_time
            
        return 0, None

    def draw(self, screen, camera_offset_x):
        is_stomper = self.glim_type == 'stomper'
        bob_offset = math.sin(self.bob_timer) * (4 if is_stomper else 2)
        draw_rect = self.surface.get_rect(center=(self.x - camera_offset_x, self.y + bob_offset))
        screen.blit(self.surface, draw_rect)
