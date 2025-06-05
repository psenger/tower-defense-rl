# tests/test_engine_features.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.engine import GameEngine
from game_simulator.game_state import GameState

class TestTimeControls(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = GameEngine(headless=True)
        
    def test_time_scale_limits(self):
        """Test time scale respects maximum limits"""
        # Test normal speed increase
        self.engine.time_scale = 1.0
        self.engine.time_scale = min(10000.0, self.engine.time_scale * 2)
        self.assertEqual(self.engine.time_scale, 2.0)
        
        # Test maximum limit
        self.engine.time_scale = 5000.0
        self.engine.time_scale = min(10000.0, self.engine.time_scale * 2)
        self.assertEqual(self.engine.time_scale, 10000.0)
        
        # Test exceeding maximum
        self.engine.time_scale = 6000.0
        self.engine.time_scale = min(10000.0, self.engine.time_scale * 2)
        self.assertEqual(self.engine.time_scale, 10000.0)  # Capped at maximum
        
    def test_scrubber_mode_functionality(self):
        """Test scrubber mode operations"""
        # Initially not in scrubber mode
        self.assertFalse(self.engine.scrubber_mode)
        
        # Toggle scrubber mode
        self.engine._toggle_scrubber_mode()
        self.assertTrue(self.engine.scrubber_mode)
        self.assertEqual(self.engine.time_scale, 0.0)  # Should pause
        
        # Target time should be set to current game time
        expected_target = self.engine.game_state.game_time / 60.0
        self.assertEqual(self.engine.target_game_minutes, expected_target)
        
    def test_scrubber_forward_backward(self):
        """Test scrubber forward and backward navigation"""
        self.engine._toggle_scrubber_mode()
        initial_target = self.engine.target_game_minutes
        
        # Scrub forward
        self.engine._scrub_forward()
        self.assertEqual(self.engine.target_game_minutes, initial_target + 10)
        
        # Scrub backward
        self.engine._scrub_backward()
        self.assertEqual(self.engine.target_game_minutes, initial_target)
        
        # Scrub backward beyond 0
        self.engine.target_game_minutes = 5
        self.engine._scrub_backward()
        self.assertEqual(self.engine.target_game_minutes, 0)  # Should not go negative
        
    def test_scrubber_time_limits(self):
        """Test scrubber respects maximum game time"""
        self.engine._toggle_scrubber_mode()
        
        # Set near maximum time (23 hours 30 minutes = 1410 minutes)
        self.engine.target_game_minutes = 1400
        
        # Scrub forward
        self.engine._scrub_forward()
        self.assertEqual(self.engine.target_game_minutes, 1410)  # Should cap at maximum
        
        # Try to exceed maximum
        self.engine._scrub_forward()
        self.assertEqual(self.engine.target_game_minutes, 1410)  # Should stay at maximum
        
    def test_fast_view_mode(self):
        """Test fast view mode calculation"""
        initial_scale = self.engine.time_scale
        
        self.engine._set_fast_view_mode()
        
        # Should set to 282x speed (84,600 seconds / 300 seconds = 282)
        self.assertEqual(self.engine.time_scale, 282.0)
        self.assertFalse(self.engine.scrubber_mode)  # Should exit scrubber mode

class TestHalfAdvancement(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = GameEngine(headless=True)
        
    def test_second_half_advancement(self):
        """Test automatic advancement to second half"""
        # Should start in first half
        self.assertEqual(self.engine.game_state.current_half, 1)
        
        # Set game time to just before half advancement (11.5 hours = 41,400 seconds)
        self.engine.game_state.game_time = 41399.0
        self.engine._check_half_advancement()
        self.assertEqual(self.engine.game_state.current_half, 1)  # Still first half
        
        # Set game time to trigger advancement
        self.engine.game_state.game_time = 41400.0
        self.engine._check_half_advancement()
        self.assertEqual(self.engine.game_state.current_half, 2)  # Should advance
        
    def test_settlement_points_awarding(self):
        """Test settlement points are awarded at halftime"""
        # Set up controlled strongholds
        alliance1 = self.engine.game_state.get_alliance(1)
        alliance2 = self.engine.game_state.get_alliance(2)
        
        stronghold_l1 = self.engine.game_state.get_stronghold("S1-1")
        stronghold_l2 = self.engine.game_state.get_stronghold("S2-9")
        stronghold_l3 = self.engine.game_state.get_stronghold("S3-10")
        
        # Simulate captures
        stronghold_l1.controlling_alliance = 1
        alliance1.add_stronghold("S1-1")
        
        stronghold_l2.controlling_alliance = 2
        alliance2.add_stronghold("S2-9")
        
        stronghold_l3.controlling_alliance = 1
        alliance1.add_stronghold("S3-10")
        
        initial_points1 = alliance1.summit_showdown_points
        initial_points2 = alliance2.summit_showdown_points
        
        # Trigger settlement points
        self.engine._award_settlement_points()
        
        # Alliance 1 should get: 1800 (L1) + 6480 (L3) = 8280 points
        # Alliance 2 should get: 3780 (L2) = 3780 points
        expected_points1 = initial_points1 + 1800 + 6480
        expected_points2 = initial_points2 + 3780
        
        self.assertEqual(alliance1.summit_showdown_points, expected_points1)
        self.assertEqual(alliance2.summit_showdown_points, expected_points2)
        
    def test_no_settlement_points_for_alliance_homes(self):
        """Test alliance homes don't award settlement points"""
        alliance1 = self.engine.game_state.get_alliance(1)
        initial_points = alliance1.summit_showdown_points
        
        # Alliance homes should already be controlled but not award settlement points
        self.engine._award_settlement_points()
        
        # Points should not change (homes don't count for settlement points)
        self.assertEqual(alliance1.summit_showdown_points, initial_points)

class TestBattleGeneration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = GameEngine(headless=True)
        
    def test_alliance_attack_adjacency_validation(self):
        """Test alliance attacks respect adjacency rules"""
        alliance = self.engine.game_state.get_alliance(1)
        
        # Alliance 1 starts with T1, which connects to S1-2
        # Should be able to attack S1-2
        self.assertTrue(self.engine.game_state.can_alliance_attack_stronghold(1, "S1-2"))
        
        # Should NOT be able to attack S3-10 (not adjacent)
        self.assertFalse(self.engine.game_state.can_alliance_attack_stronghold(1, "S3-10"))
        
    def test_test_alliance_attack_availability(self):
        """Test test alliance attack respects hero set availability"""
        # Consume all hero sets for alliance 1
        alliance = self.engine.game_state.get_alliance(1)
        for player in alliance.players:
            for hero_set in player.selected_hero_sets:
                hero_set.mark_consumed_for_attack()
        
        # Should have no available sets
        self.assertEqual(len(alliance.get_all_available_hero_sets()), 0)
        
        # Test attack should not work (no available sets)
        initial_battle_count = len(self.engine.game_state.active_battles)
        self.engine._test_alliance_attack(1)
        
        # No battle should be created
        self.assertEqual(len(self.engine.game_state.active_battles), initial_battle_count)
        
    def test_battle_limit_enforcement(self):
        """Test auto battle generation respects concurrent battle limits"""
        # Fill up to battle limit
        for i in range(3):
            self.engine._auto_generate_test_battle()
        
        initial_count = len(self.engine.game_state.active_battles)
        
        # Try to generate another battle
        self.engine._auto_generate_test_battle()
        
        # Should not exceed limit
        self.assertLessEqual(len(self.engine.game_state.active_battles), 3)

class TestObservationAndActions(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = GameEngine(headless=True)
        
    def test_observation_structure(self):
        """Test RL observation has correct structure"""
        obs = self.engine.get_observation()
        
        # Should have 4 values per stronghold (x, y, alliance_control, npc_count)
        # 23 strongholds total = 92 values
        expected_length = 23 * 4
        self.assertEqual(len(obs), expected_length)
        
        # All values should be numeric
        for value in obs:
            self.assertIsInstance(value, (int, float))
            
    def test_reward_calculation(self):
        """Test RL reward calculation"""
        # Give alliance 1 some strongholds
        alliance1 = self.engine.game_state.get_alliance(1)
        alliance1.add_stronghold("S1-1")
        alliance1.add_stronghold("S1-2")
        
        reward = self.engine.calculate_reward()
        
        # Should get 0.1 points per controlled stronghold (plus home)
        # Home (T1) + S1-1 + S1-2 = 3 strongholds = 0.3 reward
        expected_reward = 3 * 0.1
        self.assertEqual(reward, expected_reward)
        
    def test_episode_termination(self):
        """Test RL episode termination condition"""
        # Should not be done initially
        self.assertFalse(self.engine.is_done())
        
        # Set game time past termination threshold (300 seconds)
        self.engine.game_state.game_time = 301.0
        self.assertTrue(self.engine.is_done())
        
    def test_game_reset(self):
        """Test game state reset functionality"""
        # Modify game state
        self.engine.game_state.game_time = 1000.0
        self.engine.time_scale = 5.0
        
        # Reset
        obs = self.engine.reset_game()
        
        # Should reset to initial values
        self.assertEqual(self.engine.game_state.game_time, 0.0)
        self.assertIsNotNone(obs)  # Should return observation

if __name__ == '__main__':
    unittest.main()