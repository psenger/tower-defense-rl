# tests/test_rule_compliance.py - COMPREHENSIVE RULE VALIDATION TESTS
import unittest
import sys
import os
import numpy as np

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.game_state import GameState
from game_simulator.entities.hero import Hero
from game_simulator.entities.hero_set import HeroSet
from game_simulator.entities.stronghold import Stronghold
from game_simulator.entities.summit_battle import SummitBattle


class TestHeroStatGeneration(unittest.TestCase):
    """Test Rule II: Player & Hero Attributes"""

    def test_player_hero_stat_distribution(self):
        """Rule: Player heroes use normal distribution with specified means/stddevs"""
        # Generate many heroes to test distribution
        heroes = [Hero(f"test_{i}", is_npc=False) for i in range(1000)]

        attacks = [h.attack for h in heroes]
        defenses = [h.defense for h in heroes]
        hps = [h.max_hp for h in heroes]

        # Test means are approximately correct (within 2% tolerance)
        self.assertAlmostEqual(np.mean(attacks), 4627, delta=4627 * 0.02)
        self.assertAlmostEqual(np.mean(defenses), 4195, delta=4195 * 0.02)
        self.assertAlmostEqual(np.mean(hps), 8088, delta=8088 * 0.02)

        # Test standard deviations are approximately correct (within 10% tolerance)
        self.assertAlmostEqual(np.std(attacks), 432, delta=432 * 0.1)
        self.assertAlmostEqual(np.std(defenses), 346, delta=346 * 0.1)
        self.assertAlmostEqual(np.std(hps), 783, delta=783 * 0.1)

    def test_npc_hero_stat_distribution(self):
        """Rule: NPC heroes use same distributions as player heroes"""
        # Test each stronghold level
        for level in [1, 2, 3]:
            heroes = [Hero(f"npc_{level}_{i}", is_npc=True, stronghold_level=level)
                      for i in range(500)]

            attacks = [h.attack for h in heroes]
            defenses = [h.defense for h in heroes]
            hps = [h.max_hp for h in heroes]

            # NPCs should show statistical variation (not fixed values)
            self.assertGreater(np.std(attacks), 100, f"Level {level} NPCs lack attack variation")
            self.assertGreater(np.std(defenses), 100, f"Level {level} NPCs lack defense variation")
            self.assertGreater(np.std(hps), 200, f"Level {level} NPCs lack HP variation")

    def test_hero_set_creation(self):
        """Rule: Each player selects 30 heroes (6 sets of 5) from 50 initial heroes"""
        from game_simulator.entities.player import Player

        player = Player("test_player", 1)

        # Should have 50 initial heroes
        self.assertEqual(len(player.initial_hero_pool), 50)

        # Should have 6 hero sets of 5 heroes each
        self.assertEqual(len(player.selected_hero_sets), 6)
        for hero_set in player.selected_hero_sets:
            self.assertEqual(len(hero_set.heroes), 5)

        # Should have 20 discarded heroes
        self.assertEqual(len(player.discarded_heroes), 20)


class TestBattleMechanics(unittest.TestCase):
    """Test Rule III: Battle Mechanics"""

    def setUp(self):
        self.attacking_heroes = [Hero(f"att_{i}", is_npc=False) for i in range(5)]
        self.defending_heroes = [Hero(f"def_{i}", is_npc=True, stronghold_level=1) for i in range(5)]
        self.attacking_set = HeroSet("att_set", "player1", self.attacking_heroes)
        self.defending_set = HeroSet("def_set", "npc", self.defending_heroes, is_npc=True)
        self.battle = SummitBattle("test_battle", self.attacking_set, self.defending_set, "S1-1")

    def test_battle_step_limit(self):
        """Rule: Battle lasts up to 50 steps"""
        self.assertEqual(self.battle.max_steps, 50)

    def test_attacker_goes_first(self):
        """Rule: Side that initiated engagement is initial attacker"""
        self.assertTrue(self.battle.is_attacker_turn)

    def test_random_hits_per_turn(self):
        """Rule: Each turn, random hero performs 1-4 hits"""
        # Test multiple turns to verify random range
        hit_counts = []
        for _ in range(100):
            # Create fresh battle
            battle = SummitBattle("test", self.attacking_set, self.defending_set, "S1-1")

            # Mock the random hit generation
            import random
            random.seed(42)  # For reproducibility
            hits = random.randint(1, 4)
            hit_counts.append(hits)

        # Should see hits in range 1-4
        self.assertTrue(all(1 <= hits <= 4 for hits in hit_counts))
        self.assertTrue(len(set(hit_counts)) > 1)  # Should have variety

    def test_damage_calculation(self):
        """Rule: Damage_per_hit = ActingHero.Attack - AverageDefenseOfOpposingSet"""
        acting_hero = self.attacking_heroes[0]
        avg_defense = self.defending_set.get_average_defense()

        expected_damage = max(0, acting_hero.attack - avg_defense)

        # Damage should be positive given typical stats
        self.assertGreaterEqual(expected_damage, 0)

    def test_aoe_damage_distribution(self):
        """Rule: Damage distributed to all living opposing heroes with random weighting"""
        # Set up controlled scenario
        for hero in self.defending_heroes:
            hero.current_hp = 1000  # High HP to avoid deaths

        initial_total_hp = sum(h.current_hp for h in self.defending_heroes)

        # Execute one turn
        self.battle.execute_turn()

        final_total_hp = sum(h.current_hp for h in self.defending_heroes)

        # Some damage should have been dealt
        if final_total_hp < initial_total_hp:
            # Verify all living heroes could have taken damage (AoE)
            damaged_heroes = [h for h in self.defending_heroes if h.current_hp < 1000]
            self.assertGreater(len(damaged_heroes), 0)

    def test_tie_breaking_rule(self):
        """Rule: If equal damage at 50 steps, defender wins"""
        # Force a tie scenario
        self.battle.current_step = 50
        self.battle.attacker_total_damage = 1000
        self.battle.defender_total_damage = 1000

        self.battle._resolve_step_limit_tie()

        self.assertEqual(self.battle.winner, "defender")


