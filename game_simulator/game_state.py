# game_simulator/game_state.py - FIXED VERSION
import time
from .entities.alliance import Alliance
from .entities.summit_battle import SummitBattle
from .map_layout import create_game_map


class GameState:
    def __init__(self):
        # Game timing
        self.game_time = 0.0  # In-game simulated time
        self.real_start_time = time.time()

        # Game structure
        self.current_half = 1  # 1 or 2
        self.is_halftime = False
        self.game_duration_hours = 11.5  # 11 hours 30 minutes per half
        self.halftime_duration_minutes = 30

        # Game end state
        self.game_ended = False
        self.winner = None

        # Map and strongholds
        self.strongholds = create_game_map()

        # Alliances (4 alliances with 50 players each)
        self.alliances = {}
        self._initialize_alliances()

        # Active battles
        self.active_battles = []
        self.battle_counter = 0

        # Game events and history
        self.event_log = []
        self.capture_history = []

        # Scoring tracking
        self.first_time_captures = set()  # Track strongholds captured for first time globally
        self.first_time_npc_defeats = set()  # Track NPC team slots defeated for first time globally

    def _initialize_alliances(self):
        """Initialize the 4 alliances with players and heroes"""
        alliance_data = [
            (1, "Alliance Red", (200, 50, 50)),
            (2, "Alliance Blue", (50, 50, 200)),
            (3, "Alliance Green", (50, 200, 50)),
            (4, "Alliance Yellow", (200, 200, 50))
        ]

        for alliance_id, name, color in alliance_data:
            alliance = Alliance(alliance_id, name, color)

            # Set alliance home
            home_id = f"T{alliance_id}"
            if home_id in self.strongholds:
                alliance.set_home_stronghold(home_id)
                self.strongholds[home_id].set_as_alliance_home(alliance_id)

            self.alliances[alliance_id] = alliance

    def is_game_over(self):
        """Check if the game has ended"""
        return self.game_ended

    def get_game_status(self):
        """Get current game status for display including end state"""
        status = {
            "half": self.current_half,
            "game_time": self.game_time,
            "active_battles": len(self.active_battles),
            "alliance_scores": {aid: alliance.summit_showdown_points for aid, alliance in self.alliances.items()},
            "stronghold_control": self._get_stronghold_control_summary(),
            "game_ended": self.game_ended,
            "winner": self.winner
        }
        return status

    def get_stronghold(self, stronghold_id):
        """Get a stronghold by ID"""
        return self.strongholds.get(stronghold_id)

    def get_alliance(self, alliance_id):
        """Get an alliance by ID"""
        return self.alliances.get(alliance_id)

    def start_battle(self, attacking_set, stronghold_id, defending_set=None):
        """FIXED: Start a new battle with proper engagement timing

        Rule: Hero Set becomes 'Consumed for Attack' when it ENGAGES in battle
        """
        stronghold = self.get_stronghold(stronghold_id)
        if not stronghold or not stronghold.can_be_attacked():
            return None

        # FIXED: Validate adjacency more thoroughly
        attacking_alliance = self._get_alliance_by_set(attacking_set)
        if attacking_alliance and not self.can_alliance_attack_stronghold(attacking_alliance.id, stronghold_id):
            self._log_event(f"INVALID ATTACK: Alliance {attacking_alliance.id} cannot attack {stronghold_id} - not adjacent")
            return None

        # FIXED: Check if attacking set is available (not in battle, not consumed)
        if not attacking_set.can_attack():
            self._log_event(f"INVALID ATTACK: Hero set {attacking_set.id} cannot attack (consumed/defeated/in-battle)")
            return None

        # FIXED: If attacking set is garrisoned, remove it from garrison immediately
        if attacking_set.is_garrisoned:
            garrison_stronghold = self.get_stronghold(attacking_set.garrisoned_stronghold)
            if garrison_stronghold:
                garrison_stronghold.remove_garrison_set(attacking_set)
                self._log_event(f"Hero set {attacking_set.id} removed from garrison at {attacking_set.garrisoned_stronghold} for attack")

        # If no specific defending set, pick one from available defenders
        if defending_set is None:
            available_defenders = stronghold.get_all_defending_sets()
            if not available_defenders:
                return None
            defending_set = available_defenders[0]  # Take first available

        # Create battle
        self.battle_counter += 1
        battle_id = f"Battle_{self.battle_counter}"
        battle = SummitBattle(battle_id, attacking_set, defending_set, stronghold_id)

        # CRITICAL FIX: Mark sets as engaged in battle (this triggers consumption for attackers)
        attacking_set.engage_in_battle(battle_id)
        defending_set.engage_in_battle(battle_id)

        self.active_battles.append(battle)
        self._log_event(f"Battle started: {attacking_set.id} attacks {stronghold_id} vs {defending_set.id}")

        return battle

    def update_battles(self, dt=None):
        """Update all active battles"""
        completed_battles = []

        for battle in self.active_battles:
            if battle.is_active:
                # For real-time simulation, execute one turn per update
                battle.execute_turn()

                if not battle.is_active:
                    completed_battles.append(battle)

        # Process completed battles
        for battle in completed_battles:
            self._resolve_battle(battle)
            self.active_battles.remove(battle)

    def _resolve_battle(self, battle):
        """FIXED: Resolve battle outcome with immediate defender removal and proper scoring"""
        stronghold = self.get_stronghold(battle.stronghold_id)
        if not stronghold:
            return

        # FIXED: Disengage hero sets from battle
        battle.attacking_set.disengage_from_battle()
        battle.defending_set.disengage_from_battle()

        # FIXED: Clean up defeated defenders immediately after battle
        stronghold.cleanup_defeated_defenders()

        if battle.winner == "attacker":
            # Attacker wins
            attacking_alliance = self._get_alliance_by_set(battle.attacking_set)

            # Check if defending set is NPC by checking if it's in NPC list
            if battle.defending_set in stronghold.npc_defense_teams:
                # Defeated an NPC team - remove immediately
                stronghold.remove_defeated_npc_team(battle.defending_set, attacking_alliance.id)
                self._log_event(f"NPC team {battle.defending_set.id} defeated at {stronghold.id} by Alliance {attacking_alliance.id}")
                is_npc_defeat = True
            else:
                # Defeated a player garrison set - already removed by cleanup_defeated_defenders
                self._log_event(f"Garrison {battle.defending_set.id} defeated at {stronghold.id} by Alliance {attacking_alliance.id}")
                is_npc_defeat = False

            # Award team defeat points
            self._award_team_defeat_points(attacking_alliance, stronghold, is_npc_defeat)

            # Check if stronghold can be captured (only after NPC defeats)
            if is_npc_defeat and stronghold.check_capturable():
                # FIXED: Use proper protection duration based on game phase
                protection_duration = stronghold.get_reduced_protection_duration(self.game_time)

                capturing_alliance_id = stronghold.capture_by_alliance(
                    attacking_alliance.id,
                    protection_duration_minutes=protection_duration,
                    current_game_time=self.game_time
                )
                if capturing_alliance_id:
                    actual_capturing_alliance = self.get_alliance(capturing_alliance_id)
                    if actual_capturing_alliance:
                        actual_capturing_alliance.add_stronghold(stronghold.id)
                        self._award_capture_points(actual_capturing_alliance, stronghold)
                        self._log_event(f"Stronghold {stronghold.id} captured by Alliance {capturing_alliance_id} (protection: {protection_duration}m)")
                        self.capture_history.append({
                            "stronghold": stronghold.id,
                            "alliance": capturing_alliance_id,
                            "time": self.game_time
                        })

        elif battle.winner == "defender":
            # Defender wins - attacker retreats
            attacking_alliance = self._get_alliance_by_set(battle.attacking_set)
            self._log_event(f"Attack repelled at {stronghold.id} by defenders")

    def _award_team_defeat_points(self, alliance, stronghold, is_npc_defeat):
        """FIXED: Award points for defeating a team at a stronghold per README rules"""
        # Base points based on stronghold level - exact values from README
        base_points = {
            1: 40,  # Level 1 stronghold
            2: 60,  # Level 2 stronghold
            3: 80  # Level 3 stronghold
        }.get(stronghold.level, 40)

        points_awarded = base_points

        # FIXED: First-time bonus only for NPC defeats (40% bonus as implied by README)
        if is_npc_defeat:
            defeat_key = f"{stronghold.id}_npc"
            if defeat_key not in self.first_time_npc_defeats:
                self.first_time_npc_defeats.add(defeat_key)
                bonus_points = int(base_points * 0.4)
                points_awarded += bonus_points
                self._log_event(
                    f"FIRST DEFEAT BONUS! Alliance {alliance.id} gets {bonus_points} bonus points for first NPC defeat at {stronghold.id}")

        # Award points to alliance
        alliance.summit_showdown_points += points_awarded

        team_type = "NPC team" if is_npc_defeat else "garrison team"
        self._log_event(
            f"Alliance {alliance.id} awarded {points_awarded} points for defeating {team_type} at {stronghold.id}")

    def _award_capture_points(self, alliance, stronghold):
        """FIXED: Award points for capturing a stronghold per README rules"""
        # Base occupation points based on stronghold level - exact values from README
        base_points = {
            1: 200,  # Level 1 stronghold
            2: 420,  # Level 2 stronghold
            3: 720  # Level 3 stronghold
        }.get(stronghold.level, 200)

        points_awarded = base_points

        # FIXED: First-time capture bonus (40% bonus)
        if stronghold.id not in self.first_time_captures:
            self.first_time_captures.add(stronghold.id)
            bonus_points = int(base_points * 0.4)
            points_awarded += bonus_points
            self._log_event(
                f"FIRST CAPTURE BONUS! Alliance {alliance.id} gets {bonus_points} bonus points for first capture of {stronghold.id}")

        # Award points to alliance
        alliance.summit_showdown_points += points_awarded

        self._log_event(f"Alliance {alliance.id} awarded {points_awarded} points for capturing {stronghold.id}")

    def _get_alliance_by_set(self, hero_set):
        """Find which alliance owns a hero set"""
        if hero_set.is_npc:
            return None

        for alliance in self.alliances.values():
            for player in alliance.players:
                if hero_set in player.selected_hero_sets:
                    return alliance
        return None

    def advance_to_second_half(self):
        """FIXED: Complete reset for second half per README rules"""
        if self.current_half == 2:
            return  # Already in second half

        self.current_half = 2
        self._log_event("🏆 SECOND HALF BEGINS! All heroes restored to full health and sets available!")

        # FIXED: Complete reset for all alliances
        for alliance in self.alliances.values():
            alliance.restore_all_stamina_for_new_half()
            alliance.reset_all_hero_sets_for_new_half()

            # Verify complete reset
            total_available = 0
            for player in alliance.players:
                for hero_set in player.selected_hero_sets:
                    if not hero_set.consumed_for_attack and not hero_set.is_defeated():
                        total_available += 1

            self._log_event(f"Alliance {alliance.id}: {total_available} hero sets ready for Second Half")

        # FIXED: Respawn NPCs only in neutral strongholds
        npc_respawn_count = 0
        for stronghold in self.strongholds.values():
            if stronghold.respawn_npcs_if_neutral():
                npc_respawn_count += 1
            # FIXED: Clear all protection for second half
            stronghold.end_all_protection()

        self._log_event(f"NPCs respawned in {npc_respawn_count} neutral strongholds")
        self._log_event("All stronghold protection cleared for Second Half")

    def can_alliance_attack_stronghold(self, alliance_id, stronghold_id):
        """FIXED: Enhanced adjacency validation

        Rule: Players can only attack Strongholds adjacent to controlled Strongholds
        """
        alliance = self.get_alliance(alliance_id)
        stronghold = self.get_stronghold(stronghold_id)

        if not alliance or not stronghold:
            return False

        # Cannot attack own strongholds
        if stronghold.controlling_alliance == alliance_id:
            return False

        # Must be adjacent to controlled stronghold
        from .map_layout import get_adjacent_strongholds
        attackable = get_adjacent_strongholds(self.strongholds, alliance.controlled_strongholds)

        return stronghold_id in attackable and stronghold.can_be_attacked()

    def update_stronghold_protections(self):
        """Update protection status for all strongholds using current game time"""
        for stronghold in self.strongholds.values():
            stronghold.update_protection_status(self.game_time)

    def _get_stronghold_control_summary(self):
        """Get summary of stronghold control by alliance"""
        control_summary = {aid: [] for aid in self.alliances.keys()}
        neutral_count = 0

        for stronghold_id, stronghold in self.strongholds.items():
            if stronghold.controlling_alliance:
                control_summary[stronghold.controlling_alliance].append(stronghold_id)
            else:
                neutral_count += 1

        control_summary["neutral"] = neutral_count
        return control_summary

    def _log_event(self, message):
        """Log a game event"""
        timestamp = self.game_time
        self.event_log.append(f"[{timestamp:.1f}] {message}")

    def get_recent_events(self, count=20):
        """Get recent game events"""
        return self.event_log[-count:]

    def can_alliance_attack_stronghold(self, alliance_id, stronghold_id):
        """Check if an alliance can attack a specific stronghold"""
        alliance = self.get_alliance(alliance_id)
        stronghold = self.get_stronghold(stronghold_id)

        if not alliance or not stronghold:
            return False

        # Must be adjacent to controlled stronghold
        from .map_layout import get_adjacent_strongholds
        attackable = get_adjacent_strongholds(self.strongholds, alliance.controlled_strongholds)

        return stronghold_id in attackable and stronghold.can_be_attacked()

    # FIXED: Add method to update all stronghold protections
    def update_stronghold_protections(self):
        """Update protection status for all strongholds"""
        for stronghold in self.strongholds.values():
            stronghold.update_protection_status(self.game_time)

    def to_dict(self):
        """Serialize game state"""
        return {
            "game_time": self.game_time,
            "current_half": self.current_half,
            "alliance_scores": {aid: alliance.summit_showdown_points for aid, alliance in self.alliances.items()},
            "stronghold_control": self._get_stronghold_control_summary(),
            "active_battles": len(self.active_battles)
        }

    @classmethod
    def from_dict(cls, data):
        """Load game state from dict (simplified)"""
        state = cls()
        state.game_time = data.get("game_time", 0.0)
        state.current_half = data.get("current_half", 1)
        return state