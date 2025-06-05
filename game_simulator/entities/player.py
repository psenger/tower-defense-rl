# game_simulator/entities/player.py
from .hero_set import HeroSet
from .hero import Hero

class Player:
    def __init__(self, player_id, alliance_id):
        self.id = player_id
        self.alliance_id = alliance_id
        self.stamina = 4  # Summit Stamina per half
        
        # Hero management
        self.initial_hero_pool = []  # 50 initially generated heroes
        self.selected_hero_sets = []  # 6 sets of 5 heroes each (30 total)
        self.discarded_heroes = []   # 20 heroes not selected
        
        # Generate initial hero pool
        self._generate_initial_heroes()
        
    def _generate_initial_heroes(self):
        """Generate 50 random heroes for this player"""
        self.initial_hero_pool = []
        for i in range(50):
            hero_id = f"P{self.id}_H{i+1}"
            hero = Hero(hero_id, is_npc=False)
            self.initial_hero_pool.append(hero)
    
    def select_hero_sets(self, hero_indices=None):
        """Select 30 heroes (6 sets of 5) from the 50 initial heroes"""
        if hero_indices is None:
            # Auto-select first 30 heroes if no specific selection
            hero_indices = list(range(30))
        
        if len(hero_indices) != 30:
            raise ValueError("Must select exactly 30 heroes")
        
        # Create 6 hero sets
        selected_heroes = [self.initial_hero_pool[i] for i in hero_indices]
        self.selected_hero_sets = []
        
        for set_idx in range(6):
            set_id = f"P{self.id}_Set{set_idx+1}"
            heroes_for_set = selected_heroes[set_idx*5:(set_idx+1)*5]
            hero_set = HeroSet(set_id, self.id, heroes_for_set, is_npc=False)
            self.selected_hero_sets.append(hero_set)
        
        # Store discarded heroes
        self.discarded_heroes = [self.initial_hero_pool[i] for i in range(50) if i not in hero_indices]
    
    def get_available_sets_for_attack(self):
        """Get hero sets that can be used for attacks"""
        return [hero_set for hero_set in self.selected_hero_sets if hero_set.can_attack()]
    
    def get_garrisoned_sets(self):
        """Get hero sets currently garrisoning strongholds"""
        return [hero_set for hero_set in self.selected_hero_sets if hero_set.is_garrisoned]
    
    def can_attack(self):
        """Check if player has stamina and available sets to attack"""
        return self.stamina > 0 and len(self.get_available_sets_for_attack()) > 0
    
    def consume_stamina(self):
        """Consume 1 stamina for an attack"""
        if self.stamina > 0:
            self.stamina -= 1
            return True
        return False
    
    def restore_stamina_for_new_half(self):
        """Restore stamina to 4 for new half"""
        self.stamina = 4
    
    def reset_hero_sets_for_new_half(self):
        """Reset all hero sets' consumed status for new half"""
        for hero_set in self.selected_hero_sets:
            hero_set.reset_for_new_half()
    
    def get_total_power_rating(self):
        """Calculate total power rating of all selected hero sets"""
        total_attack = 0
        total_hp = 0
        for hero_set in self.selected_hero_sets:
            for hero in hero_set.heroes:
                total_attack += hero.attack
                total_hp += hero.current_hp
        return total_attack + total_hp
    
    def __repr__(self):
        available_sets = len(self.get_available_sets_for_attack())
        garrisoned_sets = len(self.get_garrisoned_sets())
        return f"Player({self.id}, Alliance:{self.alliance_id}, Stamina:{self.stamina}, Available:{available_sets}, Garrisoned:{garrisoned_sets})"