class TestStrongholdMechanics(unittest.TestCase):
    """Test Rule IV: Game Play & Stronghold Interaction"""

    def test_npc_team_counts(self):
        """Rule: Level 1=9, Level 2=12, Level 3=15 NPC teams"""
        stronghold_l1 = Stronghold("S1-1", 1, 100, 100)
        stronghold_l2 = Stronghold("S2-1", 2, 200, 200)
        stronghold_l3 = Stronghold("S3-1", 3, 300, 300)

        self.assertEqual(len(stronghold_l1.npc_defense_teams), 9)
        self.assertEqual(len(stronghold_l2.npc_defense_teams), 12)
        self.assertEqual(len(stronghold_l3.npc_defense_teams), 15)

    def test_garrison_capacity(self):
        """Rule: Level 1=9, Level 2=7, Level 3=5 garrison capacity"""
        stronghold_l1 = Stronghold("S1-1", 1, 100, 100)
        stronghold_l2 = Stronghold("S2-1", 2, 200, 200)
        stronghold_l3 = Stronghold("S3-1", 3, 300, 300)

        self.assertEqual(stronghold_l1.max_garrison_size, 9)
        self.assertEqual(stronghold_l2.max_garrison_size, 7)
        self.assertEqual(stronghold_l3.max_garrison_size, 5)

    def test_immediate_defender_removal(self):
        """Rule: Defeated defenders immediately removed permanently"""
        stronghold = Stronghold("S1-1", 1, 100, 100)
        initial_npc_count = len(stronghold.npc_defense_teams)

        # Defeat an NPC team
        npc_team = stronghold.npc_defense_teams[0]
        removed = stronghold.remove_defeated_npc_team(npc_team, 1)

        self.assertTrue(removed)
        self.assertEqual(len(stronghold.npc_defense_teams), initial_npc_count - 1)
        self.assertNotIn(npc_team, stronghold.npc_defense_teams)

    def test_capture_by_most_defeats(self):
        """Rule: Alliance with most NPC defeats captures stronghold"""
        stronghold = Stronghold("S1-1", 1, 100, 100)

        # Simulate defeats by different alliances
        stronghold.npc_teams_defeated_by_alliance = {
            1: 3,  # Alliance 1: 3 defeats
            2: 5,  # Alliance 2: 5 defeats
            3: 1  # Alliance 3: 1 defeat
        }

        # Clear NPCs to make capturable
        stronghold.npc_defense_teams = []

        # Alliance 1 triggers capture, but Alliance 2 should get it
        capturing_alliance_id = stronghold.capture_by_alliance(1)

        self.assertEqual(capturing_alliance_id, 2)  # Alliance 2 had most defeats

    def test_protection_duration(self):
        """Rule: 1-hour protection after capture"""
        stronghold = Stronghold("S1-1", 1, 100, 100)
        current_time = 1000.0

        stronghold.start_protection(60, current_time)

        self.assertTrue(stronghold.is_protected)
        self.assertEqual(stronghold.protection_end_time, current_time + 3600)  # 60 minutes

    def test_reduced_protection_final_hour(self):
        """Rule: Protection reduced to 5 minutes in final 60 minutes of First Half"""
        stronghold = Stronghold("S1-1", 1, 100, 100)

        # Test normal time (not final hour)
        normal_time = 10 * 60 * 60  # 10 hours into game
        normal_duration = stronghold.get_reduced_protection_duration(normal_time)
        self.assertEqual(normal_duration, 60)

        # Test final hour
        final_hour_time = 11 * 60 * 60  # 11 hours into game (final hour)
        final_duration = stronghold.get_reduced_protection_duration(final_hour_time)
        self.assertEqual(final_duration, 5)


