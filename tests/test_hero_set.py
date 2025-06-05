# tests/test_hero_set.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.entities.hero import Hero
from game_simulator.entities.hero_set import HeroSet

class TestHeroSet(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a set of test heroes
        self.heroes = [Hero(f"hero_{i}", is_npc=True, stronghold_level=1) for i in range(5)]
        self.hero_set = HeroSet("test_set", "test_owner", self.heroes, is_npc=True, stronghold_level=1)
    
    def test_hero_set_creation(self):
        """Test creating a hero set"""
        self.assertEqual(self.hero_set.id, "test_set")
        self.assertEqual(self.hero_set.owner_id, "test_owner")
        self.assertEqual(len(self.hero_set.heroes), 5)
        self.assertFalse(self.hero_set.consumed_for_attack)
        
        # All heroes should be alive initially
        self.assertEqual(len(self.hero_set.get_living_heroes()), 5)
        
    def test_living_heroes_tracking(self):
        """Test tracking of living vs dead heroes"""
        # Kill one hero
        self.heroes[0].take_damage(self.heroes[0].max_hp + 100)
        self.assertFalse(self.heroes[0].is_alive)
        
        # Should now have 4 living heroes
        living = self.hero_set.get_living_heroes()
        self.assertEqual(len(living), 4)
        self.assertNotIn(self.heroes[0], living)
        
        # Kill another hero
        self.heroes[1].take_damage(self.heroes[1].max_hp + 100)
        living = self.hero_set.get_living_heroes()
        self.assertEqual(len(living), 3)
        
    def test_attack_consumption(self):
        """Test attack consumption mechanics"""
        # Initially can attack
        self.assertTrue(self.hero_set.can_attack())
        
        # Mark as consumed
        self.hero_set.mark_consumed_for_attack()
        self.assertTrue(self.hero_set.consumed_for_attack)
        self.assertFalse(self.hero_set.can_attack())
        
        # Reset consumption
        self.hero_set.consumed_for_attack = False
        self.assertFalse(self.hero_set.consumed_for_attack)
        self.assertTrue(self.hero_set.can_attack())
        
    def test_cannot_attack_when_all_dead(self):
        """Test that hero set cannot attack when all heroes are dead"""
        # Kill all heroes
        for hero in self.heroes:
            hero.take_damage(hero.max_hp + 100)
        
        # Should not be able to attack even if not consumed
        self.assertFalse(self.hero_set.consumed_for_attack)
        self.assertFalse(self.hero_set.can_attack())
        
        # Even after resetting consumption
        self.hero_set.consumed_for_attack = False
        self.assertFalse(self.hero_set.can_attack())
        
    def test_heal_all_heroes(self):
        """Test healing all heroes in the set"""
        # Damage all heroes
        for hero in self.heroes:
            hero.take_damage(1000)
        
        # Verify they're damaged
        for hero in self.heroes:
            self.assertLess(hero.current_hp, hero.max_hp)
        
        # Heal all
        self.hero_set.heal_all_heroes()
        
        # Verify they're healed
        for hero in self.heroes:
            self.assertEqual(hero.current_hp, hero.max_hp)
            self.assertTrue(hero.is_alive)
            
    def test_heal_revives_dead_heroes(self):
        """Test that healing revives dead heroes"""
        # Kill some heroes
        self.heroes[0].take_damage(self.heroes[0].max_hp + 100)
        self.heroes[1].take_damage(self.heroes[1].max_hp + 100)
        
        self.assertEqual(len(self.hero_set.get_living_heroes()), 3)
        
        # Heal all
        self.hero_set.heal_all_heroes()
        
        # All should be alive again
        self.assertEqual(len(self.hero_set.get_living_heroes()), 5)
        for hero in self.heroes:
            self.assertTrue(hero.is_alive)
            self.assertEqual(hero.current_hp, hero.max_hp)
    
    def test_total_stats(self):
        """Test calculation of total stats"""
        total_attack = self.hero_set.get_total_damage_potential()
        total_hp = self.hero_set.get_total_hp()
        
        # Should equal sum of individual hero stats
        expected_attack = sum(hero.attack for hero in self.heroes)
        expected_hp = sum(hero.current_hp for hero in self.heroes)
        
        self.assertEqual(total_attack, expected_attack)
        self.assertEqual(total_hp, expected_hp)
        
    def test_total_stats_with_dead_heroes(self):
        """Test that dead heroes don't contribute to attack potential"""
        # Kill one hero
        self.heroes[0].take_damage(self.heroes[0].max_hp + 100)
        
        total_attack = self.hero_set.get_total_damage_potential()
        total_hp = self.hero_set.get_total_hp()
        
        # Attack potential should only count living heroes
        living_heroes = self.hero_set.get_living_heroes()
        expected_attack = sum(hero.attack for hero in living_heroes)
        # Total HP includes dead heroes (0 HP)
        expected_hp = sum(hero.current_hp for hero in self.heroes)
        
        self.assertEqual(total_attack, expected_attack)
        self.assertEqual(total_hp, expected_hp)
    
    def test_average_defense_calculation(self):
        """Test average defense calculation for battle mechanics"""
        avg_defense = self.hero_set.get_average_defense()
        
        living_heroes = self.hero_set.get_living_heroes()
        expected_avg = sum(hero.defense for hero in living_heroes) / len(living_heroes)
        
        self.assertEqual(avg_defense, expected_avg)
        
    def test_average_defense_with_dead_heroes(self):
        """Test average defense calculation when some heroes are dead"""
        # Kill two heroes
        self.heroes[0].take_damage(self.heroes[0].max_hp + 100)
        self.heroes[1].take_damage(self.heroes[1].max_hp + 100)
        
        avg_defense = self.hero_set.get_average_defense()
        
        living_heroes = self.hero_set.get_living_heroes()
        expected_avg = sum(hero.defense for hero in living_heroes) / len(living_heroes)
        
        self.assertEqual(avg_defense, expected_avg)
        self.assertEqual(len(living_heroes), 3)
    
    def test_hero_set_representation(self):
        """Test hero set string representation"""
        hero_set_str = str(self.hero_set)
        
        self.assertIn("test_set", hero_set_str)
        self.assertIn("5/5 alive", hero_set_str)
        self.assertIn("NPC", hero_set_str)
        
        # Kill a hero and test representation changes
        self.heroes[0].take_damage(self.heroes[0].max_hp + 100)
        hero_set_str = str(self.hero_set)
        
        self.assertIn("4/5 alive", hero_set_str)

if __name__ == '__main__':
    unittest.main()