# tests/test_alliance.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.entities.alliance import Alliance

class TestAlliance(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.alliance = Alliance(1, "Test Alliance", "TestHome", (255, 0, 0))
    
    def test_alliance_creation(self):
        """Test creating an alliance"""
        self.assertEqual(self.alliance.id, 1)
        self.assertEqual(self.alliance.name, "Test Alliance")
        self.assertEqual(self.alliance.home_stronghold, "TestHome")
        self.assertEqual(self.alliance.color, (255, 0, 0))
        
        # Should have 50 players
        self.assertEqual(len(self.alliance.players), 50)
        
        # Should start with home stronghold controlled
        self.assertIn("TestHome", self.alliance.controlled_strongholds)
        
        # All players should start with 4 stamina
        for player in self.alliance.players:
            self.assertEqual(player.stamina, 4)
    
    def test_player_creation(self):
        """Test that players are created correctly"""
        for i, player in enumerate(self.alliance.players):
            self.assertEqual(player.id, f"P{self.alliance.id}_{i+1}")
            self.assertEqual(player.alliance_id, self.alliance.id)
            self.assertEqual(len(player.selected_hero_sets), 2)  # Each player has 2 hero sets
            
            # Each hero set should have 5 heroes
            for hero_set in player.selected_hero_sets:
                self.assertEqual(len(hero_set.heroes), 5)
    
    def test_available_hero_sets(self):
        """Test getting available hero sets"""
        available = self.alliance.get_all_available_hero_sets()
        
        # Should have 100 hero sets total (50 players * 2 sets each)
        self.assertEqual(len(available), 100)
        
        # All should be available initially
        for hero_set in available:
            self.assertTrue(hero_set.can_attack())
    
    def test_available_hero_sets_after_consumption(self):
        """Test available hero sets after some are consumed"""
        # Mark some hero sets as consumed
        available = self.alliance.get_all_available_hero_sets()
        consumed_sets = available[:10]
        
        for hero_set in consumed_sets:
            hero_set.mark_consumed_for_attack()
        
        # Should now have 90 available
        still_available = self.alliance.get_all_available_hero_sets()
        self.assertEqual(len(still_available), 90)
        
        # None of the consumed sets should be in available list
        for hero_set in consumed_sets:
            self.assertNotIn(hero_set, still_available)
    
    def test_available_hero_sets_with_no_stamina(self):
        """Test that players with no stamina don't contribute hero sets"""
        # Exhaust stamina for first 10 players
        for i in range(10):
            self.alliance.players[i].stamina = 0
        
        available = self.alliance.get_all_available_hero_sets()
        
        # Should have 80 hero sets (40 players * 2 sets each)
        self.assertEqual(len(available), 80)
    
    def test_available_hero_sets_with_dead_heroes(self):
        """Test that hero sets with all dead heroes are not available"""
        # Kill all heroes in first player's first hero set
        first_set = self.alliance.players[0].selected_hero_sets[0]
        for hero in first_set.heroes:
            hero.take_damage(hero.max_hp + 100)
        
        available = self.alliance.get_all_available_hero_sets()
        
        # Should have 99 hero sets (one less due to all dead heroes)
        self.assertEqual(len(available), 99)
        self.assertNotIn(first_set, available)
    
    def test_stronghold_control(self):
        """Test stronghold control management"""
        # Add a stronghold
        self.alliance.add_controlled_stronghold("S1")
        self.assertIn("S1", self.alliance.controlled_strongholds)
        
        # Remove a stronghold
        self.alliance.remove_controlled_stronghold("S1")
        self.assertNotIn("S1", self.alliance.controlled_strongholds)
        
        # Home stronghold should still be there
        self.assertIn("TestHome", self.alliance.controlled_strongholds)
    
    def test_cannot_remove_home_stronghold(self):
        """Test that home stronghold cannot be removed from control"""
        initial_count = len(self.alliance.controlled_strongholds)
        
        # Try to remove home stronghold
        self.alliance.remove_controlled_stronghold("TestHome")
        
        # Should still be controlled
        self.assertIn("TestHome", self.alliance.controlled_strongholds)
        self.assertEqual(len(self.alliance.controlled_strongholds), initial_count)
    
    def test_stamina_management(self):
        """Test stamina restoration and tracking"""
        # Reduce stamina for all players
        for player in self.alliance.players:
            player.stamina = 1
        
        # Restore stamina
        self.alliance.restore_all_stamina()
        
        # All players should have 4 stamina again
        for player in self.alliance.players:
            self.assertEqual(player.stamina, 4)
    
    def test_hero_set_reset(self):
        """Test resetting all hero set attack consumption"""
        # Mark some hero sets as consumed
        available = self.alliance.get_all_available_hero_sets()
        for hero_set in available[:20]:
            hero_set.mark_consumed_for_attack()
        
        # Verify they're consumed
        still_available = self.alliance.get_all_available_hero_sets()
        self.assertEqual(len(still_available), 80)
        
        # Reset all
        self.alliance.reset_all_hero_set_attacks()
        
        # All should be available again (assuming stamina)
        available_after_reset = self.alliance.get_all_available_hero_sets()
        self.assertEqual(len(available_after_reset), 100)
    
    def test_total_score_calculation(self):
        """Test calculation of total alliance score"""
        # Add some controlled strongholds
        self.alliance.add_controlled_stronghold("S1")  # Level 1 = 1 point
        self.alliance.add_controlled_stronghold("L2_1")  # Level 2 = 2 points
        self.alliance.add_controlled_stronghold("L3")  # Level 3 = 3 points
        
        # Mock stronghold levels for calculation
        stronghold_levels = {
            "TestHome": 0,  # Home = 0 points
            "S1": 1,
            "L2_1": 2, 
            "L3": 3
        }
        
        score = self.alliance.calculate_score(stronghold_levels)
        expected_score = 0 + 1 + 2 + 3  # 6 points total
        self.assertEqual(score, expected_score)
    
    def test_player_by_id_lookup(self):
        """Test finding players by ID"""
        target_player = self.alliance.players[10]
        found_player = self.alliance.get_player_by_id(target_player.id)
        
        self.assertEqual(found_player, target_player)
        
        # Test non-existent player
        non_existent = self.alliance.get_player_by_id("INVALID_ID")
        self.assertIsNone(non_existent)
    
    def test_alliance_representation(self):
        """Test alliance string representation"""
        alliance_str = str(self.alliance)
        
        self.assertIn("Test Alliance", alliance_str)
        self.assertIn("50 players", alliance_str)
        self.assertIn("1 strongholds", alliance_str)  # Just home initially

if __name__ == '__main__':
    unittest.main()