# game_simulator/engine.py
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

        # Removed non-functional time scrubber
        
        # Test battle generation
        self.test_battle_timer = 0
        
        # Time scrubber - allows fast forwarding through entire match
        self.scrubber_mode = False
        self.target_game_minutes = 0  # Target time in game minutes

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
        """Update game state"""
        # Calculate simulated time based on time scale
        dt_simulated = dt_real * self.time_scale

        self.game_state.game_time += dt_simulated

        if dt_simulated > 0:
            # Check for automatic second half advancement
            self._check_half_advancement()
            
            # Update battles
            self.game_state.update_battles(dt_simulated)
            
            # Auto-generate test battles occasionally
            self.test_battle_timer += dt_simulated
            if self.test_battle_timer > 10.0:  # Every 10 seconds
                self._auto_generate_test_battle()
                self.test_battle_timer = 0

    def _check_half_advancement(self):
        """Check if it's time to advance to second half"""
        # First half duration: 11.5 hours = 41,400 seconds
        first_half_duration = 11.5 * 60 * 60  # 41,400 seconds
        
        if self.game_state.current_half == 1 and self.game_state.game_time >= first_half_duration:
            # Award settlement points for strongholds held at halftime
            self._award_settlement_points()
            
            # Advance to second half
            self.game_state.advance_to_second_half()
    
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
            1: 1800,   # Level 1 stronghold
            2: 3780,   # Level 2 stronghold
            3: 6480    # Level 3 stronghold
        }
        
        for stronghold_id, stronghold in self.game_state.strongholds.items():
            if stronghold.controlling_alliance and not stronghold.is_alliance_home:
                alliance = self.game_state.get_alliance(stronghold.controlling_alliance)
                if alliance:
                    points = settlement_points.get(stronghold.level, 0)
                    alliance.summit_showdown_points += points
                    self.game_state._log_event(f"SETTLEMENT POINTS: Alliance {alliance.id} awarded {points} points for holding {stronghold_id} at halftime")

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
            self.battle_renderer.draw_battle_list(self.screen, self.game_state.active_battles, self.selected_battle_index)
        else:
            # Fallback to map
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