from tile import Tile
from structure import Beacon
from settings import WORLD_SIZE_TILES, TILE_SIZE, BASE_TOUGHNESS, TOUGHNESS_MULTIPLIER, GROUND_Y_OFFSET_BLOCKS, ACTIVE_ZONE_RADIUS, CORE_TILE_INDEX, CORE_TILE_TOUGHNESS, BEACON_SPEED_BOOST

class Grid:
    def __init__(self, screen_height):
        self.tiles = []
        self.ground_y = screen_height - (GROUND_Y_OFFSET_BLOCKS * TILE_SIZE)
        self.center_tile_pos = (0, 0)
        self.center_index = WORLD_SIZE_TILES // 2
        self._create_tiles()
        self.tiles[self.center_index].state = 'living'
        self.tiles[self.center_index].current_toughness = 0

    def _create_tiles(self):
        core_tile_abs_index = self.center_index + CORE_TILE_INDEX
        for i in range(WORLD_SIZE_TILES):
            is_center = (i == self.center_index)
            is_core = (i == core_tile_abs_index)
            distance_from_center = abs(i - self.center_index)
            
            toughness = round(BASE_TOUGHNESS * (TOUGHNESS_MULTIPLIER ** distance_from_center))
            if is_core: toughness = CORE_TILE_TOUGHNESS
            
            x_pos = i * TILE_SIZE
            state = 'barren'
            if distance_from_center > ACTIVE_ZONE_RADIUS:
                state = 'mountain'

            self.tiles.append(Tile(x_pos, self.ground_y, toughness, state, is_center, is_core))
            if is_center:
                self.center_tile_pos = (self.tiles[i].rect.centerx, self.tiles[i].rect.top)

    def find_next_target(self, direction):
        if direction == 'right_only':
            for i in range(self.center_index, len(self.tiles)):
                if self.tiles[i].state == 'barren':
                    return self.tiles[i]
        elif direction == 'closest':
            for i in range(1, self.center_index + 1):
                # Check right
                if self.center_index + i < len(self.tiles):
                    right_tile = self.tiles[self.center_index + i]
                    if right_tile.state == 'barren': return right_tile
                # Check left
                if self.center_index - i >= 0:
                    left_tile = self.tiles[self.center_index - i]
                    if left_tile.state == 'barren': return left_tile
        return None

    def get_buff_at_tile(self, target_tile, structures):
        buff = 1.0
        if not target_tile: return buff
        for struct in structures:
            if isinstance(struct, Beacon):
                dist = abs(struct.tile.rect.centerx - target_tile.rect.centerx)
                if dist <= TILE_SIZE * 1.5:
                    buff *= BEACON_SPEED_BOOST
        return buff

    def get_tile_at_world_pos(self, world_x, world_y):
        for tile in self.tiles:
            if tile.rect.collidepoint(world_x, world_y):
                return tile
        return None

    def handle_click(self, world_x, world_y, click_strength):
        tile = self.get_tile_at_world_pos(world_x, world_y)
        if tile and tile.state == 'barren':
            return tile.take_damage(click_strength)
        return 0

    def update(self, delta_time):
        total_essence_gained = 0
        effects_to_create = []
        for tile in self.tiles:
            essence = tile.update(delta_time)
            if essence > 0:
                total_essence_gained += essence
                effects_to_create.append({'x': tile.rect.centerx, 'y': tile.rect.y, 'text': f"+{essence}"})
        return total_essence_gained, effects_to_create

    def draw(self, screen, camera_offset_x):
        for tile in self.tiles:
            tile.draw(screen, camera_offset_x)