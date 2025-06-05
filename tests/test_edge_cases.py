# tests/test_edge_cases.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.game_state import GameState
from game_simulator.entities.hero_set import HeroSet
from game_simulator.entities.hero import Hero
from game_simulator.entities.summit_battle import SummitBattle

class TestMultiAllianceCapture(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_complex_multi_alliance_stronghold_battle(self):
        """Test complex scenario where multiple alliances attack same stronghold"""
        stronghold = self.game_state.get_stronghold("S3-10")  # Level 3 with 15 NPCs
        
        # Simulate multiple alliances defeating NPCs
        # Alliance 1 defeats 6 NPCs
        for i in range(6):
            npc = stronghold.npc_defense_teams[i]
            stronghold.remove_defeated_npc_team(npc, 1)
            
        # Alliance 2 defeats 5 NPCs  
        remaining_npcs = stronghold.get_active_npc_teams()
        for i in range(5):
            npc = remaining_npcs[i]
            stronghold.remove_defeated_npc_team(npc, 2)
            
        # Alliance 3 defeats 4 NPCs
        remaining_npcs = stronghold.get_active_npc_teams()
        for i in range(4):
            npc = remaining_npcs[i]
            stronghold.remove_defeated_npc_team(npc, 3)
        
        # Verify defeat tracking
        self.assertEqual(stronghold.npc_teams_defeated_by_alliance[1], 6)
        self.assertEqual(stronghold.npc_teams_defeated_by_alliance[2], 5)
        self.assertEqual(stronghold.npc_teams_defeated_by_alliance[3], 4)
        self.assertEqual(len(stronghold.get_active_npc_teams()), 0)  # All defeated
        
        # Alliance 3 triggers capture attempt, but Alliance 1 should get it
        capturing_alliance_id = stronghold.capture_by_alliance(3)
        
        self.assertEqual(capturing_alliance_id, 1)  # Alliance 1 had most defeats
        self.assertEqual(stronghold.controlling_alliance, 1)
        
        # Verify tracking is cleared after capture
        self.assertEqual(stronghold.npc_teams_defeated_by_alliance, {})
        
    def test_perfect_tie_capture_scenario(self):
        """Test capture when alliances are perfectly tied"""
        stronghold = self.game_state.get_stronghold("S1-1")  # Level 1 with 9 NPCs
        
        # Alliance 2 and 4 each defeat 4 NPCs, Alliance 1 defeats 1
        for i in range(4):
            npc = stronghold.npc_defense_teams[i]
            stronghold.remove_defeated_npc_team(npc, 2)
            
        remaining_npcs = stronghold.get_active_npc_teams()
        for i in range(4):
            npc = remaining_npcs[i]
            stronghold.remove_defeated_npc_team(npc, 4)
            
        # Alliance 1 defeats the last one
        final_npc = stronghold.get_active_npc_teams()[0]
        stronghold.remove_defeated_npc_team(final_npc, 1)
        
        # Tie between Alliance 2 and 4 (both have 4 defeats)
        self.assertEqual(stronghold.npc_teams_defeated_by_alliance[2], 4)
        self.assertEqual(stronghold.npc_teams_defeated_by_alliance[4], 4)
        self.assertEqual(stronghold.npc_teams_defeated_by_alliance[1], 1)
        
        # Alliance 1 triggers capture, but Alliance 2 should win tie (lower ID)
        capturing_alliance_id = stronghold.capture_by_alliance(1)
        
        self.assertEqual(capturing_alliance_id, 2)  # Alliance 2 wins tie
        
    def test_no_defeats_recorded_capture_failure(self):
        """Test capture fails when no defeats are recorded"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Manually clear NPCs without recording defeats
        stronghold.npc_defense_teams = []
        
        # Should be capturable but have no defeat records
        self.assertTrue(stronghold.check_capturable())
        
        # Capture should fail due to no recorded defeats
        capturing_alliance_id = stronghold.capture_by_alliance(1)
        self.assertIsNone(capturing_alliance_id)
        self.assertIsNone(stronghold.controlling_alliance)

class TestProtectionAndCooling(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_extended_protection_period(self):
        """Test new 1-hour protection period"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Start protection with 60 minutes
        stronghold.start_protection(60)
        
        self.assertTrue(stronghold.is_protected)
        self.assertFalse(stronghold.can_be_attacked())
        
        # Protection should last for full hour
        # (In real implementation, this would be tested with time manipulation)
        
    def test_protection_prevents_all_attacks(self):
        """Test protection prevents attacks from all alliances"""
        stronghold = self.game_state.get_stronghold("S1-1")
        stronghold.start_protection(60)
        
        # No alliance should be able to attack
        for alliance_id in [1, 2, 3, 4]:
            self.assertFalse(self.game_state.can_alliance_attack_stronghold(alliance_id, "S1-1"))
            
    def test_protection_removal_on_second_half(self):
        """Test all protection is removed at start of second half"""
        strongholds_to_protect = ["S1-1", "S1-2", "S2-9"]
        
        # Apply protection to multiple strongholds
        for stronghold_id in strongholds_to_protect:
            stronghold = self.game_state.get_stronghold(stronghold_id)
            stronghold.start_protection(60)
            self.assertTrue(stronghold.is_protected)
        
        # Advance to second half
        self.game_state.advance_to_second_half()
        
        # All protection should be removed
        for stronghold_id in strongholds_to_protect:
            stronghold = self.game_state.get_stronghold(stronghold_id)
            self.assertFalse(stronghold.is_protected)
            self.assertTrue(stronghold.can_be_attacked())

class TestComplexBattleScenarios(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_simultaneous_battle_resolution(self):
        """Test multiple battles resolving simultaneously"""
        # Create multiple battles
        alliance1 = self.game_state.get_alliance(1)
        alliance2 = self.game_state.get_alliance(2)
        
        attacking_set1 = alliance1.get_all_available_hero_sets()[0]
        attacking_set2 = alliance2.get_all_available_hero_sets()[0]
        
        # Start battles at different strongholds
        battle1 = self.game_state.start_battle(attacking_set1, "S1-2")
        battle2 = self.game_state.start_battle(attacking_set2, "S1-5")
        
        self.assertEqual(len(self.game_state.active_battles), 2)
        
        # Both battles should be tracked
        self.assertIn(battle1, self.game_state.active_battles)
        self.assertIn(battle2, self.game_state.active_battles)
        
    def test_garrison_vs_garrison_battle(self):
        """Test battle mechanics with garrison defenders"""
        stronghold = self.game_state.get_stronghold("S1-3")
        
        # Clear NPCs and capture by alliance 1  
        stronghold.npc_defense_teams = []
        stronghold.npc_teams_defeated_by_alliance = {1: 9}
        capturing_alliance_id = stronghold.capture_by_alliance(1)
        self.assertEqual(capturing_alliance_id, 1)
        
        # Remove protection so it can be attacked
        stronghold.is_protected = False
        stronghold.protection_end_time = 0
        
        # Add stronghold to alliance 1's control
        alliance1 = self.game_state.get_alliance(1)
        alliance1.add_stronghold("S1-3")
        
        # Add garrison from alliance 1
        heroes1 = [Hero(f"garrison1_{i}", is_npc=False) for i in range(5)]
        garrison_set1 = HeroSet("garrison1", "player1", heroes1)
        stronghold.add_garrison_set(garrison_set1)
        
        # Verify garrison is set up correctly
        self.assertEqual(len(stronghold.garrisoned_hero_sets), 1)
        defending_sets = stronghold.get_all_defending_sets()
        self.assertEqual(len(defending_sets), 1)  # Only garrison, no NPCs
        self.assertIn(garrison_set1, defending_sets)
        self.assertFalse(defending_sets[0].is_npc)  # Should be player garrison
        
    def test_empty_stronghold_after_garrison_defeat(self):
        """Test stronghold state after all defenders are defeated"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Clear NPCs and capture
        stronghold.npc_defense_teams = []
        stronghold.npc_teams_defeated_by_alliance = {1: 9}
        stronghold.capture_by_alliance(1)
        
        # Add garrison
        heroes = [Hero(f"garrison_{i}", is_npc=False) for i in range(5)]
        garrison_set = HeroSet("garrison_test", "player1", heroes)
        stronghold.add_garrison_set(garrison_set)
        
        # Kill all garrison heroes
        for hero in garrison_set.heroes:
            hero.take_damage(hero.max_hp + 100)
        
        # Cleanup defeated defenders
        stronghold.cleanup_defeated_defenders()
        
        # Stronghold should remain controlled (can't become neutral after capture)
        self.assertEqual(stronghold.controlling_alliance, 1)
        self.assertEqual(len(stronghold.garrisoned_hero_sets), 0)
        self.assertEqual(len(stronghold.get_all_defending_sets()), 0)

class TestStaminaAndResourceManagement(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_hero_set_consumption_across_halves(self):
        """Test hero set consumption resets between halves"""
        alliance = self.game_state.get_alliance(1)
        available_sets = alliance.get_all_available_hero_sets()
        
        # Consume some hero sets
        for i in range(10):
            available_sets[i].mark_consumed_for_attack()
        
        remaining = alliance.get_all_available_hero_sets()
        self.assertEqual(len(remaining), 300 - 10)  # 290 remaining
        
        # Advance to second half
        self.game_state.advance_to_second_half()
        
        # All hero sets should be available again
        available_after_reset = alliance.get_all_available_hero_sets()
        self.assertEqual(len(available_after_reset), 300)  # All 300 available
        
    def test_stamina_restoration_second_half(self):
        """Test stamina restoration at second half"""
        alliance = self.game_state.get_alliance(1)
        
        # Exhaust stamina for some players
        for i in range(10):
            alliance.players[i].stamina = 0
        
        # Advance to second half
        self.game_state.advance_to_second_half()
        
        # All players should have 4 stamina again
        for player in alliance.players:
            self.assertEqual(player.stamina, 4)
            
    def test_npc_respawn_in_neutral_strongholds(self):
        """Test NPCs respawn in neutral strongholds at second half"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Remove some NPCs but don't capture stronghold
        for i in range(5):
            npc = stronghold.npc_defense_teams[i]
            stronghold.remove_defeated_npc_team(npc, 1)
        
        self.assertEqual(len(stronghold.get_active_npc_teams()), 4)
        self.assertTrue(stronghold.is_neutral())  # Still neutral
        
        # Advance to second half
        self.game_state.advance_to_second_half()
        
        # NPCs should respawn in neutral strongholds
        self.assertEqual(len(stronghold.get_active_npc_teams()), 9)  # Full complement
        
    def test_no_npc_respawn_in_controlled_strongholds(self):
        """Test NPCs don't respawn in controlled strongholds"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Clear all NPCs and capture
        stronghold.npc_defense_teams = []
        stronghold.npc_teams_defeated_by_alliance = {1: 9}
        stronghold.capture_by_alliance(1)
        
        self.assertEqual(len(stronghold.get_active_npc_teams()), 0)
        self.assertFalse(stronghold.is_neutral())
        
        # Advance to second half
        self.game_state.advance_to_second_half()
        
        # NPCs should NOT respawn in controlled strongholds
        self.assertEqual(len(stronghold.get_active_npc_teams()), 0)

if __name__ == '__main__':
    unittest.main()