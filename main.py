import pygame
from settings import SKY_COLOR, PLAYER_CLICK_STRENGTH, BUILD_VALID_COLOR, BUILD_INVALID_COLOR, TILE_SIZE
from grid import Grid
from camera import Camera
from game_state import GameState
from ui import UI
from structure import Wellspring, Beacon

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Glim Grid")
    clock = pygame.time.Clock()

    game_state = GameState()
    ui = UI(game_state, screen_width, screen_height)
    grid = Grid(screen_height)
    camera = Camera(screen_width)
    build_preview_surface = None

    running = True
    while running:
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
                    elif ui.build_menu_open:
                        ui.build_menu_open = False
                    else:
                        running = False
                if event.key == pygame.K_1:
                    ui.build_menu_open = not ui.build_menu_open
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    if game_state.build_mode_item:
                        tile_to_build_on = grid.get_tile_at_world_pos(world_x, world_y)
                        if tile_to_build_on and tile_to_build_on.is_buildable():
                            structure_class = Wellspring if game_state.build_mode_item == "wellspring" else Beacon
                            game_state.place_structure(structure_class, tile_to_build_on)
                    else:
                        action = ui.handle_click(mouse_pos)
                        if action == "purchase_glim":
                            if game_state.can_purchase("glim"): game_state.purchase_glim(*grid.center_tile_pos)
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
                        elif action is None:
                            essence = grid.handle_click(world_x, world_y, PLAYER_CLICK_STRENGTH)
                            if essence == "core_cultivated":
                                game_state.unlock_beacon = True
                                game_state.unlock_glim_turn_around = True
                                game_state.glim_targeting = 'closest'
                                ui.show_notification("Core Stabilized! New technologies unlocked!")
                                game_state.add_essence(1000)
                            elif essence > 0: game_state.add_essence(essence)

                elif event.button == 3: # Right Click to cancel build
                    if game_state.build_mode_item:
                        game_state.build_mode_item = None
                        pygame.mouse.set_visible(True)

        delta_time = clock.tick() / 1000.0
        camera.handle_input(events)
        camera.update_keys(delta_time)
        
        passive_essence, passive_effects = grid.update(delta_time)
        if passive_essence > 0:
            game_state.add_essence(passive_essence)
            for effect in passive_effects: ui.add_floating_text(effect['x'], effect['y'], effect['text'])

        for struct in game_state.structures:
            essence, effect = struct.update(delta_time)
            if essence > 0:
                game_state.add_essence(essence)
                ui.add_floating_text(effect['x'], effect['y'], effect['text'])
        
        current_target = grid.find_next_target(game_state.glim_targeting)
        for glim in game_state.glims:
            buff = grid.get_buff_at_tile(current_target, game_state.structures)
            essence, effect = glim.update(delta_time, current_target, buff)
            if essence == "core_cultivated":
                game_state.unlock_beacon = True
                game_state.unlock_glim_turn_around = True
                game_state.glim_targeting = 'closest'
                ui.show_notification("Core Stabilized! New technologies unlocked!")
                game_state.add_essence(1000)
            elif essence > 0:
                game_state.add_essence(essence)
                ui.add_floating_text(effect['x'], effect['y'], effect['text'])

        ui.update(delta_time)
        
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