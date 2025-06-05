# tests/test_scoring_system.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.game_state import GameState
from game_simulator.entities.hero_set import HeroSet
from game_simulator.entities.hero import Hero

class TestScoringSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_team_defeat_points_npc(self):
        """Test points awarded for defeating NPC teams"""
        alliance = self.game_state.get_alliance(1)
        stronghold = self.game_state.get_stronghold("S1-1")  # Level 1 stronghold
        
        initial_points = alliance.summit_showdown_points
        
        # Award team defeat points for NPC (first time gets bonus)
        self.game_state._award_team_defeat_points(alliance, stronghold, is_npc=True)
        
        # Should get 40 + 16 (40% bonus) = 56 points for first NPC defeat
        self.assertEqual(alliance.summit_showdown_points, initial_points + 56)
        
    def test_team_defeat_points_first_time_bonus(self):
        """Test first-time defeat bonus for NPC teams"""
        alliance = self.game_state.get_alliance(1)
        stronghold = self.game_state.get_stronghold("S2-9")  # Level 2 stronghold
        
        initial_points = alliance.summit_showdown_points
        
        # First defeat should get bonus
        self.game_state._award_team_defeat_points(alliance, stronghold, is_npc=True)
        expected_points = 60 + int(60 * 0.4)  # Base + 40% bonus = 84 points
        self.assertEqual(alliance.summit_showdown_points, initial_points + expected_points)
        
        # Second defeat should not get bonus
        alliance2 = self.game_state.get_alliance(2)
        initial_points2 = alliance2.summit_showdown_points
        self.game_state._award_team_defeat_points(alliance2, stronghold, is_npc=True)
        self.assertEqual(alliance2.summit_showdown_points, initial_points2 + 60)  # No bonus
        
    def test_capture_points_level_progression(self):
        """Test capture points for different stronghold levels"""
        alliance = self.game_state.get_alliance(1)
        
        # Test Level 1 stronghold capture (first time gets bonus)
        stronghold_l1 = self.game_state.get_stronghold("S1-1")
        initial_points = alliance.summit_showdown_points
        self.game_state._award_capture_points(alliance, stronghold_l1)
        # Should get 200 + 80 (40% bonus) = 280 points for first capture
        self.assertEqual(alliance.summit_showdown_points, initial_points + 280)
        
        # Test Level 2 stronghold capture (first time gets bonus)
        stronghold_l2 = self.game_state.get_stronghold("S2-9")
        initial_points = alliance.summit_showdown_points
        self.game_state._award_capture_points(alliance, stronghold_l2)
        # Should get 420 + 168 (40% bonus) = 588 points for first capture
        self.assertEqual(alliance.summit_showdown_points, initial_points + 588)
        
        # Test Level 3 stronghold capture (first time gets bonus)
        stronghold_l3 = self.game_state.get_stronghold("S3-10")
        initial_points = alliance.summit_showdown_points
        self.game_state._award_capture_points(alliance, stronghold_l3)
        # Should get 720 + 288 (40% bonus) = 1008 points for first capture
        self.assertEqual(alliance.summit_showdown_points, initial_points + 1008)
        
    def test_capture_points_first_time_bonus(self):
        """Test first-time capture bonus"""
        alliance1 = self.game_state.get_alliance(1)
        alliance2 = self.game_state.get_alliance(2)
        stronghold = self.game_state.get_stronghold("S3-10")  # Level 3
        
        # First capture should get bonus
        initial_points1 = alliance1.summit_showdown_points
        self.game_state._award_capture_points(alliance1, stronghold)
        expected_points = 720 + int(720 * 0.4)  # Base + 40% bonus = 1008 points
        self.assertEqual(alliance1.summit_showdown_points, initial_points1 + expected_points)
        
        # Simulate recapture - should not get first-time bonus
        initial_points2 = alliance2.summit_showdown_points
        self.game_state._award_capture_points(alliance2, stronghold)
        self.assertEqual(alliance2.summit_showdown_points, initial_points2 + 720)  # No bonus
        
    def test_garrison_defeat_points(self):
        """Test points for defeating player garrison teams"""
        alliance = self.game_state.get_alliance(1)
        stronghold = self.game_state.get_stronghold("S1-1")
        
        initial_points = alliance.summit_showdown_points
        
        # Award team defeat points for garrison
        self.game_state._award_team_defeat_points(alliance, stronghold, is_npc=False)
        
        # Should get 40 points for Level 1 stronghold garrison defeat (no first-time bonus for garrison)
        self.assertEqual(alliance.summit_showdown_points, initial_points + 40)

