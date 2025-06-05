# game_simulator/entities/summit_battle.py
import random
import time

class SummitBattle:
    """5v5 Hero Set battle following the game rules"""
    
    def __init__(self, battle_id, attacking_set, defending_set, stronghold_id):
        self.id = battle_id
        self.attacking_set = attacking_set
        self.defending_set = defending_set
        self.stronghold_id = stronghold_id
        
        # Battle state
        self.current_step = 0
        self.max_steps = 50
        self.is_active = True
        self.winner = None
        self.is_attacker_turn = True  # Attacker goes first
        
        # Damage tracking for tie-breaking
        self.attacker_total_damage = 0
        self.defender_total_damage = 0
        
        # Battle log for viewing
        self.battle_log = []
        self.start_time = time.time()
        
        # Initial log entry
        self._log_action(f"Battle started at {stronghold_id}: {attacking_set.id} vs {defending_set.id}")
    
    def _log_action(self, message):
        """Add an action to the battle log"""
        timestamp = time.time() - self.start_time
        self.battle_log.append(f"[{timestamp:.1f}s] {message}")
    
    def execute_turn(self):
        """Execute one turn of the battle"""
        if not self.is_active:
            return
        
        # Determine acting and defending sets
        if self.is_attacker_turn:
            acting_set = self.attacking_set
            defending_set = self.defending_set
            side_name = "Attacker"
        else:
            acting_set = self.defending_set
            defending_set = self.attacking_set
            side_name = "Defender"
        
        # Check if acting side has living heroes
        living_actors = acting_set.get_living_heroes()
        living_defenders = defending_set.get_living_heroes()
        
        if not living_actors or not living_defenders:
            self._end_battle()
            return
        
        # Select random hero to act
        acting_hero = random.choice(living_actors)
        
        # Generate random number of hits (1-4)
        num_hits = random.randint(1, 4)
        
        self._log_action(f"{side_name} {acting_hero.id} attacks with {num_hits} hits")
        
        # Calculate damage per hit
        avg_defense = defending_set.get_average_defense()
        damage_per_hit = max(0, acting_hero.attack - avg_defense)
        
        if damage_per_hit <= 0:
            self._log_action(f"Attack ineffective! (ATK:{acting_hero.attack} vs AVG_DEF:{avg_defense:.1f})")
            total_damage = 0
        else:
            # Apply damage for each hit
            total_damage = 0
            for hit in range(num_hits):
                hit_damage = self._apply_aoe_damage(damage_per_hit, living_defenders)
                total_damage += hit_damage
            
            # Track total damage for tie-breaking
            if self.is_attacker_turn:
                self.attacker_total_damage += total_damage
            else:
                self.defender_total_damage += total_damage
        
        # Switch turns
        self.is_attacker_turn = not self.is_attacker_turn
        
        # If both sides completed a turn, increment step
        if self.is_attacker_turn:  # Back to attacker means both sides acted
            self.current_step += 1
        
        # Check victory conditions
        self._check_victory_conditions()
    
    def _apply_aoe_damage(self, damage_per_hit, living_defenders):
        """Apply AoE damage with random weighting"""
        if not living_defenders or damage_per_hit <= 0:
            return 0
        
        # Generate random weights for each living defender
        weights = [random.random() for _ in living_defenders]
        total_weight = sum(weights)
        
        if total_weight <= 0:
            return 0
        
        # Normalize weights and apply damage
        total_damage_dealt = 0
        for i, defender in enumerate(living_defenders):
            weight_proportion = weights[i] / total_weight
            damage_to_apply = damage_per_hit * weight_proportion
            
            actual_damage = defender.take_damage(damage_to_apply)
            total_damage_dealt += actual_damage
            
            if not defender.is_alive:
                self._log_action(f"  {defender.id} defeated! (took {actual_damage:.1f} damage)")
            else:
                self._log_action(f"  {defender.id} takes {actual_damage:.1f} damage (HP: {defender.current_hp:.1f}/{defender.max_hp})")
        
        return total_damage_dealt
    
    def _check_victory_conditions(self):
        """Check if battle should end based on victory conditions"""
        attacker_living = len(self.attacking_set.get_living_heroes())
        defender_living = len(self.defending_set.get_living_heroes())
        
        # Check if one side is completely defeated
        if attacker_living == 0 and defender_living > 0:
            self.winner = "defender"
            self._log_action(f"Defenders win! All attackers defeated.")
            self._end_battle()
        elif defender_living == 0 and attacker_living > 0:
            self.winner = "attacker"
            self._log_action(f"Attackers win! All defenders defeated.")
            self._end_battle()
        elif attacker_living == 0 and defender_living == 0:
            self.winner = "draw"
            self._log_action(f"Draw! All heroes defeated.")
            self._end_battle()
        elif self.current_step >= self.max_steps:
            # 50 step limit reached
            self._resolve_step_limit_tie()
            self._end_battle()
    
    def _resolve_step_limit_tie(self):
        """Resolve battle when 50 step limit is reached"""
        if self.attacker_total_damage > self.defender_total_damage:
            self.winner = "attacker"
            self._log_action(f"Attackers win by damage! (ATK:{self.attacker_total_damage:.1f} vs DEF:{self.defender_total_damage:.1f})")
        elif self.defender_total_damage > self.attacker_total_damage:
            self.winner = "defender"
            self._log_action(f"Defenders win by damage! (DEF:{self.defender_total_damage:.1f} vs ATK:{self.attacker_total_damage:.1f})")
        else:
            # Equal damage - defender wins (attacker loses on tie)
            self.winner = "defender"
            self._log_action(f"Tie in damage - Defenders win! (Both dealt {self.attacker_total_damage:.1f} damage)")
    
    def _end_battle(self):
        """End the battle"""
        self.is_active = False
        duration = time.time() - self.start_time
        self._log_action(f"Battle ended after {self.current_step} steps ({duration:.1f}s)")
    
    def simulate_to_completion(self):
        """Simulate entire battle to completion"""
        turn_count = 0
        max_turns = 1000  # Safety limit
        
        while self.is_active and turn_count < max_turns:
            self.execute_turn()
            turn_count += 1
            
            # Safety check
            if turn_count >= max_turns:
                self._log_action("Battle terminated - too many turns!")
                self.winner = "defender"  # Default to defender in case of issues
                self._end_battle()
    
    def get_battle_status(self):
        """Get current battle status for display"""
        attacker_living = len(self.attacking_set.get_living_heroes())
        defender_living = len(self.defending_set.get_living_heroes())
        
        return {
            "battle_id": self.id,
            "stronghold": self.stronghold_id,
            "step": self.current_step,
            "max_steps": self.max_steps,
            "is_active": self.is_active,
            "winner": self.winner,
            "attacker_living": attacker_living,
            "defender_living": defender_living,
            "attacker_damage": self.attacker_total_damage,
            "defender_damage": self.defender_total_damage,
            "current_turn": "Attacker" if self.is_attacker_turn else "Defender",
        }
    
    def get_recent_log_entries(self, count=10):
        """Get recent battle log entries"""
        return self.battle_log[-count:]
    
    def __repr__(self):
        status = "Active" if self.is_active else f"Ended ({self.winner} wins)"
        attacker_living = len(self.attacking_set.get_living_heroes())
        defender_living = len(self.defending_set.get_living_heroes())
        return f"SummitBattle({self.id}, {self.stronghold_id}, Step {self.current_step}/{self.max_steps}, ATK:{attacker_living} vs DEF:{defender_living}, {status})"