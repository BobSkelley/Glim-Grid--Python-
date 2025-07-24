import pygame
from settings import UI_TEXT_COLOR, GLIM_COST, WELLSPRING_COST, BEACON_COST, UI_BUTTON_COLOR, UI_BUTTON_HOVER_COLOR, HAMMER_ICON_PATH, UI_PANEL_COLOR, UI_BG_OVERLAY_COLOR

class FloatingText:
    def __init__(self, x, y, text, font):
        self.x = x
        self.y = y
        self.font = font
        self.text = text
        self.surface = self.font.render(self.text, True, UI_TEXT_COLOR)
        self.alpha = 255
        self.duration = 1.5
        self.timer = self.duration
        self.speed = 20

    def update(self, delta_time):
        self.timer -= delta_time
        self.y -= self.speed * delta_time
        self.alpha = max(0, 255 * (self.timer / self.duration))
        if self.timer <= 0: return False
        return True

    def draw(self, screen, camera_offset_x):
        self.surface.set_alpha(self.alpha)
        screen.blit(self.surface, (self.x - camera_offset_x, self.y))

class UI:
    def __init__(self, game_state, screen_width, screen_height):
        self.game_state = game_state
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font_large = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.font_tiny = pygame.font.SysFont("Arial", 12, bold=True)
        self.floating_texts = []
        
        self.glim_button_rect = pygame.Rect(0, 0, 180, 50)
        self.build_menu_button_rect = pygame.Rect(0, 0, 60, 60)
        self.build_panel_rect = pygame.Rect(0, 0, 450, 250)
        self.build_panel_rect.center = (screen_width / 2, screen_height / 2)
        
        self.well_button_rect = pygame.Rect(0, 0, 180, 50)
        self.beacon_button_rect = pygame.Rect(0, 0, 180, 50)
        
        self.build_menu_open = False
        self.notification_text = ""
        self.notification_timer = 0
        
        try:
            self.hammer_icon = pygame.image.load(HAMMER_ICON_PATH).convert_alpha()
            self.hammer_icon = pygame.transform.scale(self.hammer_icon, (40, 40))
        except pygame.error:
            self.hammer_icon = None

    def add_floating_text(self, x, y, text):
        self.floating_texts.append(FloatingText(x, y, text, self.font_large))

    def update(self, delta_time):
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(delta_time)]
        if self.notification_timer > 0:
            self.notification_timer -= delta_time

    def show_notification(self, text, duration=4):
        self.notification_text = text
        self.notification_timer = duration

    def handle_click(self, mouse_pos):
        if self.build_menu_open:
            if self.well_button_rect.collidepoint(mouse_pos): return "build_wellspring"
            if self.game_state.unlock_beacon and self.beacon_button_rect.collidepoint(mouse_pos):
                return "build_beacon"
            if not self.build_panel_rect.collidepoint(mouse_pos):
                self.build_menu_open = False
            return "ui_click"

        if self.glim_button_rect.collidepoint(mouse_pos): return "purchase_glim"
        if self.build_menu_button_rect.collidepoint(mouse_pos):
            self.build_menu_open = not self.build_menu_open
            return "ui_click"
        
        return None

    def draw(self, screen, camera_offset_x):
        essence_text = f"Life Essence: {self.game_state.life_essence}"
        text_surface = self.font_large.render(essence_text, True, UI_TEXT_COLOR)
        text_rect = text_surface.get_rect(topright=(self.screen_width - 15, 10))
        screen.blit(text_surface, text_rect)
        
        glim_count_text = f"Glims: {len(self.game_state.glims)}"
        glim_surf = self.font_large.render(glim_count_text, True, UI_TEXT_COLOR)
        glim_rect = glim_surf.get_rect(topright=(self.screen_width - 15, 40))
        screen.blit(glim_surf, glim_rect)

        self.glim_button_rect.bottomright = (self.screen_width - 15, self.screen_height - 15)
        self._draw_button(screen, self.glim_button_rect, "Purchase Glim", f"(Cost: {GLIM_COST})", "glim")

        self.build_menu_button_rect.midbottom = (self.screen_width / 2, self.screen_height - 15)
        self._draw_build_menu_button(screen)

        if self.build_menu_open: self._draw_build_panel(screen)
        
        if self.notification_timer > 0: self._draw_notification(screen)

        for ft in self.floating_texts: ft.draw(screen, camera_offset_x)

    def _draw_notification(self, screen):
        alpha = min(255, self.notification_timer * 255)
        text_surf = self.font_large.render(self.notification_text, True, UI_TEXT_COLOR)
        text_surf.set_alpha(alpha)
        screen.blit(text_surf, text_surf.get_rect(midbottom=(self.screen_width/2, self.screen_height - 100)))

    def _draw_build_panel(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(UI_BG_OVERLAY_COLOR)
        screen.blit(overlay, (0,0))

        pygame.draw.rect(screen, UI_PANEL_COLOR, self.build_panel_rect, border_radius=15)
        pygame.draw.rect(screen, UI_BUTTON_HOVER_COLOR, self.build_panel_rect, 3, 15)

        title_surf = self.font_large.render("Build Menu", True, UI_TEXT_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(self.build_panel_rect.centerx, self.build_panel_rect.top + 30)))

        self.well_button_rect.topleft = (self.build_panel_rect.left + 25, self.build_panel_rect.top + 70)
        self._draw_button(screen, self.well_button_rect, "Build Wellspring", f"(Cost: {WELLSPRING_COST})", "wellspring")
        
        if self.game_state.unlock_beacon:
            self.beacon_button_rect.topleft = (self.build_panel_rect.left + 225, self.build_panel_rect.top + 70)
            self._draw_button(screen, self.beacon_button_rect, "Build Beacon", f"(Cost: {BEACON_COST})", "beacon")

    def _draw_build_menu_button(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        hover = self.build_menu_button_rect.collidepoint(mouse_pos)
        color = UI_BUTTON_HOVER_COLOR if hover else UI_BUTTON_COLOR
        pygame.draw.rect(screen, color, self.build_menu_button_rect, border_radius=8)
        
        if self.hammer_icon:
            screen.blit(self.hammer_icon, self.hammer_icon.get_rect(center=self.build_menu_button_rect.center))
        else:
            pygame.draw.rect(screen, (40,40,50), self.build_menu_button_rect.inflate(-20, -20))

        key_text = self.font_tiny.render("1", True, UI_TEXT_COLOR)
        screen.blit(key_text, (self.build_menu_button_rect.left + 5, self.build_menu_button_rect.bottom - 15))

    def _draw_button(self, screen, rect, text_l1, text_l2, item_type):
        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos)
        is_disabled = not self.game_state.can_purchase(item_type)
        
        base_color = UI_BUTTON_HOVER_COLOR if hover and not is_disabled else UI_BUTTON_COLOR
        alpha = 128 if is_disabled else 255
        
        # Create a new, independent color object to modify its alpha
        final_color = pygame.Color(base_color)
        final_color.a = alpha

        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(button_surface, final_color, button_surface.get_rect(topleft=(0,0)), border_radius=5)
        
        text_surf_l1 = self.font_small.render(text_l1, True, UI_TEXT_COLOR)
        text_surf_l2 = self.font_small.render(text_l2, True, UI_TEXT_COLOR)
        text_surf_l1.set_alpha(alpha)
        text_surf_l2.set_alpha(alpha)

        button_surface.blit(text_surf_l1, text_surf_l1.get_rect(center=(rect.width / 2, rect.height / 2 - 10)))
        button_surface.blit(text_surf_l2, text_surf_l2.get_rect(center=(rect.width / 2, rect.height / 2 + 10)))
        screen.blit(button_surface, rect)