class TestCaptureLogic(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_stronghold_capture_by_most_defeats(self):
        """Test stronghold capture goes to alliance with most NPC defeats"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Simulate defeats by different alliances
        stronghold.npc_teams_defeated_by_alliance = {
            1: 3,  # Alliance 1 defeated 3 NPCs
            2: 5,  # Alliance 2 defeated 5 NPCs  
            3: 1   # Alliance 3 defeated 1 NPC
        }
        
        # Clear all NPCs to make it capturable
        stronghold.npc_defense_teams = []
        
        # Alliance 1 triggers capture, but Alliance 2 should get it
        capturing_alliance_id = stronghold.capture_by_alliance(1)
        
        self.assertEqual(capturing_alliance_id, 2)  # Alliance 2 had most defeats
        self.assertEqual(stronghold.controlling_alliance, 2)
        
    def test_stronghold_capture_tie_breaking(self):
        """Test tie-breaking in stronghold capture"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Simulate tie between alliances
        stronghold.npc_teams_defeated_by_alliance = {
            1: 4,  # Alliance 1 defeated 4 NPCs
            3: 4,  # Alliance 3 defeated 4 NPCs (tie)
            2: 2   # Alliance 2 defeated 2 NPCs
        }
        
        # Clear all NPCs to make it capturable
        stronghold.npc_defense_teams = []
        
        # Should go to alliance with lowest ID (simplified tie-breaking)
        capturing_alliance_id = stronghold.capture_by_alliance(3)
        
        self.assertEqual(capturing_alliance_id, 1)  # Alliance 1 wins tie (lower ID)
        self.assertEqual(stronghold.controlling_alliance, 1)
        
    def test_stronghold_not_capturable_with_npcs(self):
        """Test stronghold cannot be captured while NPCs remain"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Should have NPCs initially
        self.assertFalse(stronghold.check_capturable())
        
        # Try to capture - should fail
        capturing_alliance_id = stronghold.capture_by_alliance(1)
        self.assertIsNone(capturing_alliance_id)
        self.assertIsNone(stronghold.controlling_alliance)
        
    def test_stronghold_protection_after_capture(self):
        """Test stronghold gets 1-hour protection after capture"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Simulate successful capture conditions
        stronghold.npc_defense_teams = []  # No NPCs
        stronghold.npc_teams_defeated_by_alliance = {1: 5}
        
        # Capture with 60-minute protection
        capturing_alliance_id = stronghold.capture_by_alliance(1, protection_duration_minutes=60)
        
        self.assertEqual(capturing_alliance_id, 1)
        self.assertTrue(stronghold.is_protected)
        self.assertFalse(stronghold.can_be_attacked())

class TestDefenderRemoval(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        
    def test_defeated_npc_removal(self):
        """Test defeated NPCs are immediately removed"""
        stronghold = self.game_state.get_stronghold("S1-1")
        initial_count = len(stronghold.npc_defense_teams)
        
        # Defeat an NPC team
        defeated_npc = stronghold.npc_defense_teams[0]
        stronghold.remove_defeated_npc_team(defeated_npc, 1)
        
        # Should be removed from list
        self.assertEqual(len(stronghold.npc_defense_teams), initial_count - 1)
        self.assertNotIn(defeated_npc, stronghold.npc_defense_teams)
        
        # Should track the defeat
        self.assertEqual(stronghold.npc_teams_defeated_by_alliance[1], 1)
        
    def test_defeated_garrison_removal(self):
        """Test defeated garrison sets are removed by cleanup"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Add a garrison set
        heroes = [Hero(f"hero_{i}", is_npc=False) for i in range(5)]
        garrison_set = HeroSet("garrison_test", "player1", heroes)
        stronghold.add_garrison_set(garrison_set)
        
        self.assertEqual(len(stronghold.garrisoned_hero_sets), 1)
        
        # Kill all heroes in the garrison set
        for hero in garrison_set.heroes:
            hero.take_damage(hero.max_hp + 100)
        
        self.assertTrue(garrison_set.is_defeated())
        
        # Cleanup should remove defeated garrison
        stronghold.cleanup_defeated_defenders()
        
        self.assertEqual(len(stronghold.garrisoned_hero_sets), 0)
        self.assertNotIn(garrison_set, stronghold.garrisoned_hero_sets)
        
    def test_defending_sets_excludes_defeated(self):
        """Test get_all_defending_sets excludes defeated sets"""
        stronghold = self.game_state.get_stronghold("S1-1")
        
        # Add garrison with living heroes
        living_heroes = [Hero(f"living_{i}", is_npc=False) for i in range(5)]
        living_set = HeroSet("living_set", "player1", living_heroes)
        stronghold.add_garrison_set(living_set)
        
        # Add garrison with dead heroes
        dead_heroes = [Hero(f"dead_{i}", is_npc=False) for i in range(5)]
        dead_set = HeroSet("dead_set", "player2", dead_heroes)
        for hero in dead_heroes:
            hero.take_damage(hero.max_hp + 100)
        stronghold.add_garrison_set(dead_set)
        
        defending_sets = stronghold.get_all_defending_sets()
        
        # Should include NPCs + living garrison, but not dead garrison
        self.assertIn(living_set, defending_sets)
        self.assertNotIn(dead_set, defending_sets)
        
        # Should be 9 NPCs + 1 living garrison = 10 total
        self.assertEqual(len(defending_sets), 10)

if __name__ == '__main__':
    unittest.main()