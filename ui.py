import pygame
from settings import (UI_TEXT_COLOR, GLIM_COST, WELLSPRING_COST, BEACON_COST, 
                      STOMPER_POST_COST, STOMPER_CONVERSION_COST,
                      UI_BUTTON_COLOR, UI_BUTTON_HOVER_COLOR, HAMMER_ICON_PATH, 
                      UI_PANEL_COLOR, UI_BG_OVERLAY_COLOR, SKILL_ICON_PATH, MOTION_SKILL_ICON_PATH)

class FloatingText:
    def __init__(self, x, y, text, font, duration=1.5, speed=20, color=UI_TEXT_COLOR):
        self.x = x
        self.y = y
        self.font = font
        self.text = text
        self.color = color
        self.surface = self.font.render(self.text, True, self.color)
        self.alpha = 255
        self.duration = duration
        self.timer = self.duration
        self.speed = speed

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
        self.font_medium = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.font_tiny = pygame.font.SysFont("Arial", 12, bold=True)
        self.floating_texts = []
        
        self.glim_button_rect = pygame.Rect(0, 0, 180, 50)
        self.build_menu_button_rect = pygame.Rect(0, 0, 60, 60)
        self.skill_tree_button_rect = pygame.Rect(0, 0, 60, 60)
        
        self.build_panel_rect = pygame.Rect(0, 0, 450, 250)
        self.build_panel_rect.center = (screen_width / 2, screen_height / 2)
        self.skill_panel_rect = pygame.Rect(0, 0, 450, 350)
        self.skill_panel_rect.center = (screen_width / 2, screen_height / 2)

        self.well_button_rect = pygame.Rect(0, 0, 180, 50)
        self.beacon_button_rect = pygame.Rect(0, 0, 180, 50)
        self.stomper_post_button_rect = pygame.Rect(0, 0, 180, 50)
        
        self.motion_skill_rect = pygame.Rect(0, 0, 80, 80)
        self.drills_skill_rect = pygame.Rect(0, 0, 80, 80)

        self.build_menu_open = False
        self.skill_tree_open = False
        
        try:
            self.hammer_icon = pygame.image.load(HAMMER_ICON_PATH).convert_alpha()
            self.hammer_icon = pygame.transform.scale(self.hammer_icon, (40, 40))
        except pygame.error: self.hammer_icon = None
        try:
            self.skill_icon = pygame.image.load(SKILL_ICON_PATH).convert_alpha()
            self.skill_icon = pygame.transform.scale(self.skill_icon, (40, 40))
        except pygame.error: self.skill_icon = None
        # FIX: Added try-except block to prevent crash if file is missing
        try:
            self.motion_skill_icon = pygame.image.load(MOTION_SKILL_ICON_PATH).convert_alpha()
            self.motion_skill_icon = pygame.transform.scale(self.motion_skill_icon, (40, 40))
        except pygame.error: self.motion_skill_icon = None

    def add_floating_text(self, x, y, text, duration=1.5):
        self.floating_texts.append(FloatingText(x, y, text, self.font_large, duration=duration))

    def update(self, delta_time):
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(delta_time)]

    def show_notification(self, text, duration=4):
        self.add_floating_text(self.screen_width / 2, self.screen_height - 100, text, duration=duration)

    def handle_click(self, mouse_pos):
        if self.build_menu_open:
            if self.well_button_rect.collidepoint(mouse_pos): return "build_wellspring"
            if self.beacon_button_rect.collidepoint(mouse_pos): return "build_beacon"
            if self.game_state.skills['glimdraulic_drills']['unlocked'] and self.stomper_post_button_rect.collidepoint(mouse_pos):
                return "build_stomper_post"
            if not self.build_panel_rect.collidepoint(mouse_pos): self.build_menu_open = False
            return "ui_click"

        if self.skill_tree_open:
            if self.motion_skill_rect.collidepoint(mouse_pos):
                return "purchase_glimversal_motion"
            if self.drills_skill_rect.collidepoint(mouse_pos):
                return "purchase_glimdraulic_drills"
            if not self.skill_panel_rect.collidepoint(mouse_pos): self.skill_tree_open = False
            return "ui_click"

        if self.glim_button_rect.collidepoint(mouse_pos): return "purchase_glim"
        if self.build_menu_button_rect.collidepoint(mouse_pos):
            self.build_menu_open = not self.build_menu_open
            self.skill_tree_open = False
            return "ui_click"
        if self.game_state.skill_tree_unlocked and self.skill_tree_button_rect.collidepoint(mouse_pos):
            self.skill_tree_open = not self.skill_tree_open
            self.build_menu_open = False
            return "ui_click"
        
        return None

    def draw(self, screen, camera_offset_x):
        mouse_pos = pygame.mouse.get_pos()
        essence_text = f"Life Essence: {self.game_state.life_essence}"
        text_surface = self.font_large.render(essence_text, True, UI_TEXT_COLOR)
        screen.blit(text_surface, text_surface.get_rect(topright=(self.screen_width - 15, 10)))
        
        glim_count_text = f"Glims: {len(self.game_state.glims)}/{self.game_state.glim_cap}"
        glim_surf = self.font_large.render(glim_count_text, True, UI_TEXT_COLOR)
        screen.blit(glim_surf, glim_surf.get_rect(topright=(self.screen_width - 15, 40)))

        if self.game_state.skill_tree_unlocked:
            sp_text = f"Skill Points: {self.game_state.skill_points}"
            sp_surf = self.font_large.render(sp_text, True, UI_TEXT_COLOR)
            screen.blit(sp_surf, sp_surf.get_rect(topright=(self.screen_width - 15, 70)))

        self.glim_button_rect.bottomright = (self.screen_width - 15, self.screen_height - 15)
        self._draw_button(screen, self.glim_button_rect, "Purchase Glim", f"(Cost: {GLIM_COST})", "glim")

        self.build_menu_button_rect.midbottom = (self.screen_width / 2, self.screen_height - 15)
        self._draw_build_menu_button(screen)
        
        if self.game_state.skill_tree_unlocked:
            self.skill_tree_button_rect.bottomleft = (self.build_menu_button_rect.right + 10, self.screen_height - 15)
            self._draw_skill_tree_button(screen)

        if self.build_menu_open: self._draw_build_panel(screen, mouse_pos)
        if self.skill_tree_open: self._draw_skill_tree_panel(screen, mouse_pos)

        for ft in self.floating_texts: ft.draw(screen, camera_offset_x)

    def _draw_build_panel(self, screen, mouse_pos):
        self._draw_panel_background(screen)
        pygame.draw.rect(screen, UI_PANEL_COLOR, self.build_panel_rect, border_radius=15)
        pygame.draw.rect(screen, UI_BUTTON_HOVER_COLOR, self.build_panel_rect, 3, 15)
        
        title_surf = self.font_large.render("Build Menu", True, UI_TEXT_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(self.build_panel_rect.centerx, self.build_panel_rect.top + 30)))

        self.well_button_rect.topleft = (self.build_panel_rect.left + 25, self.build_panel_rect.top + 70)
        self.beacon_button_rect.topleft = (self.build_panel_rect.left + 225, self.build_panel_rect.top + 70)
        self.stomper_post_button_rect.topleft = (self.build_panel_rect.left + 25, self.build_panel_rect.top + 140)

        self._draw_button(screen, self.well_button_rect, "Build Wellspring", f"(Cost: {WELLSPRING_COST})", "wellspring")
        if self.well_button_rect.collidepoint(mouse_pos):
            self._draw_info_tooltip(screen, mouse_pos, ["Creates Life Essence over time."])

        self._draw_button(screen, self.beacon_button_rect, "Build Beacon", f"(Cost: {BEACON_COST})", "beacon")
        if self.beacon_button_rect.collidepoint(mouse_pos):
            self._draw_info_tooltip(screen, mouse_pos, ["Boosts speed of nearby Glims."])
        
        if self.game_state.skills['glimdraulic_drills']['unlocked']:
            self._draw_button(screen, self.stomper_post_button_rect, "Stomper Post", f"(Cost: {STOMPER_POST_COST})", "stompertrainingpost")
            if self.stomper_post_button_rect.collidepoint(mouse_pos):
                self._draw_info_tooltip(screen, mouse_pos, ["Automatically trains Glims into Stompers.", "Click the built post to pause/resume."])
                
    def _draw_skill_tree_panel(self, screen, mouse_pos):
        self._draw_panel_background(screen)
        pygame.draw.rect(screen, UI_PANEL_COLOR, self.skill_panel_rect, border_radius=15)
        pygame.draw.rect(screen, UI_BUTTON_HOVER_COLOR, self.skill_panel_rect, 3, 15)

        title_surf = self.font_large.render("Skill Tree", True, UI_TEXT_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(self.skill_panel_rect.centerx, self.skill_panel_rect.top + 30)))
        
        self.motion_skill_rect.center = (self.skill_panel_rect.centerx, self.skill_panel_rect.top + 120)
        self.drills_skill_rect.center = (self.skill_panel_rect.centerx, self.motion_skill_rect.bottom + 60)
        
        motion_unlocked = self.game_state.skills['glimversal_motion']['unlocked']
        if motion_unlocked:
            pygame.draw.line(screen, UI_BUTTON_HOVER_COLOR, self.motion_skill_rect.midbottom, self.drills_skill_rect.midtop, 3)

        self._draw_skill_button(screen, mouse_pos, 'glimversal_motion', self.motion_skill_rect, self.motion_skill_icon,
                                ["Glimversal Motion", "Allows Glims to cultivate tiles", "to the left and right."])

        if motion_unlocked:
             self._draw_skill_button(screen, mouse_pos, 'glimdraulic_drills', self.drills_skill_rect, self.skill_icon,
                                ["Glimdraulic Drills", "Unlocks Stomper Glims & Training Post.", "Grants 5 free Stomper Glims."])

    def _draw_skill_button(self, screen, mouse_pos, skill_name, rect, icon, tooltip_lines):
        skill = self.game_state.skills[skill_name]
        is_unlocked = skill['unlocked']
        can_buy = self.game_state.can_purchase_skill(skill_name)
        
        color = (50, 150, 50) if is_unlocked else (UI_BUTTON_HOVER_COLOR if can_buy else UI_BUTTON_COLOR)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        
        if icon:
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)
        
        if rect.collidepoint(mouse_pos):
            lines = list(tooltip_lines)
            if not is_unlocked:
                req_glims_str = f"Requires: {skill['req_glims']} Standard Glims"
                lines.extend([
                    f"Cost: {skill['cost_essence']} LE, {skill['cost_sp']} SP",
                    req_glims_str
                ])
            self._draw_info_tooltip(screen, mouse_pos, lines)

    def _draw_info_tooltip(self, screen, mouse_pos, lines):
        if not lines: return
        
        surfaces = [self.font_small.render(line, True, UI_TEXT_COLOR) for line in lines]
        max_width = max(s.get_width() for s in surfaces)
        total_height = sum(s.get_height() for s in surfaces) + (len(surfaces) - 1) * 5
        
        tooltip_rect = pygame.Rect(0, 0, max_width + 20, total_height + 20)
        
        if mouse_pos[0] + tooltip_rect.width > self.screen_width:
            tooltip_rect.topright = (mouse_pos[0] - 15, mouse_pos[1] + 15)
        else:
            tooltip_rect.topleft = (mouse_pos[0] + 15, mouse_pos[1] + 15)

        pygame.draw.rect(screen, UI_PANEL_COLOR, tooltip_rect, border_radius=5)
        pygame.draw.rect(screen, UI_BUTTON_HOVER_COLOR, tooltip_rect, 2, 5)

        current_y = tooltip_rect.top + 10
        for surface in surfaces:
            screen.blit(surface, (tooltip_rect.left + 10, current_y))
            current_y += surface.get_height() + 5

    def _draw_panel_background(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(UI_BG_OVERLAY_COLOR)
        screen.blit(overlay, (0,0))
    
    def _draw_skill_tree_button(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        hover = self.skill_tree_button_rect.collidepoint(mouse_pos)
        color = UI_BUTTON_HOVER_COLOR if hover else UI_BUTTON_COLOR
        pygame.draw.rect(screen, color, self.skill_tree_button_rect, border_radius=8)
        
        key_text = self.font_tiny.render("2", True, UI_TEXT_COLOR)
        screen.blit(key_text, (self.skill_tree_button_rect.left + 5, self.skill_tree_button_rect.bottom - 15))

    def _draw_build_menu_button(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        hover = self.build_menu_button_rect.collidepoint(mouse_pos)
        color = UI_BUTTON_HOVER_COLOR if hover else UI_BUTTON_COLOR
        pygame.draw.rect(screen, color, self.build_menu_button_rect, border_radius=8)
        
        if self.hammer_icon:
            screen.blit(self.hammer_icon, self.hammer_icon.get_rect(center=self.build_menu_button_rect.center))
        
        key_text = self.font_tiny.render("1", True, UI_TEXT_COLOR)
        screen.blit(key_text, (self.build_menu_button_rect.left + 5, self.build_menu_button_rect.bottom - 15))

    def _draw_button(self, screen, rect, text_l1, text_l2, item_type):
        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos)
        is_disabled = not self.game_state.can_purchase(item_type)
        
        base_color = UI_BUTTON_HOVER_COLOR if hover and not is_disabled else UI_BUTTON_COLOR
        alpha = 128 if is_disabled else 255
        
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
