# game_simulator/entities/hero.py
import random
import numpy as np

class Hero:
    def __init__(self, hero_id, is_npc=False, stronghold_level=1):
        self.id = hero_id
        self.is_npc = is_npc
        self.attack = 0
        self.defense = 0
        self.max_hp = 0
        self.current_hp = 0
        self.is_alive = True
        
        # Generate stats based on type
        if is_npc:
            self._generate_npc_stats(stronghold_level)
        else:
            self._generate_player_stats()
    
    def _generate_player_stats(self):
        """Generate stats for player heroes using normal distribution"""
        # Stats from game rules
        self.attack = max(1, int(np.random.normal(4627, 432)))
        self.defense = max(1, int(np.random.normal(4195, 346))) 
        self.max_hp = max(1, int(np.random.normal(8088, 783)))
        self.current_hp = self.max_hp
    
    def _generate_npc_stats(self, stronghold_level):
        """FIXED: Generate NPC stats using same distributions as player heroes

        Rule from README: "NPC Hero stats are generated using the same distributions as Player Heroes"
        This means NPCs should use np.random.normal, not fixed values.
        """
        # Base player averages - use same distributions as players
        base_attack = 4627
        base_defense = 4195
        base_hp = 8088
        
        # Base standard deviations from player distribution
        attack_std = 432
        defense_std = 346
        hp_std = 783
        
        # Add slight variance to make NPCs feel different without being overpowered
        variance = 0.1  # 10% variance

        self.attack = int(base_attack * (1 + random.uniform(-variance, variance)))
        self.defense = int(base_defense * (1 + random.uniform(-variance, variance)))
        self.max_hp = int(base_hp * (1 + random.uniform(-variance, variance)))
        self.current_hp = self.max_hp
    
    def take_damage(self, damage):
        """Apply damage to the hero"""
        if not self.is_alive:
            return 0
            
        actual_damage = max(0, damage)
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        if self.current_hp <= 0:
            self.is_alive = False
            self.current_hp = 0
            
        return actual_damage
    
    def heal_full(self):
        """Restore hero to full health"""
        self.current_hp = self.max_hp
        self.is_alive = True
    
    def get_hp_percentage(self):
        """Get current HP as percentage of max HP"""
        if self.max_hp <= 0:
            return 0
        return (self.current_hp / self.max_hp) * 100
    
    def __repr__(self):
        status = "Alive" if self.is_alive else "Dead"
        npc_str = "NPC" if self.is_npc else "Player"
        return f"Hero({self.id}, {npc_str}, ATK:{self.attack}, DEF:{self.defense}, HP:{self.current_hp}/{self.max_hp}, {status})"