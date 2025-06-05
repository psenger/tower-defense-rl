# tests/test_stronghold.py - UPDATED WITH RULE COMPLIANCE
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.entities.stronghold import Stronghold
from game_simulator.entities.hero_set import HeroSet
from game_simulator.entities.hero import Hero


class TestStronghold(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create different types of strongholds
        self.alliance_home = Stronghold("T1", 1, 100, 100, connections=[])
        self.alliance_home.set_as_alliance_home(1)  # Set after creation
        self.level1_stronghold = Stronghold("S1-1", 1, 200, 200, connections=["T1", "S5-5"])
        self.level2_stronghold = Stronghold("S10-10", 2, 300, 300, connections=["S5-5", "S18-18"])
        self.level3_stronghold = Stronghold("S18-18", 3, 400, 400, connections=["S10-10", "S11-11", "S17-17", "S19-19"])

    def test_stronghold_creation(self):
        """Test creating strongholds of different types"""
        # Alliance home
        self.assertEqual(self.alliance_home.id, "T1")
        self.assertTrue(self.alliance_home.is_alliance_home)
        self.assertEqual(self.alliance_home.level, 1)
        self.assertEqual(len(self.alliance_home.npc_defense_teams), 0)  # No NPCs in homes after set as alliance home
        self.assertEqual(self.alliance_home.controlling_alliance, 1)  # Set during setup

        # Level 1 stronghold - EXACT VALUES per README
        self.assertEqual(self.level1_stronghold.level, 1)
        self.assertFalse(self.level1_stronghold.is_alliance_home)
        self.assertEqual(len(self.level1_stronghold.npc_defense_teams), 9)  # Level 1 = 9 NPCs
        self.assertEqual(self.level1_stronghold.max_npc_teams, 9)
        self.assertEqual(self.level1_stronghold.max_garrison_size, 9)  # Level 1 = 9 garrison

        # Level 2 stronghold - EXACT VALUES per README
        self.assertEqual(self.level2_stronghold.level, 2)
        self.assertEqual(len(self.level2_stronghold.npc_defense_teams), 12)  # Level 2 = 12 NPCs
        self.assertEqual(self.level2_stronghold.max_garrison_size, 7)  # Level 2 = 7 garrison

        # Level 3 stronghold - EXACT VALUES per README
        self.assertEqual(self.level3_stronghold.level, 3)
        self.assertEqual(len(self.level3_stronghold.npc_defense_teams), 15)  # Level 3 = 15 NPCs
        self.assertEqual(self.level3_stronghold.max_garrison_size, 5)  # Level 3 = 5 garrison

    def test_npc_team_creation_with_proper_stats(self):
        """FIXED: Test that NPC teams are created with proper statistical variation"""
        npc_teams = self.level2_stronghold.npc_defense_teams

        # Each team should have 5 heroes
        for team in npc_teams:
            self.assertEqual(len(team.heroes), 5)

            # Each hero should be an NPC with level 2 stats showing variation
            attacks = [hero.attack for hero in team.heroes]
            defenses = [hero.defense for hero in team.heroes]

            for hero in team.heroes:
                self.assertTrue(hero.is_npc)

            # FIXED: NPCs should show statistical variation, not fixed values
            if len(attacks) > 1:  # Need multiple heroes to test variation
                # Should have some variation in stats (not all identical)
                self.assertTrue(len(set(attacks)) > 1 or len(set(defenses)) > 1)

    def test_alliance_control(self):
        """Test alliance control mechanics"""
        # Initially uncontrolled
        self.assertIsNone(self.level1_stronghold.controlling_alliance)
        self.assertTrue(self.level1_stronghold.is_neutral())

        # Set control (through capture simulation)
        self.level1_stronghold.controlling_alliance = 2
        self.assertEqual(self.level1_stronghold.controlling_alliance, 2)
        self.assertFalse(self.level1_stronghold.is_neutral())

        # Remove control
        self.level1_stronghold.controlling_alliance = None
        self.assertIsNone(self.level1_stronghold.controlling_alliance)
        self.assertTrue(self.level1_stronghold.is_neutral())

    def test_protection_mechanics_with_game_time(self):
        """FIXED: Test stronghold protection period using game time"""
        current_game_time = 1000.0  # Some point in the game

        # Initially not protected
        self.assertFalse(self.level1_stronghold.is_protected)

        # Apply protection (60 minutes = 3600 seconds)
        self.level1_stronghold.start_protection(60, current_game_time)
        self.assertTrue(self.level1_stronghold.is_protected)
        self.assertEqual(self.level1_stronghold.protection_end_time, current_game_time + 3600)

        # Check protection hasn't expired yet
        self.level1_stronghold.update_protection_status(current_game_time + 1800)  # 30 minutes later
        self.assertTrue(self.level1_stronghold.is_protected)

        # Check protection expires
        self.level1_stronghold.update_protection_status(current_game_time + 3700)  # 61+ minutes later
        self.assertFalse(self.level1_stronghold.is_protected)

    def test_reduced_protection_in_final_hour(self):
        """FIXED: Test protection reduction in final hour per README rules"""
        # Normal time (not in final hour)
        normal_time = 10 * 60 * 60  # 10 hours into first half
        duration = self.level1_stronghold.get_reduced_protection_duration(normal_time)
        self.assertEqual(duration, 60)  # Normal 60 minutes

        # Final hour of first half (11 hours in)
        final_hour_time = 11 * 60 * 60  # 11 hours into first half
        duration = self.level1_stronghold.get_reduced_protection_duration(final_hour_time)
        self.assertEqual(duration, 5)  # Reduced to 5 minutes

        # Just before final hour
        pre_final_time = (11.5 * 60 * 60) - (61 * 60)  # 1 minute before final hour
        duration = self.level1_stronghold.get_reduced_protection_duration(pre_final_time)
        self.assertEqual(duration, 60)  # Still normal

    def test_can_be_attacked(self):
        """Test attack eligibility rules"""
        # Uncontrolled stronghold can be attacked
        self.assertTrue(self.level1_stronghold.can_be_attacked())

        # Protected stronghold cannot be attacked
        self.level1_stronghold.start_protection(20, 0)
        self.assertFalse(self.level1_stronghold.can_be_attacked())

        # Remove protection
        self.level1_stronghold.protection_end_time = 0
        self.level1_stronghold.is_protected = False
        self.assertTrue(self.level1_stronghold.can_be_attacked())

        # Controlled stronghold can be attacked
        self.level1_stronghold.controlling_alliance = 1
        self.assertTrue(self.level1_stronghold.can_be_attacked())

    def test_immediate_npc_team_removal(self):
        """FIXED: Test immediate NPC team removal per README rules"""
        initial_count = len(self.level1_stronghold.get_active_npc_teams())
        self.assertEqual(initial_count, 9)

        # Simulate NPC team defeat with immediate removal
        first_npc = self.level1_stronghold.npc_defense_teams[0]

        # FIXED: remove_defeated_npc_team should immediately remove the team
        success = self.level1_stronghold.remove_defeated_npc_team(first_npc, 1)

        self.assertTrue(success)
        active_teams = self.level1_stronghold.get_active_npc_teams()
        self.assertEqual(len(active_teams), 8)  # Should be immediately reduced
        self.assertNotIn(first_npc, self.level1_stronghold.npc_defense_teams)  # Should be gone

        # Check tracking of defeats
        self.assertEqual(self.level1_stronghold.npc_teams_defeated_by_alliance[1], 1)

    def test_capture_by_most_defeats(self):
        """FIXED: Test capture goes to alliance with most defeats"""
        # Set up defeat tracking
        self.level1_stronghold.npc_teams_defeated_by_alliance = {
            1: 3,  # Alliance 1: 3 defeats
            2: 5,  # Alliance 2: 5 defeats
            3: 2  # Alliance 3: 2 defeats
        }

        # Clear all NPCs to make capturable
        self.level1_stronghold.npc_defense_teams = []

        # Alliance 3 triggers capture, but Alliance 2 should get it (most defeats)
        capturing_alliance_id = self.level1_stronghold.capture_by_alliance(3, 60, 1000.0)

        self.assertEqual(capturing_alliance_id, 2)  # Alliance 2 had most defeats
        self.assertEqual(self.level1_stronghold.controlling_alliance, 2)

        # Verify tracking is cleared after capture
        self.assertEqual(self.level1_stronghold.npc_teams_defeated_by_alliance, {})

    def test_tie_breaking_in_capture(self):
        """FIXED: Test tie-breaking logic in capture"""
        # Set up tie scenario
        self.level1_stronghold.npc_teams_defeated_by_alliance = {
            1: 4,  # Alliance 1: 4 defeats
            3: 4,  # Alliance 3: 4 defeats (tie)
            2: 2  # Alliance 2: 2 defeats
        }

        # Clear all NPCs to make capturable
        self.level1_stronghold.npc_defense_teams = []

        # Should go to alliance with lowest ID in tie
        capturing_alliance_id = self.level1_stronghold.capture_by_alliance(3)

        self.assertEqual(capturing_alliance_id, 1)  # Alliance 1 wins tie (lower ID)
        self.assertEqual(self.level1_stronghold.controlling_alliance, 1)

    def test_garrison_management(self):
        """Test garrison hero set management"""
        # Create some hero sets to garrison
        heroes1 = [Hero(f"garrison_hero_{i}", is_npc=False) for i in range(5)]
        heroes2 = [Hero(f"garrison_hero_{i + 5}", is_npc=False) for i in range(5)]
        garrison_set1 = HeroSet("garrison_set_1", "player1", heroes1)
        garrison_set2 = HeroSet("garrison_set_2", "player2", heroes2)

        # Add to garrison
        success1 = self.level1_stronghold.add_garrison_set(garrison_set1)
        success2 = self.level1_stronghold.add_garrison_set(garrison_set2)

        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertEqual(len(self.level1_stronghold.garrisoned_hero_sets), 2)
        self.assertIn(garrison_set1, self.level1_stronghold.garrisoned_hero_sets)
        self.assertIn(garrison_set2, self.level1_stronghold.garrisoned_hero_sets)

        # Remove from garrison
        success = self.level1_stronghold.remove_garrison_set(garrison_set1)
        self.assertTrue(success)
        self.assertEqual(len(self.level1_stronghold.garrisoned_hero_sets), 1)
        self.assertNotIn(garrison_set1, self.level1_stronghold.garrisoned_hero_sets)

    def test_garrison_capacity_limits(self):
        """Test garrison capacity limits per README rules"""
        # Test Level 1 (max 9), Level 2 (max 7), Level 3 (max 5)
        test_cases = [
            (self.level1_stronghold, 9),
            (self.level2_stronghold, 7),
            (self.level3_stronghold, 5)
        ]

        for stronghold, max_capacity in test_cases:
            # Fill to capacity
            garrison_sets = []
            for i in range(max_capacity + 2):  # Try to add more than capacity
                heroes = [Hero(f"hero_{j}_{i}", is_npc=False) for j in range(5)]
                hero_set = HeroSet(f"set_{i}", f"player_{i}", heroes)
                garrison_sets.append(hero_set)

            # Add hero sets
            added_count = 0
            for hero_set in garrison_sets:
                if stronghold.add_garrison_set(hero_set):
                    added_count += 1

            # Should only have added up to capacity
            self.assertEqual(added_count, max_capacity)
            self.assertEqual(len(stronghold.garrisoned_hero_sets), max_capacity)

    def test_immediate_cleanup_defeated_defenders(self):
        """FIXED: Test immediate cleanup of defeated defenders"""
        # Add garrison with living and dead heroes
        living_heroes = [Hero(f"living_{i}", is_npc=False) for i in range(5)]
        living_set = HeroSet("living_set", "player1", living_heroes)

        dead_heroes = [Hero(f"dead_{i}", is_npc=False) for i in range(5)]
        dead_set = HeroSet("dead_set", "player2", dead_heroes)

        # Kill all heroes in dead set
        for hero in dead_heroes:
            hero.take_damage(hero.max_hp + 100)

        self.level1_stronghold.add_garrison_set(living_set)
        self.level1_stronghold.add_garrison_set(dead_set)

        self.assertEqual(len(self.level1_stronghold.garrisoned_hero_sets), 2)

        # Cleanup should remove defeated sets immediately
        self.level1_stronghold.cleanup_defeated_defenders()

        self.assertEqual(len(self.level1_stronghold.garrisoned_hero_sets), 1)
        self.assertIn(living_set, self.level1_stronghold.garrisoned_hero_sets)
        self.assertNotIn(dead_set, self.level1_stronghold.garrisoned_hero_sets)

    def test_defense_team_availability(self):
        """Test getting available defense teams (NPCs + garrison)"""
        # Initially should have all NPC teams
        defense_teams = self.level1_stronghold.get_all_defending_sets()
        self.assertEqual(len(defense_teams), 9)

        # Add garrison
        heroes = [Hero(f"garrison_hero_{i}", is_npc=False) for i in range(5)]
        garrison_set = HeroSet("garrison_set", "player1", heroes)
        self.level1_stronghold.add_garrison_set(garrison_set)

        # Should now include garrison
        defense_teams = self.level1_stronghold.get_all_defending_sets()
        self.assertEqual(len(defense_teams), 10)  # 9 NPCs + 1 garrison

        # Simulate some NPC team defeats with immediate removal
        first_npc = self.level1_stronghold.npc_defense_teams[0]
        second_npc = self.level1_stronghold.npc_defense_teams[1]
        self.level1_stronghold.remove_defeated_npc_team(first_npc, 1)
        self.level1_stronghold.remove_defeated_npc_team(second_npc, 1)

        defense_teams = self.level1_stronghold.get_all_defending_sets()
        self.assertEqual(len(defense_teams), 8)  # 7 NPCs + 1 garrison

    def test_npc_respawn_rules(self):
        """FIXED: Test NPC respawn only in neutral strongholds"""
        # Remove some NPCs from neutral stronghold
        initial_count = len(self.level1_stronghold.npc_defense_teams)
        for i in range(3):
            npc = self.level1_stronghold.npc_defense_teams[0]
            self.level1_stronghold.remove_defeated_npc_team(npc, 1)

        self.assertEqual(len(self.level1_stronghold.npc_defense_teams), initial_count - 3)
        self.assertTrue(self.level1_stronghold.is_neutral())  # Still neutral

        # Should respawn NPCs in neutral stronghold
        respawned = self.level1_stronghold.respawn_npcs_if_neutral()
        self.assertTrue(respawned)
        self.assertEqual(len(self.level1_stronghold.npc_defense_teams), initial_count)  # Full complement

        # Capture stronghold and test no respawn
        self.level1_stronghold.controlling_alliance = 1
        self.assertFalse(self.level1_stronghold.is_neutral())

        # Clear NPCs
        self.level1_stronghold.npc_defense_teams = []

        # Should NOT respawn in controlled stronghold
        respawned = self.level1_stronghold.respawn_npcs_if_neutral()
        self.assertFalse(respawned)
        self.assertEqual(len(self.level1_stronghold.npc_defense_teams), 0)


if __name__ == '__main__':
    unittest.main()