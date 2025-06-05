# game_simulator/entities/hero_set.py
from .hero import Hero


class HeroSet:
    def __init__(self, set_id, owner_id, heroes=None, is_npc=False, stronghold_level=1):
        self.id = set_id
        self.owner_id = owner_id  # Player ID or "NPC"
        self.is_npc = is_npc

        # Game mechanics status
        self.consumed_for_attack = False  # Per game half
        self.is_garrisoned = False
        self.garrisoned_stronghold = None

        # FIXED: Track if this set is currently engaged in battle
        self.is_in_battle = False
        self.current_battle_id = None

        # Create 5 heroes for this set
        if heroes:
            self.heroes = heroes[:5]  # Ensure exactly 5 heroes
            # Ensure we have exactly 5 heroes
            while len(self.heroes) < 5:
                hero_id = f"{set_id}_H{len(self.heroes) + 1}"
                hero = Hero(hero_id, is_npc, stronghold_level)
                self.heroes.append(hero)
        else:
            self.heroes = []
            for i in range(5):
                hero_id = f"{set_id}_H{i + 1}"
                hero = Hero(hero_id, is_npc, stronghold_level)
                self.heroes.append(hero)

    def get_living_heroes(self):
        """Get all living heroes in this set"""
        return [hero for hero in self.heroes if hero.is_alive]

    def get_average_defense(self):
        """Get average defense of all living heroes"""
        living_heroes = self.get_living_heroes()
        if not living_heroes:
            return 0
        return sum(hero.defense for hero in living_heroes) / len(living_heroes)

    def is_defeated(self):
        """Check if all heroes in this set are defeated"""
        return len(self.get_living_heroes()) == 0

    def heal_all_heroes(self):
        """Restore all heroes to full health"""
        for hero in self.heroes:
            hero.heal_full()

    def get_total_damage_potential(self):
        """Calculate total damage potential of living heroes"""
        return sum(hero.attack for hero in self.get_living_heroes())

    def get_total_hp(self):
        """Get total current HP of all heroes"""
        return sum(hero.current_hp for hero in self.heroes)

    def get_max_hp(self):
        """Get total max HP of all heroes"""
        return sum(hero.max_hp for hero in self.heroes)

    def reset_for_new_half(self):
        """FIXED: Complete reset for new game half per README rules

        Rule: "All Hero Sets revert to 'Available for Attack' and all Heroes are restored to full health"
        """
        # Reset consumption status
        self.consumed_for_attack = False

        # Reset battle engagement status
        self.is_in_battle = False
        self.current_battle_id = None

        # CRITICAL FIX: Heal all heroes to full health for new half
        self.heal_all_heroes()

        # Note: garrison status persists across halves per rules

    def assign_to_garrison(self, stronghold_id):
        """Assign this set to garrison a stronghold"""
        self.is_garrisoned = True
        self.garrisoned_stronghold = stronghold_id

    def remove_from_garrison(self):
        """Remove this set from garrison duty"""
        self.is_garrisoned = False
        self.garrisoned_stronghold = None

    def can_attack(self):
        """FIXED: Check if this set can be used to initiate attacks

        Rule compliance:
        - Not consumed for attack this half
        - Not currently defeated (has living heroes)
        - Not currently engaged in battle
        """
        return (not self.consumed_for_attack and
                not self.is_defeated() and
                not self.is_in_battle)

    def engage_in_battle(self, battle_id):
        """FIXED: Mark as engaged in battle - this is when consumption should occur

        Rule: "Hero Set becomes 'Consumed for Attack' when it ENGAGES in battle"
        """
        self.is_in_battle = True
        self.current_battle_id = battle_id
        # CRITICAL FIX: Only mark as consumed when actually engaging, not during start_battle()
        if not self.is_npc:  # Only player sets get consumed
            self.consumed_for_attack = True

    def disengage_from_battle(self):
        """Mark as no longer in battle"""
        self.is_in_battle = False
        self.current_battle_id = None

    def can_be_garrisoned(self):
        """Check if this set can be assigned to garrison duty"""
        return not self.is_defeated() and not self.is_in_battle

    def __repr__(self):
        living_count = len(self.get_living_heroes())
        status_parts = []
        if self.consumed_for_attack:
            status_parts.append("Consumed")
        if self.is_in_battle:
            status_parts.append(f"InBattle({self.current_battle_id})")
        if self.is_garrisoned:
            status_parts.append(f"Garrisoned@{self.garrisoned_stronghold}")

        status = f" ({', '.join(status_parts)})" if status_parts else ""
        npc_str = "NPC" if self.is_npc else "Player"

        return f"HeroSet({self.id}, {npc_str}, {living_count}/5 alive{status})"
