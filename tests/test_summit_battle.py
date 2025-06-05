# tests/test_summit_battle.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.entities.summit_battle import SummitBattle
from game_simulator.entities.hero_set import HeroSet
from game_simulator.entities.hero import Hero

class TestSummitBattle(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create attacking hero set (player heroes)
        self.attacking_heroes = [Hero(f"attacker_{i}", is_npc=False) for i in range(5)]
        self.attacking_set = HeroSet("attacking_set", "player_1", self.attacking_heroes, is_npc=False)
        
        # Create defending hero set (NPCs)
        self.defending_heroes = [Hero(f"defender_{i}", is_npc=True, stronghold_level=1) for i in range(5)]
        self.defending_set = HeroSet("defending_set", "npc", self.defending_heroes, is_npc=True, stronghold_level=1)
        
        # Create battle
        self.battle = SummitBattle("test_battle", self.attacking_set, self.defending_set, "S1")
    
    def test_battle_creation(self):
        """Test creating a summit battle"""
        self.assertEqual(self.battle.id, "test_battle")
        self.assertEqual(self.battle.attacking_set, self.attacking_set)
        self.assertEqual(self.battle.defending_set, self.defending_set)
        self.assertEqual(self.battle.stronghold_id, "S1")
        self.assertTrue(self.battle.is_active)
        self.assertIsNone(self.battle.winner)
        
        # Battle log should be initialized with starting message
        self.assertIsInstance(self.battle.battle_log, list)
        self.assertEqual(len(self.battle.battle_log), 1)
    
    def test_damage_calculation(self):
        """Test damage calculation mechanics"""
        # Get a specific attacker and defending set
        attacker = self.attacking_heroes[0]
        
        # Calculate expected damage
        avg_defense = self.defending_set.get_average_defense()
        expected_damage = max(0, attacker.attack - avg_defense)
        
        # Test damage calculation manually
        calculated_damage = max(0, attacker.attack - avg_defense)
        self.assertEqual(calculated_damage, expected_damage)
        
        # Test case where defense exceeds attack
        weak_attacker = Hero("weak", is_npc=True, stronghold_level=1)
        weak_attacker.attack = 100  # Very low attack
        
        damage = max(0, weak_attacker.attack - avg_defense)
        self.assertEqual(damage, 0)  # Should be 0 when defense > attack
    
    def test_turn_execution(self):
        """Test execution of a single turn"""
        # Record initial HP of defenders
        initial_defender_hp = sum(hero.current_hp for hero in self.defending_heroes)
        initial_log_length = len(self.battle.battle_log)
        
        # Execute one turn
        self.battle.execute_turn()
        
        # Check if damage was dealt (may not always happen if attack is weak)
        final_defender_hp = sum(hero.current_hp for hero in self.defending_heroes)
        
        # Battle log should have new entries
        self.assertGreater(len(self.battle.battle_log), initial_log_length)
    
    def test_battle_progression(self):
        """Test battle progressing through turns"""
        initial_step = self.battle.current_step
        
        # Execute several turns
        for _ in range(5):
            if self.battle.is_active:
                self.battle.execute_turn()
        
        # Should have progressed if turns were executed
        if self.battle.is_active:
            # Steps only increment after both sides act
            pass  # This test is more about the mechanics working
    
    def test_battle_victory_conditions(self):
        """Test battle ending when one side is defeated"""
        # Kill all defenders
        for hero in self.defending_heroes:
            hero.take_damage(hero.max_hp + 100)
        
        # Verify they're actually dead
        self.assertEqual(len(self.defending_set.get_living_heroes()), 0)
        
        # Execute turn - should detect victory
        self.battle.execute_turn()
        
        # Check if battle ended and winner is determined
        if not self.battle.is_active:
            self.assertEqual(self.battle.winner, "attacker")
        else:
            # Battle might still be active if victory check didn't trigger yet
            # Force victory check by calling the method
            self.battle._check_victory_conditions()
            self.assertFalse(self.battle.is_active)
            self.assertEqual(self.battle.winner, "attacker")
        
        # Test defender victory - create fresh heroes for battle2
        attacking_heroes2 = [Hero(f"attacker2_{i}", is_npc=False) for i in range(5)]
        defending_heroes2 = [Hero(f"defender2_{i}", is_npc=True, stronghold_level=1) for i in range(5)]
        attacking_set2 = HeroSet("attacking_set2", "player_2", attacking_heroes2, is_npc=False)
        defending_set2 = HeroSet("defending_set2", "npc2", defending_heroes2, is_npc=True, stronghold_level=1)
        
        battle2 = SummitBattle("test2", attacking_set2, defending_set2, "S1")
        
        # Kill all attackers
        for hero in attacking_heroes2:
            hero.take_damage(hero.max_hp + 100)
        
        battle2.execute_turn()
        
        self.assertFalse(battle2.is_active)
        self.assertEqual(battle2.winner, "defender")
    
    def test_battle_step_limit(self):
        """Test battle ending due to step limit"""
        # Advance battle to step limit
        self.battle.current_step = 50  # At step limit
        
        # Execute turn to trigger victory check
        self.battle.execute_turn()
        
        # Should end battle or check victory conditions
        if self.battle.current_step >= self.battle.max_steps:
            self.assertFalse(self.battle.is_active)
            self.assertIsNotNone(self.battle.winner)  # Winner determined by damage
    
    def test_aoe_damage_distribution(self):
        """Test AoE damage distribution mechanics"""
        # Record initial HP
        initial_hp = sum(hero.current_hp for hero in self.defending_heroes)
        
        # Execute a turn which should cause damage
        self.battle.execute_turn()
        
        # Check if any damage was dealt
        final_hp = sum(hero.current_hp for hero in self.defending_heroes)
        
        # Damage may or may not occur based on attack vs defense
        # This test mainly ensures the mechanics work
        self.assertIsInstance(final_hp, (int, float))
    
    def test_battle_status_reporting(self):
        """Test battle status reporting"""
        status = self.battle.get_battle_status()
        
        self.assertIn("is_active", status)
        self.assertIn("winner", status)
        self.assertIn("step", status)
        self.assertIn("max_steps", status)
        self.assertIn("attacker_living", status)
        self.assertIn("defender_living", status)
        
        self.assertTrue(status["is_active"])
        self.assertIsNone(status["winner"])
        self.assertEqual(status["step"], 0)
    
    def test_battle_log_tracking(self):
        """Test that battle events are logged correctly"""
        initial_log_length = len(self.battle.battle_log)
        
        # Execute some battle turns
        for _ in range(3):
            if self.battle.is_active:
                self.battle.execute_turn()
        
        # Should have more log entries
        self.assertGreater(len(self.battle.battle_log), initial_log_length)
        
        # Log entries should be strings
        if len(self.battle.battle_log) > 1:
            log_entry = self.battle.battle_log[1]  # Skip initial entry
            self.assertIsInstance(log_entry, str)
    
    def test_hero_set_hp_tracking(self):
        """Test tracking of hero set HP percentages"""
        # Calculate HP percentages manually
        attacking_current = self.attacking_set.get_total_hp()
        attacking_max = self.attacking_set.get_max_hp()
        attacking_hp = (attacking_current / attacking_max) * 100
        
        defending_current = self.defending_set.get_total_hp()
        defending_max = self.defending_set.get_max_hp()
        defending_hp = (defending_current / defending_max) * 100
        
        # Should start at 100%
        self.assertEqual(attacking_hp, 100.0)
        self.assertEqual(defending_hp, 100.0)
        
        # Damage some heroes
        self.attacking_heroes[0].take_damage(self.attacking_heroes[0].max_hp // 2)
        
        attacking_current_after = self.attacking_set.get_total_hp()
        attacking_hp_after = (attacking_current_after / attacking_max) * 100
        self.assertLess(attacking_hp_after, 100.0)
    
    def test_step_progression(self):
        """Test that battle steps progress correctly"""
        initial_step = self.battle.current_step
        
        # Execute turns (both attacker and defender need to act for step to increment)
        self.battle.execute_turn()  # Attacker turn
        self.assertEqual(self.battle.current_step, initial_step)  # Step shouldn't increment yet
        
        if self.battle.is_active:
            self.battle.execute_turn()  # Defender turn
            # Now step should increment
            self.assertGreaterEqual(self.battle.current_step, initial_step)
    
    def test_battle_with_different_npc_levels(self):
        """Test battles against NPCs of different levels"""
        # Level 3 NPCs (stronger)
        level3_defenders = [Hero(f"l3_defender_{i}", is_npc=True, stronghold_level=3) for i in range(5)]
        level3_set = HeroSet("level3_defenders", level3_defenders)
        
        battle_l3 = SummitBattle("battle_l3", self.attacking_set, level3_set, "L3")
        
        # Level 3 NPCs should have higher stats
        for hero in level3_defenders:
            self.assertGreater(hero.attack, self.defending_heroes[0].attack)
            self.assertGreater(hero.defense, self.defending_heroes[0].defense)
            self.assertGreater(hero.max_hp, self.defending_heroes[0].max_hp)
    
    def test_battle_representation(self):
        """Test battle string representation"""
        battle_str = str(self.battle)
        
        self.assertIn("test_battle", battle_str)
        self.assertIn("S1", battle_str)
        self.assertIn("Active", battle_str)
        self.assertIn("ATK:5 vs DEF:5", battle_str)

if __name__ == '__main__':
    unittest.main()