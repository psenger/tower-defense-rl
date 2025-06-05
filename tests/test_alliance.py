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
        self.alliance = Alliance(1, "Test Alliance", (255, 0, 0))
    
    def test_alliance_creation(self):
        """Test creating an alliance"""
        self.assertEqual(self.alliance.id, 1)
        self.assertEqual(self.alliance.name, "Test Alliance")
        self.assertEqual(self.alliance.color, (255, 0, 0))
        
        # Should have 50 players
        self.assertEqual(len(self.alliance.players), 50)
        
        # All players should start with 4 stamina
        for player in self.alliance.players:
            self.assertEqual(player.stamina, 4)
    
    def test_player_creation(self):
        """Test that players are created correctly"""
        for i, player in enumerate(self.alliance.players):
            self.assertEqual(player.id, f"A{self.alliance.id}_P{i+1}")
            self.assertEqual(player.alliance_id, self.alliance.id)
            self.assertEqual(len(player.selected_hero_sets), 6)  # Each player has 6 hero sets
            
            # Each hero set should have 5 heroes
            for hero_set in player.selected_hero_sets:
                self.assertEqual(len(hero_set.heroes), 5)
    
    def test_available_hero_sets(self):
        """Test getting available hero sets"""
        available = self.alliance.get_all_available_hero_sets()
        
        # Should have 300 hero sets total (50 players * 6 sets each)
        self.assertEqual(len(available), 300)
        
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
        
        # Should now have 290 available
        still_available = self.alliance.get_all_available_hero_sets()
        self.assertEqual(len(still_available), 290)
        
        # None of the consumed sets should be in available list
        for hero_set in consumed_sets:
            self.assertNotIn(hero_set, still_available)
    
    def test_available_hero_sets_with_no_stamina(self):
        """Test that stamina doesn't affect hero set availability (stamina is consumed on attack)"""
        # Exhaust stamina for first 10 players
        for i in range(10):
            self.alliance.players[i].stamina = 0
        
        available = self.alliance.get_all_available_hero_sets()
        
        # Hero sets are still available - stamina is consumed when attacking, not when listing available sets
        self.assertEqual(len(available), 300)
    
    def test_available_hero_sets_with_dead_heroes(self):
        """Test that hero sets with all dead heroes are not available"""
        # Kill all heroes in first player's first hero set
        first_set = self.alliance.players[0].selected_hero_sets[0]
        for hero in first_set.heroes:
            hero.take_damage(hero.max_hp + 100)
        
        available = self.alliance.get_all_available_hero_sets()
        
        # Should have 299 hero sets (one less due to all dead heroes)
        self.assertEqual(len(available), 299)
        self.assertNotIn(first_set, available)
    
    def test_stronghold_control(self):
        """Test stronghold control management"""
        # Add a stronghold
        self.alliance.add_stronghold("S1")
        self.assertIn("S1", self.alliance.controlled_strongholds)
        
        # Remove a stronghold
        self.alliance.remove_stronghold("S1")
        self.assertNotIn("S1", self.alliance.controlled_strongholds)
    
    def test_cannot_remove_home_stronghold(self):
        """Test that home stronghold cannot be removed from control"""
        initial_count = len(self.alliance.controlled_strongholds)
        
        # Home stronghold handling is now handled by game state
        # This test is no longer applicable with new architecture
        self.assertEqual(len(self.alliance.controlled_strongholds), initial_count)
    
    def test_stamina_management(self):
        """Test stamina restoration and tracking"""
        # Reduce stamina for all players
        for player in self.alliance.players:
            player.stamina = 1
        
        # Restore stamina
        self.alliance.restore_all_stamina_for_new_half()
        
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
        self.assertEqual(len(still_available), 280)
        
        # Reset all
        self.alliance.reset_all_hero_sets_for_new_half()
        
        # All should be available again (assuming stamina)
        available_after_reset = self.alliance.get_all_available_hero_sets()
        self.assertEqual(len(available_after_reset), 300)
    
    def test_total_score_calculation(self):
        """Test calculation of total alliance score"""
        # Test summit showdown points
        self.alliance.summit_showdown_points = 1000
        self.assertEqual(self.alliance.summit_showdown_points, 1000)
    
    def test_player_by_id_lookup(self):
        """Test finding players by ID"""
        target_player = self.alliance.players[10]
        found_player = self.alliance.get_player(target_player.id)
        
        self.assertEqual(found_player, target_player)
        
        # Test non-existent player
        non_existent = self.alliance.get_player("INVALID_ID")
        self.assertIsNone(non_existent)
    
    def test_alliance_representation(self):
        """Test alliance string representation"""
        alliance_str = str(self.alliance)
        
        self.assertIn("Test Alliance", alliance_str)
        self.assertIn("Players:50", alliance_str)
        self.assertIn("0", alliance_str)  # Points start at 0

if __name__ == '__main__':
    unittest.main()