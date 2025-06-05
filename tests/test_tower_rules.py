# tests/test_tower_rules.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.game_state import GameState
from game_simulator.game_rules import tower_rules

class TestTowerRules(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_tower_progress_update(self):
        """Test that player tower progress increases over time"""
        # Set a tower to be player-owned
        tower = self.game_state.get_tower("T1")
        tower.owner = "player"
        tower.progress = 0
        
        # Update progress for 1 second
        tower_rules.update_tower_progress(self.game_state, 1.0)
        
        # Progress should have increased
        self.assertEqual(tower.progress, 5.0)  # 5 units per second
        
    def test_tower_progress_cap(self):
        """Test that tower progress caps at 100"""
        tower = self.game_state.get_tower("T1")
        tower.owner = "player"
        tower.progress = 95
        
        # Update progress for 2 seconds (should add 10, but cap at 100)
        tower_rules.update_tower_progress(self.game_state, 2.0)
        
        self.assertEqual(tower.progress, 100)
        
    def test_tower_capture(self):
        """Test that towers are captured when progress reaches 100"""
        tower = self.game_state.get_tower("T1")
        tower.owner = "enemy"
        tower.progress = 100
        
        tower_rules.check_tower_capture(self.game_state)
        
        self.assertEqual(tower.owner, "player")
        self.assertEqual(tower.progress, 0)
        
    def test_resource_generation(self):
        """Test that teams generate resources based on towers controlled"""
        # Set up team with controlled towers
        player_team = self.game_state.teams["player"]
        player_team.towers_controlled = ["T1", "T2"]
        initial_resources = player_team.resources
        
        # Generate resources for 1 second
        tower_rules.generate_tower_resources(self.game_state, 1.0)
        
        # Should gain 2 resources (1 per tower per second)
        self.assertEqual(player_team.resources, initial_resources + 2)
        
    def test_tower_upgrade(self):
        """Test tower upgrade functionality"""
        # Set up player tower and give player resources
        tower = self.game_state.get_tower("T1")
        tower.owner = "player"
        
        player_team = self.game_state.teams["player"]
        player_team.resources = 100
        
        # Attempt upgrade
        success = tower_rules.upgrade_tower(self.game_state, "T1", "basic")
        
        self.assertTrue(success)
        self.assertEqual(player_team.resources, 50)  # Should cost 50
        self.assertTrue(hasattr(tower, 'max_hp'))
        self.assertTrue(hasattr(tower, 'defense_bonus'))
        
    def test_tower_upgrade_insufficient_resources(self):
        """Test that upgrade fails with insufficient resources"""
        tower = self.game_state.get_tower("T1")
        tower.owner = "player"
        
        player_team = self.game_state.teams["player"]
        player_team.resources = 10  # Not enough for upgrade
        
        success = tower_rules.upgrade_tower(self.game_state, "T1", "basic")
        
        self.assertFalse(success)
        self.assertEqual(player_team.resources, 10)  # Should be unchanged
        
    def test_get_connected_towers(self):
        """Test getting connected towers"""
        connected = tower_rules.get_connected_towers(self.game_state, "T1")
        
        # T1 should be connected to T2
        self.assertEqual(len(connected), 1)
        self.assertEqual(connected[0].id, "T2")

if __name__ == '__main__':
    unittest.main()