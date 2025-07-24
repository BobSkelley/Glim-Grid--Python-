import pygame
from settings import SKY_COLOR, PLAYER_CLICK_STRENGTH, BUILD_VALID_COLOR, BUILD_INVALID_COLOR, TILE_SIZE
from grid import Grid
from camera import Camera
from game_state import GameState
from ui import UI
from structure import Wellspring, Beacon, StomperTrainingPost

def main():
    pygame.init()
    pygame.font.init()
    
    print("[DEBUG] Pygame initialized.")

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Glim Grid")
    clock = pygame.time.Clock()
    
    print(f"[DEBUG] Screen created with size: {screen_width}x{screen_height}")

    game_state = GameState()
    ui = UI(game_state, screen_width, screen_height)
    grid = Grid(screen_height)
    camera = Camera(screen_width)
    build_preview_surface = None

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        world_x, world_y = mouse_pos[0] + camera.offset_x, mouse_pos[1]

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state.build_mode_item:
                        game_state.build_mode_item = None
                        pygame.mouse.set_visible(True)
                    elif ui.build_menu_open: ui.build_menu_open = False
                    elif ui.skill_tree_open: ui.skill_tree_open = False
                    else: running = False
                if event.key == pygame.K_1:
                    ui.build_menu_open = not ui.build_menu_open
                    ui.skill_tree_open = False
                if event.key == pygame.K_2:
                    if game_state.skill_tree_unlocked:
                        ui.skill_tree_open = not ui.skill_tree_open
                        ui.build_menu_open = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    action = ui.handle_click(mouse_pos)
                    
                    if action == "purchase_glim":
                        game_state.purchase_glim(*grid.center_tile_pos)
                    elif action == "build_wellspring":
                        if game_state.can_purchase("wellspring"):
                            game_state.build_mode_item = "wellspring"
                            build_preview_surface = Wellspring.get_preview_surface()
                            ui.build_menu_open = False
                            pygame.mouse.set_visible(False)
                    elif action == "build_beacon":
                        if game_state.can_purchase("beacon"):
                            game_state.build_mode_item = "beacon"
                            build_preview_surface = Beacon.get_preview_surface()
                            ui.build_menu_open = False
                            pygame.mouse.set_visible(False)
                    elif action == "build_stomper_post":
                        if game_state.can_purchase("stompertrainingpost"):
                            game_state.build_mode_item = "stomper_post"
                            build_preview_surface = StomperTrainingPost.get_preview_surface()
                            ui.build_menu_open = False
                            pygame.mouse.set_visible(False)
                    elif action == "purchase_glimversal_motion":
                        if game_state.purchase_skill('glimversal_motion', grid.center_tile_pos):
                            ui.show_notification("Glimversal Motion unlocked!")
                    elif action == "purchase_glimdraulic_drills":
                        if game_state.purchase_skill('glimdraulic_drills', grid.center_tile_pos):
                            ui.show_notification("Glimdraulic Drills unlocked!")
                    
                    elif action is None: # World click
                        if game_state.build_mode_item:
                            tile_to_build_on = grid.get_tile_at_world_pos(world_x, world_y)
                            if tile_to_build_on and tile_to_build_on.is_buildable():
                                structure_map = {
                                    "wellspring": Wellspring,
                                    "beacon": Beacon,
                                    "stomper_post": StomperTrainingPost
                                }
                                structure_class = structure_map.get(game_state.build_mode_item)
                                if structure_class:
                                    game_state.place_structure(structure_class, tile_to_build_on)
                        else:
                            clicked_structure = grid.get_structure_at_world_pos(world_x, world_y, game_state.structures)
                            if clicked_structure and isinstance(clicked_structure, StomperTrainingPost):
                                status = clicked_structure.toggle_pause()
                                ui.show_notification(f"Training {status}")
                            else:
                                result = grid.handle_click(world_x, world_y, PLAYER_CLICK_STRENGTH)
                                if result == "core_cultivated":
                                    if not game_state.skill_tree_unlocked:
                                        game_state.skill_tree_unlocked = True
                                        game_state.skill_points += 1
                                        ui.show_notification("Core Stabilized! Skill Tree Unlocked!")
                                    game_state.add_essence(1000)
                                elif isinstance(result, (int, float)) and result > 0:
                                     game_state.add_essence(result)

                elif event.button == 3:
                    if game_state.build_mode_item:
                        game_state.build_mode_item = None
                        pygame.mouse.set_visible(True)

        camera.handle_input(events)
        camera.update_keys(delta_time)
        
        # Update Logic
        passive_essence, grid_effects = grid.update(delta_time)
        if passive_essence > 0:
            game_state.add_essence(passive_essence)
        for effect in grid_effects:
            ui.add_floating_text(effect.get('x', 0), effect.get('y', 0), effect.get('text', ''))

        for struct in game_state.structures:
            essence, effect = struct.update(delta_time, game_state)
            if essence > 0:
                game_state.add_essence(essence)
            if effect and effect.get('type') == 'notification':
                ui.show_notification(effect['text'])
            elif effect:
                ui.add_floating_text(effect.get('x',0), effect.get('y',0), effect.get('text',''))
        
        for glim in game_state.glims:
            target = grid.find_next_target(glim, game_state.glim_targeting)
            buff = grid.get_buff_at_tile(glim, game_state.structures)
            essence, effect = glim.update(delta_time, target, buff)
            if essence == "core_cultivated":
                if not game_state.skill_tree_unlocked:
                    game_state.skill_tree_unlocked = True
                    game_state.skill_points += 1
                    ui.show_notification("Core Stabilized! Skill Tree Unlocked!")
                game_state.add_essence(1000)
            elif isinstance(essence, (int, float)) and essence > 0:
                game_state.add_essence(essence)
            if effect:
                if effect.get('type') == 'notification':
                    ui.show_notification(effect['text'])
                else:
                    ui.add_floating_text(effect.get('x',0), effect.get('y',0), effect.get('text',''))

        ui.update(delta_time)
        
        # Draw Logic
        screen.fill(SKY_COLOR)
        grid.draw(screen, camera.offset_x)

        for struct in game_state.structures:
            struct.draw(screen, camera.offset_x)

        for glim in game_state.glims:
            glim.draw(screen, camera.offset_x)

        if game_state.build_mode_item:
            tile_under_mouse = grid.get_tile_at_world_pos(world_x, world_y)
            if tile_under_mouse:
                overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                color = BUILD_VALID_COLOR if tile_under_mouse.is_buildable() else BUILD_INVALID_COLOR
                overlay.fill(color)
                on_screen_rect = tile_under_mouse.rect.copy()
                on_screen_rect.x -= camera.offset_x
                screen.blit(overlay, on_screen_rect)
            
            if build_preview_surface:
                screen.blit(build_preview_surface, build_preview_surface.get_rect(center=mouse_pos))

        ui.draw(screen, camera.offset_x)
        pygame.display.flip()
    
    pygame.quit()

if __name__ == '__main__':
    main()
