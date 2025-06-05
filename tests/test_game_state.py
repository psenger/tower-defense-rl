# tests/test_game_state.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.game_state import GameState
from game_simulator.entities.summit_battle import SummitBattle
from game_simulator.entities.hero import Hero
from game_simulator.entities.hero_set import HeroSet

class TestGameState(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_initial_state(self):
        """Test that game state initializes correctly"""
        # Should have 23 strongholds (4 homes + 16 L1 + 2 L2 + 1 L3)
        self.assertEqual(len(self.game_state.strongholds), 23)
        
        # Should have 4 alliances
        self.assertEqual(len(self.game_state.alliances), 4)
        for i in range(1, 5):
            self.assertIn(i, self.game_state.alliances)
        
        # Game time should start at 0
        self.assertEqual(self.game_state.game_time, 0.0)
        
        # Should have no active battles initially
        self.assertEqual(len(self.game_state.active_battles), 0)
        
        # Should start in first half
        self.assertEqual(self.game_state.current_half, 1)
        
    def test_stronghold_retrieval(self):
        """Test that strongholds can be retrieved by ID"""
        stronghold = self.game_state.get_stronghold("T1")
        self.assertIsNotNone(stronghold)
        self.assertEqual(stronghold.id, "T1")
        self.assertTrue(stronghold.is_alliance_home)
        
        # Test level 3 stronghold
        l3_stronghold = self.game_state.get_stronghold("S3-10")
        self.assertIsNotNone(l3_stronghold)
        self.assertEqual(l3_stronghold.level, 3)
        
        # Test non-existent stronghold
        non_existent = self.game_state.get_stronghold("INVALID")
        self.assertIsNone(non_existent)
        
    def test_alliance_retrieval(self):
        """Test alliance retrieval and setup"""
        alliance = self.game_state.get_alliance(1)
        self.assertIsNotNone(alliance)
        self.assertEqual(alliance.id, 1)
        self.assertEqual(len(alliance.players), 50)
        self.assertEqual(alliance.home_stronghold, "T1")
        
        # Test alliance colors and names
        expected_names = ["Alliance Red", "Alliance Blue", "Alliance Green", "Alliance Yellow"]
        for i in range(1, 5):
            alliance = self.game_state.get_alliance(i)
            self.assertEqual(alliance.name, expected_names[i-1])
        
    def test_battle_management(self):
        """Test adding and removing battles"""
        # Get alliance and hero sets
        alliance = self.game_state.get_alliance(1)
        attacking_set = alliance.get_all_available_hero_sets()[0]
        
        # Get a stronghold with NPC teams
        stronghold = self.game_state.get_stronghold("S1-2")
        self.assertTrue(len(stronghold.get_active_npc_teams()) > 0)
        
        # Start a battle
        battle = self.game_state.start_battle(attacking_set, "S1-2")
        self.assertIsNotNone(battle)
        self.assertEqual(len(self.game_state.active_battles), 1)
        self.assertIn(battle, self.game_state.active_battles)
        
        # Battle is normally removed by update_battles when completed
        # Manually remove for testing
        self.game_state.active_battles.remove(battle)
        self.assertEqual(len(self.game_state.active_battles), 0)
        
    def test_initial_stronghold_setup(self):
        """Test initial stronghold setup"""
        # Alliance homes should be controlled
        for i in range(1, 5):
            home = self.game_state.get_stronghold(f"T{i}")
            self.assertEqual(home.controlling_alliance, i)
            self.assertTrue(home.is_alliance_home)
            self.assertEqual(len(home.npc_defense_teams), 0)  # Homes have no NPCs
        
        # Regular strongholds should be neutral with NPCs
        s1 = self.game_state.get_stronghold("S1-1")
        self.assertIsNone(s1.controlling_alliance)
        self.assertEqual(len(s1.npc_defense_teams), 9)  # Level 1 = 9 NPCs
        
        # Level 2 stronghold
        l2 = self.game_state.get_stronghold("S2-11")
        self.assertEqual(l2.level, 2)
        self.assertEqual(len(l2.npc_defense_teams), 12)  # Level 2 = 12 NPCs
        
        # Level 3 stronghold
        l3 = self.game_state.get_stronghold("S3-10")
        self.assertEqual(l3.level, 3)
        self.assertEqual(len(l3.npc_defense_teams), 15)  # Level 3 = 15 NPCs
        
    def test_stronghold_connections(self):
        """Test that stronghold connections are set up correctly"""
        # Test alliance home connections
        team1 = self.game_state.get_stronghold("T1")
        self.assertIn("S1-2", team1.connections)
        
        # Test L3 connections (should connect to level 2 strongholds)
        l3 = self.game_state.get_stronghold("S3-10")
        self.assertIn("S2-9", l3.connections)
        self.assertIn("S2-11", l3.connections)
        
    def test_game_status(self):
        """Test game status reporting"""
        status = self.game_state.get_game_status()
        
        self.assertIn("half", status)
        self.assertIn("game_time", status)
        self.assertIn("active_battles", status)
        self.assertIn("alliance_scores", status)
        self.assertIn("stronghold_control", status)
        
        self.assertEqual(status["half"], 1)
        self.assertEqual(status["game_time"], 0.0)
        self.assertEqual(status["active_battles"], 0)
        
    def test_second_half_transition(self):
        """Test transition to second half"""
        # Advance to second half
        self.game_state.advance_to_second_half()
        
        self.assertEqual(self.game_state.current_half, 2)
        
        # All players should have restored stamina
        for alliance in self.game_state.alliances.values():
            for player in alliance.players:
                self.assertEqual(player.stamina, 4)
                
        # All hero sets should be available for attack
        for alliance in self.game_state.alliances.values():
            for player in alliance.players:
                for hero_set in player.selected_hero_sets:
                    self.assertFalse(hero_set.consumed_for_attack)
        
    def test_state_serialization(self):
        """Test that game state can be serialized to dict"""
        state_dict = self.game_state.to_dict()
        
        self.assertIn("game_time", state_dict)
        self.assertIn("current_half", state_dict)
        self.assertIn("alliance_scores", state_dict)
        self.assertIn("stronghold_control", state_dict)
        self.assertIn("active_battles", state_dict)
        
        self.assertEqual(state_dict["game_time"], 0.0)
        self.assertEqual(state_dict["current_half"], 1)

if __name__ == '__main__':
    unittest.main()