import pygame
from settings import CAMERA_SPEED, WORLD_WIDTH_PIXELS

class Camera:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.offset_x = (WORLD_WIDTH_PIXELS - self.screen_width) // 2
        self.is_dragging = False
        self.drag_start_x = 0
        self.initial_offset_x = 0

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_dragging = True
                self.drag_start_x = pygame.mouse.get_pos()[0]
                self.initial_offset_x = self.offset_x
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_dragging = False
            if event.type == pygame.MOUSEMOTION and self.is_dragging:
                current_x = pygame.mouse.get_pos()[0]
                self.offset_x = self.initial_offset_x - (current_x - self.drag_start_x)
        
        self._clamp_offset()

    def update_keys(self, delta_time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.offset_x -= CAMERA_SPEED * delta_time
        if keys[pygame.K_d]:
            self.offset_x += CAMERA_SPEED * delta_time
        
        self._clamp_offset()
    
    def _clamp_offset(self):
        max_offset = WORLD_WIDTH_PIXELS - self.screen_width
        self.offset_x = max(0, min(self.offset_x, max_offset))