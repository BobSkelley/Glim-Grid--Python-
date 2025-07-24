import pygame
from settings import GLIM_COST, WELLSPRING_COST, BEACON_COST
from glim import Glim

class GameState:
    def __init__(self):
        self.life_essence = 10000
        self.glims = []
        self.structures = []
        
        self.glim_targeting = 'right_only'
        self.build_mode_item = None

        self.unlock_beacon = False
        self.unlock_glim_turn_around = False

    def add_essence(self, amount):
        self.life_essence += amount

    def can_purchase(self, item_type):
        cost_map = {"glim": GLIM_COST, "wellspring": WELLSPRING_COST, "beacon": BEACON_COST}
        return self.life_essence >= cost_map.get(item_type, float('inf'))

    def purchase_glim(self, x, y):
        if self.can_purchase("glim"):
            self.life_essence -= GLIM_COST
            self.glims.append(Glim(x, y))
    
    def place_structure(self, structure_class, tile):
        item_name = structure_class.__name__.lower()
        if self.can_purchase(item_name):
            cost_map = {"wellspring": WELLSPRING_COST, "beacon": BEACON_COST}
            self.life_essence -= cost_map[item_name]
            new_structure = structure_class(tile)
            self.structures.append(new_structure)
            self.build_mode_item = None
            pygame.mouse.set_visible(True)