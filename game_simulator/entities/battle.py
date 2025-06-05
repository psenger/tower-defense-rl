# game_simulator/entities/battle.py
import random

class Battle:
    def __init__(self, tower_id, attackers, defenders):
        self.tower_id = tower_id
        self.attackers = attackers  # List of units
        self.defenders = defenders  # List of units
        self.duration = 0.0
        self.battle_active = True
        self.winner = None
        
    def update(self, dt):
        if not self.battle_active:
            return
            
        self.duration += dt
        
        # Remove dead units
        self.attackers = [unit for unit in self.attackers if unit.is_alive()]
        self.defenders = [unit for unit in self.defenders if unit.is_alive()]
        
        # Check if battle is over
        if not self.attackers and not self.defenders:
            self.battle_active = False
            self.winner = None  # Draw
        elif not self.attackers:
            self.battle_active = False
            self.winner = "defenders"
        elif not self.defenders:
            self.battle_active = False
            self.winner = "attackers"
        else:
            # Simulate combat
            self._simulate_combat(dt)
            
    def _simulate_combat(self, dt):
        # Simple combat simulation - units randomly attack each other
        all_attackers = [unit for unit in self.attackers if unit.is_alive()]
        all_defenders = [unit for unit in self.defenders if unit.is_alive()]
        
        # Attackers attack defenders
        for attacker in all_attackers:
            if all_defenders:
                target = random.choice(all_defenders)
                target.take_damage(attacker.attack)
                
        # Defenders attack attackers
        for defender in all_defenders:
            if all_attackers:
                target = random.choice(all_attackers)
                target.take_damage(defender.attack)
                
    def is_over(self):
        return not self.battle_active
        
    def get_outcome(self):
        return self.winner
        
    def __repr__(self):
        return f"Battle(Tower: {self.tower_id}, Attackers: {len(self.attackers)}, Defenders: {len(self.defenders)}, Active: {self.battle_active})"