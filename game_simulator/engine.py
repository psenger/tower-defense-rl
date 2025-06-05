# game_simulator/engine.py - COMPLETE FILE WITH PROTECTION FIXES

import pygame
import random
import config
from .game_state import GameState
from .graphics.map_renderer import MapRenderer
from .graphics.battle_renderer import BattleRenderer
from .graphics.ui_elements import UIElements


class GameEngine:
    def __init__(self, headless=False):
        self.headless = headless
        if not self.headless:
            pygame.init()
            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            pygame.display.set_caption("Summit Showdown Simulator")
            self.clock = pygame.time.Clock()
            self.map_renderer = MapRenderer()
            self.battle_renderer = BattleRenderer()
            self.ui_elements = UIElements()

        self.game_state = GameState()
        self.game_state.engine = self  # Reference for renderer to access scrubber mode

        self.running = False
        self.time_scale = config.INITIAL_TIME_SCALE
        self.current_view = "map"  # "map", "battle", "battle_list"
        self.active_battle_to_view = None
        self.selected_battle_index = 0

        # Enhanced battle generation for realistic alliance warfare
        self.alliance_battle_timer = 0
        self.battle_frequency = 30.0  # Base seconds between alliance actions
        self.alliance_aggression = {1: 1.0, 2: 1.2, 3: 0.8, 4: 1.1}  # Different aggression levels

        # Time scrubber
        self.scrubber_mode = False
        self.target_game_minutes = 0

    def _handle_input(self):
        if self.headless:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:  # Toggle pause
                    self.time_scale = 0.0 if self.time_scale > 0.0 else 1.0
                elif event.key == pygame.K_RIGHT:  # Speed up or scrub forward
                    if self.scrubber_mode:
                        self._scrub_forward()
                    else:
                        self.time_scale = min(10000.0, self.time_scale * 2 if self.time_scale > 0 else 0.1)
                elif event.key == pygame.K_LEFT:  # Slow down or scrub backward
                    if self.scrubber_mode:
                        self._scrub_backward()
                    else:
                        self.time_scale = max(0.0, self.time_scale / 2)
                elif event.key == pygame.K_s:  # Toggle scrubber mode
                    self._toggle_scrubber_mode()
                elif event.key == pygame.K_f:  # Fast view - entire match in 5 minutes
                    self._set_fast_view_mode()
                elif event.key == pygame.K_m:  # Map view
                    self.current_view = "map"
                elif event.key == pygame.K_l:  # Battle list view
                    self.current_view = "battle_list"
                    self.selected_battle_index = 0
                elif event.key == pygame.K_b:  # Cycle through battles
                    self._cycle_battle_view()

                # Battle list navigation (check this first to avoid conflicts)
                elif self.current_view == "battle_list":
                    if event.key == pygame.K_UP:
                        self.selected_battle_index = max(0, self.selected_battle_index - 1)
                    elif event.key == pygame.K_DOWN:
                        max_index = len(self.game_state.active_battles) - 1
                        self.selected_battle_index = min(max_index, self.selected_battle_index + 1)
                    elif event.key == pygame.K_RETURN and self.game_state.active_battles:
                        if 0 <= self.selected_battle_index < len(self.game_state.active_battles):
                            self.active_battle_to_view = self.game_state.active_battles[self.selected_battle_index]
                            self.current_view = "battle"
                    # Test alliance attacks (1-4 keys) - also work in battle list
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        alliance_id = event.key - pygame.K_0
                        self._test_alliance_attack(alliance_id)

                # Test alliance attacks (1-4 keys) - for other views
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    alliance_id = event.key - pygame.K_0
                    self._test_alliance_attack(alliance_id)

    def _cycle_battle_view(self):
        """Cycle through active battles or return to map"""
        if not self.game_state.active_battles:
            self.current_view = "map"
            return

        if self.current_view != "battle" or not self.active_battle_to_view:
            # Show first battle
            self.active_battle_to_view = self.game_state.active_battles[0]
            self.current_view = "battle"
        else:
            # Find current battle index and go to next
            try:
                current_index = self.game_state.active_battles.index(self.active_battle_to_view)
                next_index = (current_index + 1) % len(self.game_state.active_battles)
                self.active_battle_to_view = self.game_state.active_battles[next_index]
            except ValueError:
                # Current battle not in list anymore, show first
                self.active_battle_to_view = self.game_state.active_battles[0]

    def _test_alliance_attack(self, alliance_id):
        """Generate a test attack by the specified alliance"""
        alliance = self.game_state.get_alliance(alliance_id)
        if not alliance:
            return

        # Find available hero sets
        available_sets = alliance.get_all_available_hero_sets()
        if not available_sets:
            print(f"Alliance {alliance_id} has no available hero sets")
            return

        # Find attackable strongholds
        from .map_layout import get_adjacent_strongholds
        attackable = get_adjacent_strongholds(self.game_state.strongholds, alliance.controlled_strongholds)
        valid_targets = [sid for sid in attackable if self.game_state.get_stronghold(sid).can_be_attacked()]

        if not valid_targets:
            print(f"Alliance {alliance_id} has no valid targets to attack")
            return

        # Pick random attacking set and target
        attacking_set = random.choice(available_sets)
        target_stronghold_id = random.choice(valid_targets)

        # Start the battle
        battle = self.game_state.start_battle(attacking_set, target_stronghold_id)
        if battle:
            print(f"Test battle started: Alliance {alliance_id} attacks {target_stronghold_id}")

    def update(self, dt_real):
        """ENHANCED: Update with realistic alliance warfare"""
        # Calculate simulated time based on time scale
        dt_simulated = dt_real * self.time_scale

        self.game_state.game_time += dt_simulated

        if dt_simulated > 0:
            # Check for automatic second half advancement
            self._check_half_advancement()

            # Update battles
            self.game_state.update_battles(dt_simulated)

            # Update stronghold protection status
            for stronghold in self.game_state.strongholds.values():
                stronghold.update_protection_status(self.game_state.game_time)

            # ENHANCED: Generate realistic alliance warfare
            self.alliance_battle_timer += dt_simulated
            if self.alliance_battle_timer > self._get_next_battle_interval():
                self._generate_alliance_warfare()
                self.alliance_battle_timer = 0

    def _get_next_battle_interval(self):
        """Calculate dynamic battle frequency based on game state"""
        base_interval = self.battle_frequency

        # More frequent battles as game progresses
        game_minutes = self.game_state.game_time / 60.0
        if game_minutes > 300:  # After 5 hours, increase frequency
            base_interval *= 0.5
        elif game_minutes > 600:  # After 10 hours, very frequent
            base_interval *= 0.3

        # More battles when fewer strongholds are neutral
        neutral_count = sum(1 for s in self.game_state.strongholds.values()
                          if s.is_neutral() and not s.is_alliance_home)
        if neutral_count < 10:  # High competition for remaining neutrals
            base_interval *= 0.6

        return base_interval + random.uniform(-5, 5)  # Add randomness

    def _generate_alliance_warfare(self):
        """ENHANCED: Generate realistic strategic alliance battles"""
        if len(self.game_state.active_battles) >= 6:  # Limit concurrent battles
            return

        # Pick an attacking alliance based on aggression and capability
        attacking_alliance = self._select_attacking_alliance()
        if not attacking_alliance:
            return

        # Find strategic targets
        targets = self._find_strategic_targets(attacking_alliance)
        if not targets:
            return

        # Pick target based on strategic value
        target_stronghold_id = self._select_best_target(attacking_alliance, targets)
        if not target_stronghold_id:
            return

        # Execute the attack
        available_sets = attacking_alliance.get_all_available_hero_sets()
        if available_sets:
            attacking_set = random.choice(available_sets)
            battle = self.game_state.start_battle(attacking_set, target_stronghold_id)
            if battle:
                print(f"⚔️  Alliance {attacking_alliance.id} ({attacking_alliance.name}) attacks {target_stronghold_id}")

    def _select_attacking_alliance(self):
        """Select which alliance should attack based on capability and aggression"""
        candidates = []

        for alliance_id, alliance in self.game_state.alliances.items():
            available_sets = len(alliance.get_all_available_hero_sets())
            if available_sets == 0:
                continue

            # Calculate attack likelihood based on multiple factors
            aggression = self.alliance_aggression.get(alliance_id, 1.0)
            capability = available_sets / 10.0  # More sets = more likely to attack

            # Strategic pressure - alliances with fewer strongholds are more aggressive
            stronghold_count = len(alliance.controlled_strongholds)
            pressure = 1.5 if stronghold_count <= 2 else 1.0

            attack_score = aggression * capability * pressure
            candidates.append((alliance, attack_score))

        if not candidates:
            return None

        # Weighted random selection
        total_score = sum(score for _, score in candidates)
        if total_score <= 0:
            return random.choice([alliance for alliance, _ in candidates])

        rand_val = random.random() * total_score
        current_sum = 0
        for alliance, score in candidates:
            current_sum += score
            if rand_val <= current_sum:
                return alliance

        return candidates[0][0]  # Fallback

    def _find_strategic_targets(self, attacking_alliance):
        """Find valid strategic targets for an alliance"""
        from .map_layout import get_adjacent_strongholds

        # Get strongholds adjacent to alliance's controlled territory
        adjacents = get_adjacent_strongholds(
            self.game_state.strongholds,
            attacking_alliance.controlled_strongholds
        )

        # Filter to attackable strongholds
        valid_targets = []
        for stronghold_id in adjacents:
            stronghold = self.game_state.get_stronghold(stronghold_id)
            if stronghold and stronghold.can_be_attacked():
                valid_targets.append(stronghold_id)

        return valid_targets

    def _select_best_target(self, attacking_alliance, targets):
        """Select the best target based on strategic value"""
        if not targets:
            return None

        target_scores = []

        for stronghold_id in targets:
            stronghold = self.game_state.get_stronghold(stronghold_id)
            if not stronghold:
                continue

            score = 0

            # Base value by level
            score += stronghold.level * 10

            # Prefer neutral strongholds over enemy-controlled
            if stronghold.is_neutral():
                score += 20
            elif stronghold.controlling_alliance != attacking_alliance.id:
                score += 15  # Enemy strongholds valuable but harder

            # Prefer weakly defended strongholds
            total_defenders = len(stronghold.get_all_defending_sets())
            score += max(0, 15 - total_defenders)  # Prefer fewer defenders

            # Strategic position bonus for Level 3 and central strongholds
            if stronghold.level == 3:
                score += 25  # High value target
            elif stronghold.id in ["S2-9", "S2-11"]:  # Level 2 strongholds
                score += 15

            target_scores.append((stronghold_id, score))

        if not target_scores:
            return random.choice(targets)

        # Weighted selection favoring higher scores
        total_score = sum(score for _, score in target_scores)
        if total_score <= 0:
            return random.choice(targets)

        rand_val = random.random() * total_score
        current_sum = 0
        for stronghold_id, score in target_scores:
            current_sum += score
            if rand_val <= current_sum:
                return stronghold_id

        return target_scores[0][0]  # Fallback to highest scoring

    def _check_half_advancement(self):
        """Check for half advancement and ensure proper hero reset"""
        first_half_duration = 11.5 * 60 * 60  # 41,400 seconds
        total_game_duration = 23.5 * 60 * 60  # 84,600 seconds

        if self.game_state.current_half == 1 and self.game_state.game_time >= first_half_duration:
            print("🏆 HALFTIME! All heroes reset and ready for Second Half combat!")

            # Award settlement points
            self._award_settlement_points()

            # Advance to second half
            self.game_state.advance_to_second_half()

            # Clear all protection
            for stronghold in self.game_state.strongholds.values():
                stronghold.end_all_protection()

            # Reset battle frequency for intense second half
            self.battle_frequency = 20.0  # More frequent battles in second half

        elif self.game_state.current_half == 2 and self.game_state.game_time >= total_game_duration:
            self._end_game()

    def _test_alliance_attack(self, alliance_id):
        """Enhanced test attack that considers strategy"""
        alliance = self.game_state.get_alliance(alliance_id)
        if not alliance:
            return

        available_sets = alliance.get_all_available_hero_sets()
        if not available_sets:
            print(f"Alliance {alliance_id} has no available hero sets")
            return

        # Use the same strategic target selection
        targets = self._find_strategic_targets(alliance)
        if not targets:
            print(f"Alliance {alliance_id} has no valid targets to attack")
            return

        target_stronghold_id = self._select_best_target(alliance, targets)
        attacking_set = random.choice(available_sets)

        battle = self.game_state.start_battle(attacking_set, target_stronghold_id)
        if battle:
            print(f"🎯 Manual test: Alliance {alliance_id} attacks {target_stronghold_id}")

    def _end_game(self):
        """ADDED: End the game and declare winner"""
        self.game_state.game_ended = True
        self.game_state.winner = self._determine_winner()

        self.game_state._log_event("=== GAME ENDED ===")
        self.game_state._log_event(f"Winner: {self.game_state.winner}")
        self._log_final_scores()

        # Pause the game
        self.time_scale = 0.0

        print(f"\n🏆 GAME OVER! Winner: {self.game_state.winner}")
        print("Game has been paused. Press ESC to exit.")

    def _determine_winner(self):
        """ADDED: Determine the winning alliance based on Summit Showdown Points"""
        if not self.game_state.alliances:
            return "No Winner"

        # Find alliance with highest score
        winner_alliance = max(
            self.game_state.alliances.values(),
            key=lambda alliance: alliance.summit_showdown_points
        )

        winner_score = winner_alliance.summit_showdown_points

        # Check for ties
        tied_alliances = [
            alliance for alliance in self.game_state.alliances.values()
            if alliance.summit_showdown_points == winner_score
        ]

        if len(tied_alliances) > 1:
            tied_names = [alliance.name for alliance in tied_alliances]
            return f"TIE: {', '.join(tied_names)} ({winner_score} points)"
        else:
            return f"{winner_alliance.name} ({winner_score} points)"

    def _log_final_scores(self):
        """ADDED: Log final scores for all alliances"""
        self.game_state._log_event("=== FINAL SCORES ===")

        # Sort alliances by score (highest first)
        sorted_alliances = sorted(
            self.game_state.alliances.values(),
            key=lambda alliance: alliance.summit_showdown_points,
            reverse=True
        )

        for i, alliance in enumerate(sorted_alliances, 1):
            strongholds_controlled = len(alliance.controlled_strongholds)
            self.game_state._log_event(
                f"{i}. {alliance.name}: {alliance.summit_showdown_points} points "
                f"({strongholds_controlled} strongholds)"
            )

    def _toggle_scrubber_mode(self):
        """Toggle between normal speed control and time scrubber mode"""
        self.scrubber_mode = not self.scrubber_mode
        if self.scrubber_mode:
            self.time_scale = 0.0  # Pause when entering scrubber mode
            self.target_game_minutes = self.game_state.game_time / 60.0  # Current time in minutes

    def _scrub_forward(self):
        """Scrub forward by 10 game minutes"""
        if self.scrubber_mode:
            self.target_game_minutes += 10
            max_minutes = (23 * 60) + 30  # 23 hours 30 minutes total game time
            self.target_game_minutes = min(self.target_game_minutes, max_minutes)
            self._jump_to_target_time()

    def _scrub_backward(self):
        """Scrub backward by 10 game minutes"""
        if self.scrubber_mode:
            self.target_game_minutes -= 10
            self.target_game_minutes = max(0, self.target_game_minutes)
            self._jump_to_target_time()

    def _jump_to_target_time(self):
        """Jump to the target time instantly"""
        target_seconds = self.target_game_minutes * 60
        current_seconds = self.game_state.game_time

        if target_seconds > current_seconds:
            # Fast forward - use very high time scale
            time_diff = target_seconds - current_seconds
            self.time_scale = min(10000.0, time_diff * 10)  # Very fast forward
        else:
            # Going backward - reset and fast forward to target
            self._reset_to_time(target_seconds)

    def _reset_to_time(self, target_seconds):
        """Reset game and fast forward to specific time (simplified)"""
        # For now, just set the time directly
        # In a full implementation, you'd replay events to the target time
        self.game_state.game_time = target_seconds
        if target_seconds >= (11.5 * 60 * 60) and self.game_state.current_half == 1:
            self.game_state.advance_to_second_half()

    def _set_fast_view_mode(self):
        """Set time scale to view entire match in 5 minutes"""
        # Total game time: 23 hours 30 minutes = 84,600 seconds
        # To view in 5 minutes (300 seconds): scale = 84,600 / 300 = 282x
        self.time_scale = 282.0
        self.scrubber_mode = False

    def _award_settlement_points(self):
        """Award settlement points for strongholds held at halftime"""
        settlement_points = {
            1: 1800,  # Level 1 stronghold
            2: 3780,  # Level 2 stronghold
            3: 6480  # Level 3 stronghold
        }

        for stronghold_id, stronghold in self.game_state.strongholds.items():
            if stronghold.controlling_alliance and not stronghold.is_alliance_home:
                alliance = self.game_state.get_alliance(stronghold.controlling_alliance)
                if alliance:
                    points = settlement_points.get(stronghold.level, 0)
                    alliance.summit_showdown_points += points
                    self.game_state._log_event(
                        f"SETTLEMENT POINTS: Alliance {alliance.id} awarded {points} points for holding {stronghold_id} at halftime")

    def _auto_generate_test_battle(self):
        """Automatically generate a test battle for demonstration"""
        if len(self.game_state.active_battles) >= 3:  # Limit concurrent battles
            return

        # Pick a random alliance to attack
        alliance_id = random.randint(1, 4)
        self._test_alliance_attack(alliance_id)

    def render(self):
        if self.headless:
            return

        if self.current_view == "map":
            self.map_renderer.draw(self.screen, self.game_state, self.time_scale)
        elif self.current_view == "battle" and self.active_battle_to_view:
            self.battle_renderer.draw(self.screen, self.active_battle_to_view, self.game_state)
        elif self.current_view == "battle_list":
            self.battle_renderer.draw_battle_list(self.screen, self.game_state.active_battles,
                                                  self.selected_battle_index)
        else:
            self.map_renderer.draw(self.screen, self.game_state, self.time_scale)

        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            dt_real = self.clock.tick(config.FPS) / 1000.0 if not self.headless else 0.016

            if not self.headless:
                self._handle_input()

            self.update(dt_real)

            if not self.headless:
                self.render()

        if not self.headless:
            pygame.quit()

    # --- Methods for RL Interface ---
    def get_observation(self):
        """Get observation for RL (simplified for now)"""
        obs_list = []

        # Stronghold states
        for stronghold_id in sorted(self.game_state.strongholds.keys()):
            stronghold = self.game_state.strongholds[stronghold_id]

            # Position (normalized)
            x_norm = stronghold.x / config.SCREEN_WIDTH
            y_norm = stronghold.y / config.SCREEN_HEIGHT

            # Alliance control (1-4 for alliances, 0 for neutral)
            alliance_control = stronghold.controlling_alliance if stronghold.controlling_alliance else 0

            # NPC count (normalized)
            npc_count_norm = len(stronghold.get_active_npc_teams()) / stronghold.max_npc_teams

            obs_list.extend([x_norm, y_norm, alliance_control, npc_count_norm])

        return obs_list

    def apply_action(self, action):
        """Apply RL action (placeholder)"""
        print(f"Action received: {action}")
        # TODO: Implement action decoding for RL
        pass

    def calculate_reward(self):
        """Calculate reward for RL (placeholder)"""
        reward = 0
        # Simple reward based on stronghold control
        for alliance_id, alliance in self.game_state.alliances.items():
            if alliance_id == 1:  # Assume alliance 1 is the RL agent
                reward += len(alliance.controlled_strongholds) * 0.1
        return reward

    def is_done(self):
        """Check if episode is done (placeholder)"""
        # Game could end based on time limit or domination
        return self.game_state.game_time > 300  # 5 minutes for testing

    def reset_game(self):
        """Reset game state"""
        self.game_state = GameState()
        self.time_scale = config.INITIAL_TIME_SCALE
        self.current_view = "map"
        self.active_battle_to_view = None
        self.test_battle_timer = 0
        return self.get_observation()