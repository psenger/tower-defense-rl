# tests/test_stronghold.py
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
        
        # Level 1 stronghold
        self.assertEqual(self.level1_stronghold.level, 1)
        self.assertFalse(self.level1_stronghold.is_alliance_home)
        self.assertEqual(len(self.level1_stronghold.npc_defense_teams), 9)  # Level 1 = 9 NPCs
        self.assertEqual(self.level1_stronghold.max_npc_teams, 9)
        
        # Level 2 stronghold
        self.assertEqual(self.level2_stronghold.level, 2)
        self.assertEqual(len(self.level2_stronghold.npc_defense_teams), 12)  # Level 2 = 12 NPCs
        
        # Level 3 stronghold
        self.assertEqual(self.level3_stronghold.level, 3)
        self.assertEqual(len(self.level3_stronghold.npc_defense_teams), 15)  # Level 3 = 15 NPCs
    
    def test_npc_team_creation(self):
        """Test that NPC teams are created with correct stats"""
        npc_teams = self.level2_stronghold.npc_defense_teams
        
        # Each team should have 5 heroes
        for team in npc_teams:
            self.assertEqual(len(team.heroes), 5)
            
            # Each hero should be an NPC with level 2 stats
            for hero in team.heroes:
                self.assertTrue(hero.is_npc)
                # Level 2 NPCs should have 100% of player average stats
                self.assertEqual(hero.attack, 4627)
                self.assertEqual(hero.defense, 4195)
                self.assertEqual(hero.max_hp, 8088)
    
    def test_alliance_control(self):
        """Test alliance control mechanics"""
        # Initially uncontrolled
        self.assertIsNone(self.level1_stronghold.controlling_alliance)
        self.assertFalse(self.level1_stronghold.is_controlled)
        
        # Set control
        self.level1_stronghold.set_controlling_alliance(2)
        self.assertEqual(self.level1_stronghold.controlling_alliance, 2)
        self.assertTrue(self.level1_stronghold.is_controlled)
        
        # Remove control
        self.level1_stronghold.remove_alliance_control()
        self.assertIsNone(self.level1_stronghold.controlling_alliance)
        self.assertFalse(self.level1_stronghold.is_controlled)
    
    def test_protection_mechanics(self):
        """Test stronghold protection period"""
        # Initially not protected
        self.assertFalse(self.level1_stronghold.is_protected)
        
        # Apply protection
        self.level1_stronghold.apply_protection(1200.0)  # 20 minutes
        self.assertTrue(self.level1_stronghold.is_protected)
        
        # Check protection expiry
        self.level1_stronghold.update_protection(600.0)  # 10 minutes passed
        self.assertTrue(self.level1_stronghold.is_protected)  # Still protected
        
        self.level1_stronghold.update_protection(1300.0)  # Total 21 minutes passed
        self.assertFalse(self.level1_stronghold.is_protected)  # Protection expired
    
    def test_can_be_attacked(self):
        """Test attack eligibility rules"""
        # Uncontrolled stronghold can be attacked
        self.assertTrue(self.level1_stronghold.can_be_attacked())
        
        # Protected stronghold cannot be attacked
        self.level1_stronghold.apply_protection(1200.0)
        self.assertFalse(self.level1_stronghold.can_be_attacked())
        
        # Remove protection
        self.level1_stronghold.protection_end_time = 0
        self.assertTrue(self.level1_stronghold.can_be_attacked())
        
        # Controlled stronghold can be attacked
        self.level1_stronghold.set_controlling_alliance(1)
        self.assertTrue(self.level1_stronghold.can_be_attacked())
    
    def test_npc_team_management(self):
        """Test NPC team destruction and tracking"""
        initial_count = len(self.level1_stronghold.get_active_npc_teams())
        self.assertEqual(initial_count, 9)
        
        # Destroy some NPC teams
        self.level1_stronghold.destroy_npc_team(0)
        self.level1_stronghold.destroy_npc_team(1)
        
        active_teams = self.level1_stronghold.get_active_npc_teams()
        self.assertEqual(len(active_teams), 7)
        
        # Check that destroyed teams are actually destroyed
        self.assertIsNone(self.level1_stronghold.npc_defense_teams[0])
        self.assertIsNone(self.level1_stronghold.npc_defense_teams[1])
    
    def test_garrison_management(self):
        """Test garrison hero set management"""
        # Create some hero sets to garrison
        heroes1 = [Hero(f"garrison_hero_{i}", is_npc=False) for i in range(5)]
        heroes2 = [Hero(f"garrison_hero_{i+5}", is_npc=False) for i in range(5)]
        garrison_set1 = HeroSet("garrison_set_1", heroes1)
        garrison_set2 = HeroSet("garrison_set_2", heroes2)
        
        # Add to garrison
        self.level1_stronghold.add_garrison(garrison_set1)
        self.level1_stronghold.add_garrison(garrison_set2)
        
        self.assertEqual(len(self.level1_stronghold.garrisoned_hero_sets), 2)
        self.assertIn(garrison_set1, self.level1_stronghold.garrisoned_hero_sets)
        self.assertIn(garrison_set2, self.level1_stronghold.garrisoned_hero_sets)
        
        # Remove from garrison
        self.level1_stronghold.remove_garrison(garrison_set1)
        self.assertEqual(len(self.level1_stronghold.garrisoned_hero_sets), 1)
        self.assertNotIn(garrison_set1, self.level1_stronghold.garrisoned_hero_sets)
    
    def test_garrison_capacity(self):
        """Test garrison capacity limits"""
        # Fill garrison to capacity (9 hero sets for level 1)
        garrison_sets = []
        for i in range(10):  # Try to add 10 (more than capacity)
            heroes = [Hero(f"hero_{j}_{i}", is_npc=False) for j in range(5)]
            hero_set = HeroSet(f"set_{i}", heroes)
            garrison_sets.append(hero_set)
        
        # Add hero sets
        for hero_set in garrison_sets:
            self.level1_stronghold.add_garrison(hero_set)
        
        # Should only have 9 (capacity limit for level 1)
        self.assertEqual(len(self.level1_stronghold.garrisoned_hero_sets), 9)
    
    def test_defense_team_availability(self):
        """Test getting available defense teams (NPCs + garrison)"""
        # Initially should have all NPC teams
        defense_teams = self.level1_stronghold.get_available_defense_teams()
        self.assertEqual(len(defense_teams), 9)
        
        # Add garrison
        heroes = [Hero(f"garrison_hero_{i}", is_npc=False) for i in range(5)]
        garrison_set = HeroSet("garrison_set", heroes)
        self.level1_stronghold.add_garrison(garrison_set)
        
        # Should now include garrison
        defense_teams = self.level1_stronghold.get_available_defense_teams()
        self.assertEqual(len(defense_teams), 10)  # 9 NPCs + 1 garrison
        
        # Destroy some NPC teams
        self.level1_stronghold.destroy_npc_team(0)
        self.level1_stronghold.destroy_npc_team(1)
        
        defense_teams = self.level1_stronghold.get_available_defense_teams()
        self.assertEqual(len(defense_teams), 8)  # 7 NPCs + 1 garrison
    
    def test_connections(self):
        """Test stronghold connections"""
        self.assertIn("T1", self.level1_stronghold.connections)
        self.assertIn("S5-5", self.level1_stronghold.connections)
        
        # Test connection check
        self.assertTrue(self.level1_stronghold.is_connected_to("T1"))
        self.assertTrue(self.level1_stronghold.is_connected_to("S5-5"))
        self.assertFalse(self.level1_stronghold.is_connected_to("S18-18"))
    
    def test_stronghold_representation(self):
        """Test stronghold string representation"""
        stronghold_str = str(self.level1_stronghold)
        
        self.assertIn("S1-1", stronghold_str)
        self.assertIn("Level 1", stronghold_str)
        self.assertIn("Neutral", stronghold_str)
        
        # Test controlled stronghold representation
        self.level1_stronghold.set_controlling_alliance(2)
        controlled_str = str(self.level1_stronghold)
        self.assertIn("Alliance 2", controlled_str)
    
    def test_alliance_home_special_properties(self):
        """Test special properties of alliance home strongholds"""
        # Alliance homes have no NPCs
        self.assertEqual(len(self.alliance_home.npc_defense_teams), 0)
        self.assertEqual(len(self.alliance_home.get_active_npc_teams()), 0)
        
        # Alliance homes have same garrison capacity as level 1 strongholds (both level 1)
        self.assertEqual(self.alliance_home.max_garrison_size, 9)
        
        # Same as regular level 1 strongholds
        self.assertEqual(self.level1_stronghold.max_garrison_size, 9)

if __name__ == '__main__':
    unittest.main()