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
        
    def test_player_hero_stat_distribution(self):
        """FIXED: Test that player heroes follow correct statistical distribution"""
        # Generate many heroes to test distribution
        heroes = [Hero(f"hero_{i}", is_npc=False) for i in range(500)]

        attacks = [h.attack for h in heroes]
        defenses = [h.defense for h in heroes]
        hps = [h.max_hp for h in heroes]
        
        # Test means are approximately correct (README specifies exact values)
        self.assertAlmostEqual(np.mean(attacks), 4627, delta=200)
        self.assertAlmostEqual(np.mean(defenses), 4195, delta=150)
        self.assertAlmostEqual(np.mean(hps), 8088, delta=300)

        # Test that there's proper variation (not fixed values)
        self.assertGreater(np.std(attacks), 300)
        self.assertGreater(np.std(defenses), 200)
        self.assertGreater(np.std(hps), 500)

    def test_npc_hero_creation_with_normal_distribution(self):
        """FIXED: Test NPC heroes use normal distribution per README rules"""
        # Level 1 NPCs (90% scaling)
        npc_l1_heroes = [Hero(f"npc_l1_{i}", is_npc=True, stronghold_level=1) for i in range(200)]
        l1_attacks = [h.attack for h in npc_l1_heroes]
        l1_expected_mean = 4627 * 0.9

        # Should be approximately 90% of player average
        self.assertAlmostEqual(np.mean(l1_attacks), l1_expected_mean, delta=200)
        # Should show statistical variation (normal distribution)
        self.assertGreater(np.std(l1_attacks), 200)

        # Level 2 NPCs (100% scaling)
        npc_l2_heroes = [Hero(f"npc_l2_{i}", is_npc=True, stronghold_level=2) for i in range(200)]
        l2_attacks = [h.attack for h in npc_l2_heroes]

        # Should be approximately equal to player average
        self.assertAlmostEqual(np.mean(l2_attacks), 4627, delta=200)
        self.assertGreater(np.std(l2_attacks), 200)

        # Level 3 NPCs (110% scaling)
        npc_l3_heroes = [Hero(f"npc_l3_{i}", is_npc=True, stronghold_level=3) for i in range(200)]
        l3_attacks = [h.attack for h in npc_l3_heroes]
        l3_expected_mean = 4627 * 1.1

        # Should be approximately 110% of player average
        self.assertAlmostEqual(np.mean(l3_attacks), l3_expected_mean, delta=200)
        self.assertGreater(np.std(l3_attacks), 200)
        
    def test_npc_level_progression(self):
        """FIXED: Test that NPC levels provide proper difficulty progression"""
        # Generate heroes for each level
        l1_heroes = [Hero(f"l1_{i}", is_npc=True, stronghold_level=1) for i in range(100)]
        l2_heroes = [Hero(f"l2_{i}", is_npc=True, stronghold_level=2) for i in range(100)]
        l3_heroes = [Hero(f"l3_{i}", is_npc=True, stronghold_level=3) for i in range(100)]
        
        l1_avg_attack = np.mean([h.attack for h in l1_heroes])
        l2_avg_attack = np.mean([h.attack for h in l2_heroes])
        l3_avg_attack = np.mean([h.attack for h in l3_heroes])
        
        # Should show progression: L1 < L2 < L3
        self.assertLess(l1_avg_attack, l2_avg_attack)
        self.assertLess(l2_avg_attack, l3_avg_attack)

        # Verify approximate scaling ratios
        self.assertAlmostEqual(l1_avg_attack / l2_avg_attack, 0.9, delta=0.1)
        self.assertAlmostEqual(l3_avg_attack / l2_avg_attack, 1.1, delta=0.1)
        
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

    def test_stat_bounds(self):
        """ADDED: Test that stats have reasonable bounds"""
        heroes = [Hero(f"hero_{i}", is_npc=False) for i in range(100)]

        for hero in heroes:
            # All stats should be positive
            self.assertGreater(hero.attack, 0)
            self.assertGreater(hero.defense, 0)
            self.assertGreater(hero.max_hp, 0)

            # Stats should be within reasonable bounds (mean ± 4 standard deviations)
            self.assertGreater(hero.attack, 4627 - 4*432)
            self.assertLess(hero.attack, 4627 + 4*432)

if __name__ == '__main__':
    unittest.main()