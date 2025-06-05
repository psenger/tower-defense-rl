# rl_interface/environment.py
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import sys
import os

# Add the parent directory to the path so we can import game_simulator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_simulator.engine import GameEngine
import config

class TowerDefenseEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': config.FPS}

    def __init__(self, render_mode=None, game_config=None): # game_config can pass params to GameEngine
        super().__init__()
        self.render_mode = render_mode

        # Initialize your game engine.
        # For RL, often run in 'headless' mode (no Pygame window).
        # The 'human' render_mode will create its own window via engine.run()
        self.game_engine = GameEngine(headless=(render_mode != 'human'))

        # Define action_space (what the AI can do)
        # Example: Discrete action space - N actions.
        # Action 0: Do nothing
        # Action 1: Send units from player tower 1 to enemy tower X
        # This needs careful design based on your game!
        # For now, a placeholder:
        self.num_towers = len(self.game_engine.game_state.towers)
        # self.action_space = spaces.Discrete(1 + self.num_towers * self.num_towers) # Example: do nothing OR send from T_i to T_j
        self.action_space = spaces.Discrete(5) # Placeholder: 5 distinct actions

        # Define observation_space (what the AI sees)
        # Example: Box space for continuous features.
        # [tower1_x, tower1_y, tower1_owner, tower1_progress, tower2_x, ...]
        # This must match game_engine.get_observation() output!
        # For now, a placeholder based on the simple get_observation:
        num_features_per_tower = 4
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, # Adjust low/high if features are bounded (e.g. progress 0-1)
            shape=(self.num_towers * num_features_per_tower,),
            dtype=np.float32
        )

        if self.render_mode == "human":
            # Initialize Pygame window if rendering for humans (done by GameEngine)
            pass


    def _get_obs(self):
        return np.array(self.game_engine.get_observation(), dtype=np.float32)

    def _get_info(self):
        # Auxiliary information, not used for training but good for debugging
        return {"game_time": self.game_engine.game_state.game_time}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed) # Important for reproducibility

        observation_list = self.game_engine.reset_game()
        observation = np.array(observation_list, dtype=np.float32)
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame() # Initial render

        return observation, info

    def step(self, action):
        # 1. Apply action to the game
        self.game_engine.apply_action(action)

        # 2. Advance the game simulation by one (or more) step(s)
        # How much game time passes per RL step? This is a design choice.
        # For now, let's assume one RL step corresponds to a small fixed amount of game time.
        # Or, you could run the game engine's update loop for a fixed number of frames.
        simulated_dt_per_rl_step = 0.1 # e.g., 0.1 game seconds
        self.game_engine.update(simulated_dt_per_rl_step / self.game_engine.time_scale) # Pass real_dt that results in simulated_dt

        # 3. Get new observation, reward, done, truncated, info
        observation = self._get_obs()
        reward = self.game_engine.calculate_reward()
        terminated = self.game_engine.is_done() # Game ended based on win/loss
        truncated = False # Game ended due to time limit or other external factor (not yet implemented)
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame_rgb()
        elif self.render_mode == "human":
            self._render_frame() # GameEngine handles its own rendering loop and display
            return # For human mode, render is usually called by step

    def _render_frame(self): # For human mode, called by step
        if self.game_engine.headless: # Should not happen if render_mode is human
            return
        # The game engine's own loop handles input and rendering.
        # We just need to make sure Pygame events are processed if we're not running the full engine.run()
        self.game_engine._handle_input() # Process inputs like closing window
        self.game_engine.render()      # Call engine's render method
        # self.game_engine.clock.tick(self.metadata['render_fps']) # Control FPS if needed here

    def _render_frame_rgb(self): # For rgb_array mode
        # This requires rendering to an offscreen Pygame surface and then converting to numpy array
        if self.game_engine.headless: # Temporarily un-headless or use an offscreen buffer
            temp_screen = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        else:
            temp_screen = self.game_engine.screen

        # Perform rendering logic onto temp_screen
        if self.game_engine.current_view == "map":
            temp_screen.fill(config.MAP_BACKGROUND_COLOR)
            self.game_engine.map_renderer.draw(temp_screen, self.game_engine.game_state)
        # ... handle battle view ...
        # ... render UI overlays ...

        return np.transpose(
            pygame.surfarray.array3d(temp_screen), axes=(1, 0, 2)
        ) # HWC format

    def close(self):
        if not self.game_engine.headless:
            pygame.quit()