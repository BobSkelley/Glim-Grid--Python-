import pygame
from settings import GLIM_COST, WELLSPRING_COST, BEACON_COST, STOMPER_POST_COST, STOMPER_CONVERSION_COST
from glim import Glim

class GameState:
    def __init__(self):
        self.life_essence = 999990
        self.glims = []
        self.structures = []
        self.glim_cap = 100
        
        self.glim_targeting = 'right_only'
        self.build_mode_item = None

        self.skill_tree_unlocked = False
        self.skill_points = 0
        self.skills = {
            'glimdraulic_drills': {
                'unlocked': False,
                'cost_essence': 500,
                'cost_sp': 1,
                'req_glims': 5
            }
        }

    def add_essence(self, amount):
        self.life_essence += amount

    def can_purchase(self, item_type):
        cost_map = {
            "glim": GLIM_COST, 
            "wellspring": WELLSPRING_COST, 
            "beacon": BEACON_COST,
            "stompertrainingpost": STOMPER_POST_COST
        }
        
        if item_type == "glim":
            return self.life_essence >= GLIM_COST and len(self.glims) < self.glim_cap
        
        return self.life_essence >= cost_map.get(item_type, float('inf'))

    def can_purchase_skill(self, skill_name):
        skill = self.skills.get(skill_name)
        if not skill or skill['unlocked']:
            return False
        
        has_sp = self.skill_points >= skill['cost_sp']
        has_essence = self.life_essence >= skill['cost_essence']
        
        # Count standard glims for the requirement
        standard_glim_count = sum(1 for glim in self.glims if glim.glim_type == 'standard')
        has_glims = standard_glim_count >= skill['req_glims']
        
        return has_sp and has_essence and has_glims

    def purchase_skill(self, skill_name, center_pos):
        if self.can_purchase_skill(skill_name):
            skill = self.skills[skill_name]
            self.life_essence -= skill['cost_essence']
            self.skill_points -= skill['cost_sp']
            skill['unlocked'] = True
            
            # Special effect for this skill: grant 5 free stompers
            if skill_name == 'glimdraulic_drills':
                for _ in range(5):
                    if len(self.glims) < self.glim_cap:
                        self.glims.append(Glim(*center_pos, glim_type='stomper'))
            return True
        return False

    def purchase_glim(self, x, y):
        if self.can_purchase("glim"):
            self.life_essence -= GLIM_COST
            self.glims.append(Glim(x, y, glim_type='standard'))
    
    def place_structure(self, structure_class, tile):
        item_name = structure_class.__name__.lower()
        if self.can_purchase(item_name):
            cost_map = {
                "wellspring": WELLSPRING_COST, 
                "beacon": BEACON_COST,
                "stompertrainingpost": STOMPER_POST_COST
            }
            self.life_essence -= cost_map.get(item_name, 0)
            new_structure = structure_class(tile)
            self.structures.append(new_structure)
            self.build_mode_item = None
            pygame.mouse.set_visible(True)

    def convert_glim_to_stomper(self):
        if self.life_essence >= STOMPER_CONVERSION_COST:
            # Find the first available standard glim to convert
            for glim in self.glims:
                if glim.glim_type == 'standard':
                    self.life_essence -= STOMPER_CONVERSION_COST
                    glim.convert_to_stomper()
                    return True # Successfully converted one
        return False
