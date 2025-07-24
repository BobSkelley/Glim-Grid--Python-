import pygame
import random
import math
from settings import (GLIM_SPEED, GLIM_CULTIVATION_RATE, GLIM_CULTIVATION_STRENGTH, 
                      GLIM_MINING_STRENGTH, GLIM_COLOR_PALETTE, GLIM_EYE_COLOR, 
                      GLIM_PUPIL_COLOR, PI, STOMPER_LUNGE_DISTANCE, 
                      STOMPER_LUNGE_SPEED_MULTIPLIER, STOMPER_LUNGE_COOLDOWN)

class Glim:
    def __init__(self, x, y, glim_type='standard'):
        self.x = x
        self.y = y
        self.glim_type = glim_type
        
        # Generic attributes
        self.bob_timer = random.uniform(0, 2 * PI)
        self.color = random.choice(GLIM_COLOR_PALETTE)
        self.surface = self._create_surface()
        self.current_target_tile = None

        # State machine for actions
        self.state = 'idle' # idle, moving, cultivating, lunging, returning
        self.action_timer = 0
        
        # Stomper-specific attributes
        self.lunge_origin_pos = None

    def _create_surface(self):
        is_stomper = self.glim_type == 'stomper'
        size = (24, 24) if is_stomper else (16, 16)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        body_rect = (0, 6, size[0], size[1]-6) if is_stomper else (0, 4, 16, 12)
        eye_y = 10 if is_stomper else 7
        pupil_y = 12 if is_stomper else 9

        pygame.draw.rect(surface, self.color, body_rect, border_radius=5)
        
        pygame.draw.rect(surface, GLIM_EYE_COLOR, (size[0]*0.18, eye_y, size[0]*0.25, size[1]*0.3), border_radius=2)
        pygame.draw.rect(surface, GLIM_EYE_COLOR, (size[0]*0.56, eye_y, size[0]*0.25, size[1]*0.3), border_radius=2)
        pygame.draw.rect(surface, GLIM_PUPIL_COLOR, (size[0]*0.25, pupil_y, size[0]*0.125, size[1]*0.125))
        pygame.draw.rect(surface, GLIM_PUPIL_COLOR, (size[0]*0.625, pupil_y, size[0]*0.125, size[1]*0.125))
        return surface

    def convert_to_stomper(self):
        self.glim_type = 'stomper'
        self.surface = self._create_surface()
        self.state = 'idle' # Reset state on conversion

    def _move_towards(self, target_pos, speed, delta_time):
        dx, dy = target_pos[0] - self.x, target_pos[1] - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist < 2:
            return True # Arrived
        
        self.x += (dx / dist) * speed * delta_time
        self.y += (dy / dist) * speed * delta_time
        return False

    def update(self, delta_time, target_tile, speed_buff):
        self.bob_timer += delta_time * 10
        
        # If target changes, reset state
        if target_tile != self.current_target_tile:
            self.state = 'idle'
            if self.current_target_tile and self.current_target_tile.state == 'mountain':
                self.current_target_tile.is_being_mined = False
            self.current_target_tile = target_tile

        if not self.current_target_tile:
            self.state = 'idle'
            return 0, None

        # --- Standard Glim Logic ---
        if self.glim_type == 'standard':
            target_pos = (self.current_target_tile.rect.centerx, self.current_target_tile.rect.top - 8)
            arrived = self._move_towards(target_pos, GLIM_SPEED * speed_buff, delta_time)
            
            if arrived:
                self.action_timer += delta_time
                if self.action_timer >= GLIM_CULTIVATION_RATE:
                    self.action_timer = 0
                    essence = self.current_target_tile.take_damage(GLIM_CULTIVATION_STRENGTH)
                    if essence == "core_cultivated": return "core_cultivated", None
                    if essence > 0:
                        return essence, {'x': self.x, 'y': self.y, 'text': f"+{essence}"}
            return 0, None

        # --- Stomper Glim Logic (State Machine) ---
        elif self.glim_type == 'stomper':
            if self.current_target_tile.state != 'mountain':
                self.state = 'idle'
                return 0, None # Stompers only care about mountains

            # State: idle
            if self.state == 'idle':
                # Determine lunge origin based on which side of the mountain we are on
                if self.x < self.current_target_tile.rect.centerx:
                    self.lunge_origin_pos = (self.current_target_tile.rect.left - STOMPER_LUNGE_DISTANCE, self.current_target_tile.rect.centery)
                else:
                    self.lunge_origin_pos = (self.current_target_tile.rect.right + STOMPER_LUNGE_DISTANCE, self.current_target_tile.rect.centery)
                self.state = 'moving_to_origin'

            # State: moving_to_origin
            elif self.state == 'moving_to_origin':
                arrived = self._move_towards(self.lunge_origin_pos, GLIM_SPEED * speed_buff, delta_time)
                if arrived:
                    self.state = 'lunging'

            # State: lunging
            elif self.state == 'lunging':
                target_pos = (self.current_target_tile.rect.centerx, self.current_target_tile.rect.centery)
                lunge_speed = GLIM_SPEED * speed_buff * STOMPER_LUNGE_SPEED_MULTIPLIER
                arrived = self._move_towards(target_pos, lunge_speed, delta_time)
                
                if arrived:
                    self.current_target_tile.is_being_mined = True
                    result = self.current_target_tile.take_damage(GLIM_MINING_STRENGTH)
                    self.state = 'returning'
                    self.action_timer = STOMPER_LUNGE_COOLDOWN
                    effect = {'x': self.x, 'y': self.y, 'text': f"-{GLIM_MINING_STRENGTH}"}
                    if result == "mountain_cleared":
                        self.current_target_tile.is_being_mined = False
                        self.state = 'idle'
                        return 0, {'type': 'notification', 'text': 'Mountain Cleared!'}
                    return 0, effect

            # State: returning
            elif self.state == 'returning':
                 self.action_timer -= delta_time
                 arrived = self._move_towards(self.lunge_origin_pos, GLIM_SPEED * speed_buff, delta_time)
                 if arrived and self.action_timer <= 0:
                     self.state = 'lunging'
        
        return 0, None

    def draw(self, screen, camera_offset_x):
        is_stomper = self.glim_type == 'stomper'
        bob_offset = math.sin(self.bob_timer) * (4 if is_stomper else 2)
        
        # Don't bob while lunging for a more direct look
        if self.state == 'lunging':
            bob_offset = 0

        draw_rect = self.surface.get_rect(center=(self.x - camera_offset_x, self.y + bob_offset))
        screen.blit(self.surface, draw_rect)
