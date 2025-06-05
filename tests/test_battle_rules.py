# tests/test_battle_rules.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.game_state import GameState
from game_simulator.entities.unit import Unit
from game_simulator.entities.battle import Battle
from game_simulator.game_rules import battle_rules

class TestBattleRules(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_battle_creation(self):
        """Test that battles can be created properly"""
        # Create some test units
        attacker = Unit("att1", "basic", "player")
        defender = Unit("def1", "basic", "enemy")
        
        battle = Battle("T1", [attacker], [defender])
        
        self.assertEqual(battle.tower_id, "T1")
        self.assertEqual(len(battle.attackers), 1)
        self.assertEqual(len(battle.defenders), 1)
        self.assertTrue(battle.battle_active)
        
    def test_battle_outcome_attackers_win(self):
        """Test battle outcome when attackers win"""
        # Create a strong attacker and weak defender
        strong_attacker = Unit("att1", "basic", "player")
        strong_attacker.attack = 100
        
        weak_defender = Unit("def1", "basic", "enemy")
        weak_defender.hp = 1
        
        battle = Battle("T1", [strong_attacker], [weak_defender])
        
        # Simulate battle until completion
        while battle.battle_active:
            battle.update(0.1)
            
        self.assertEqual(battle.get_outcome(), "attackers")
        
    def test_battle_outcome_defenders_win(self):
        """Test battle outcome when defenders win"""
        # Create a weak attacker and strong defender
        weak_attacker = Unit("att1", "basic", "player")
        weak_attacker.hp = 1
        
        strong_defender = Unit("def1", "basic", "enemy")
        strong_defender.attack = 100
        
        battle = Battle("T1", [weak_attacker], [strong_defender])
        
        # Simulate battle until completion
        while battle.battle_active:
            battle.update(0.1)
            
        self.assertEqual(battle.get_outcome(), "defenders")
        
    def test_battle_advantage_calculation(self):
        """Test battle advantage calculation"""
        attackers = [Unit("att1", "basic", "player")]
        defenders = [Unit("def1", "basic", "enemy")]
        
        advantage = battle_rules.calculate_battle_advantage(attackers, defenders)
        
        # Should be a positive number
        self.assertGreater(advantage, 0)
        # Defenders should have slight advantage due to defensive bonus
        self.assertLess(advantage, 1.0)

if __name__ == '__main__':
    unittest.main()