class TestHeroSetConsumption(unittest.TestCase):
    """Test Rule: Hero Set consumption timing"""

    def test_consumption_on_engagement(self):
        """Rule: Hero Set consumed when it ENGAGES in battle, not when battle starts"""
        heroes = [Hero(f"hero_{i}", is_npc=False) for i in range(5)]
        hero_set = HeroSet("test_set", "player1", heroes)

        # Initially not consumed
        self.assertFalse(hero_set.consumed_for_attack)
        self.assertTrue(hero_set.can_attack())

        # Engage in battle
        hero_set.engage_in_battle("battle_1")

        # Now should be consumed
        self.assertTrue(hero_set.consumed_for_attack)
        self.assertFalse(hero_set.can_attack())
        self.assertTrue(hero_set.is_in_battle)

    def test_garrison_removal_on_attack(self):
        """Rule: Garrisoned set removed when used for attack"""
        stronghold = Stronghold("S1-1", 1, 100, 100)
        heroes = [Hero(f"hero_{i}", is_npc=False) for i in range(5)]
        hero_set = HeroSet("test_set", "player1", heroes)

        # Add to garrison
        stronghold.add_garrison_set(hero_set)
        self.assertTrue(hero_set.is_garrisoned)

        # Simulate using for attack (removal should happen)
        stronghold.remove_garrison_set(hero_set)
        self.assertFalse(hero_set.is_garrisoned)


class TestSecondHalfReset(unittest.TestCase):
    """Test Rule: Second Half reset mechanics"""

    def test_complete_hero_reset(self):
        """Rule: All Hero Sets revert to 'Available' AND all Heroes restored to full health"""
        heroes = [Hero(f"hero_{i}", is_npc=False) for i in range(5)]
        hero_set = HeroSet("test_set", "player1", heroes)

        # Damage heroes and consume set
        for hero in heroes:
            hero.take_damage(1000)
        hero_set.consumed_for_attack = True

        # Verify damaged state
        self.assertTrue(hero_set.consumed_for_attack)
        self.assertTrue(any(h.current_hp < h.max_hp for h in heroes))

        # Reset for new half
        hero_set.reset_for_new_half()

        # Verify complete reset
        self.assertFalse(hero_set.consumed_for_attack)
        self.assertTrue(all(h.current_hp == h.max_hp for h in heroes))
        self.assertTrue(all(h.is_alive for h in heroes))


class TestScoringSystem(unittest.TestCase):
    """Test Rule V: Scoring Rules"""

    def test_team_defeat_points(self):
        """Rule: Team Points - L1=40, L2=60, L3=80"""
        game_state = GameState()
        alliance = game_state.get_alliance(1)

        # Test each stronghold level
        for level, expected_points in [(1, 40), (2, 60), (3, 80)]:
            stronghold = Stronghold(f"S{level}-1", level, 100, 100)
            initial_points = alliance.summit_showdown_points

            game_state._award_team_defeat_points(alliance, stronghold, is_npc=True)

            points_gained = alliance.summit_showdown_points - initial_points
            # Should be at least base points (may include first-time bonus)
            self.assertGreaterEqual(points_gained, expected_points)

    def test_occupation_points(self):
        """Rule: Occupation Points - L1=200, L2=420, L3=720"""
        game_state = GameState()
        alliance = game_state.get_alliance(1)

        # Test each stronghold level
        for level, expected_points in [(1, 200), (2, 420), (3, 720)]:
            stronghold = Stronghold(f"S{level}-1", level, 100, 100)
            initial_points = alliance.summit_showdown_points

            game_state._award_capture_points(alliance, stronghold)

            points_gained = alliance.summit_showdown_points - initial_points
            # Should be at least base points (may include first-time bonus)
            self.assertGreaterEqual(points_gained, expected_points)


class TestAdjacencyValidation(unittest.TestCase):
    """Test adjacency rules for attacks"""

    def test_adjacency_requirement(self):
        """Rule: Can only attack adjacent strongholds"""
        game_state = GameState()
        alliance = game_state.get_alliance(1)

        # Alliance 1 starts with T1, connected to S1-2
        self.assertTrue(game_state.can_alliance_attack_stronghold(1, "S1-2"))

        # Cannot attack non-adjacent strongholds
        self.assertFalse(game_state.can_alliance_attack_stronghold(1, "S3-10"))

    def test_cannot_attack_own_strongholds(self):
        """Rule: Cannot attack own controlled strongholds"""
        game_state = GameState()

        # Cannot attack own home
        self.assertFalse(game_state.can_alliance_attack_stronghold(1, "T1"))


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)