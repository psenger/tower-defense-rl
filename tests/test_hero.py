# tests/test_hero.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.entities.hero import Hero

class TestHero(unittest.TestCase):
    
    def test_player_hero_creation(self):
        """Test creating a player hero with random stats"""
        hero = Hero("test_hero", is_npc=False)
        
        self.assertEqual(hero.id, "test_hero")
        self.assertFalse(hero.is_npc)
        self.assertTrue(hero.is_alive)
        
        # Stats should be positive
        self.assertGreater(hero.attack, 0)
        self.assertGreater(hero.defense, 0)
        self.assertGreater(hero.max_hp, 0)
        self.assertEqual(hero.current_hp, hero.max_hp)
        
        # Stats should be roughly around expected ranges
        self.assertGreater(hero.attack, 3000)  # Should be around 4627 ± some variance
        self.assertLess(hero.attack, 7000)
        
    def test_npc_hero_creation(self):
        """Test creating NPC heroes with scaled stats"""
        # Level 1 NPC (80% of player average)
        npc_l1 = Hero("npc_l1", is_npc=True, stronghold_level=1)
        expected_attack_l1 = int(4627 * 0.8)
        expected_defense_l1 = int(4195 * 0.8)
        expected_hp_l1 = int(8088 * 0.8)
        
        self.assertEqual(npc_l1.attack, expected_attack_l1)
        self.assertEqual(npc_l1.defense, expected_defense_l1)
        self.assertEqual(npc_l1.max_hp, expected_hp_l1)
        
        # Level 2 NPC (100% of player average)
        npc_l2 = Hero("npc_l2", is_npc=True, stronghold_level=2)
        self.assertEqual(npc_l2.attack, 4627)
        self.assertEqual(npc_l2.defense, 4195)
        self.assertEqual(npc_l2.max_hp, 8088)
        
        # Level 3 NPC (120% of player average)
        npc_l3 = Hero("npc_l3", is_npc=True, stronghold_level=3)
        expected_attack_l3 = int(4627 * 1.2)
        expected_defense_l3 = int(4195 * 1.2)
        expected_hp_l3 = int(8088 * 1.2)
        
        self.assertEqual(npc_l3.attack, expected_attack_l3)
        self.assertEqual(npc_l3.defense, expected_defense_l3)
        self.assertEqual(npc_l3.max_hp, expected_hp_l3)
        
    def test_damage_system(self):
        """Test hero damage and death mechanics"""
        hero = Hero("test_hero", is_npc=True, stronghold_level=1)  # Use NPC for predictable stats
        initial_hp = hero.current_hp
        
        # Apply damage
        damage_dealt = hero.take_damage(1000)
        self.assertEqual(damage_dealt, 1000)
        self.assertEqual(hero.current_hp, initial_hp - 1000)
        self.assertTrue(hero.is_alive)
        
        # Apply fatal damage
        fatal_damage = hero.current_hp + 100
        damage_dealt = hero.take_damage(fatal_damage)
        self.assertEqual(hero.current_hp, 0)
        self.assertFalse(hero.is_alive)
        
        # Cannot take more damage when dead
        damage_dealt = hero.take_damage(100)
        self.assertEqual(damage_dealt, 0)
        self.assertEqual(hero.current_hp, 0)
        
    def test_healing(self):
        """Test hero healing mechanics"""
        hero = Hero("test_hero", is_npc=True, stronghold_level=1)
        
        # Damage the hero
        hero.take_damage(1000)
        damaged_hp = hero.current_hp
        self.assertLess(damaged_hp, hero.max_hp)
        self.assertTrue(hero.is_alive)
        
        # Heal to full
        hero.heal_full()
        self.assertEqual(hero.current_hp, hero.max_hp)
        self.assertTrue(hero.is_alive)
        
        # Test healing a dead hero
        hero.take_damage(hero.max_hp + 100)  # Kill the hero
        self.assertFalse(hero.is_alive)
        
        hero.heal_full()
        self.assertTrue(hero.is_alive)
        self.assertEqual(hero.current_hp, hero.max_hp)
        
    def test_hp_percentage(self):
        """Test HP percentage calculation"""
        hero = Hero("test_hero", is_npc=True, stronghold_level=1)
        
        # Full health
        self.assertEqual(hero.get_hp_percentage(), 100.0)
        
        # Half health
        hero.take_damage(hero.max_hp // 2)
        self.assertAlmostEqual(hero.get_hp_percentage(), 50.0, places=1)
        
        # Dead
        hero.take_damage(hero.max_hp)
        self.assertEqual(hero.get_hp_percentage(), 0.0)
        
    def test_hero_representation(self):
        """Test hero string representation"""
        hero = Hero("test_hero", is_npc=False)
        hero_str = str(hero)
        
        self.assertIn("test_hero", hero_str)
        self.assertIn("Player", hero_str)
        self.assertIn("Alive", hero_str)
        
        # Test NPC representation
        npc = Hero("npc_hero", is_npc=True)
        npc_str = str(npc)
        
        self.assertIn("npc_hero", npc_str)
        self.assertIn("NPC", npc_str)

if __name__ == '__main__':
    unittest.main()