# rl_interface/observation_space.py
import numpy as np
from gymnasium import spaces

class ObservationSpaceHelper:
    """Helper class to define and manage observation space for the RL environment"""
    
    def __init__(self, num_towers):
        self.num_towers = num_towers
        # Features per tower: x, y, owner_encoded, progress
        self.features_per_tower = 4
        
        # Total observation size
        self.obs_size = self.num_towers * self.features_per_tower
        
        # Define the observation space
        self.space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.obs_size,),
            dtype=np.float32
        )
    
    def encode_observation(self, game_state):
        """Convert game state to observation vector"""
        obs = []
        
        # Sort tower IDs for consistent ordering
        tower_ids = sorted(game_state.towers.keys())
        
        for tower_id in tower_ids:
            tower = game_state.towers[tower_id]
            
            # Position (normalized to 0-1 based on screen size)
            x_norm = tower.pos.x / 1280.0  # Assuming screen width
            y_norm = tower.pos.y / 720.0   # Assuming screen height
            
            # Owner encoding: -1 = enemy, 0 = neutral, 1 = player
            if tower.owner == "player":
                owner_encoded = 1.0
            elif tower.owner == "enemy":
                owner_encoded = -1.0
            else:
                owner_encoded = 0.0
            
            # Progress (0-1)
            progress_norm = tower.progress / 100.0
            
            obs.extend([x_norm, y_norm, owner_encoded, progress_norm])
        
        return np.array(obs, dtype=np.float32)
    
    def get_space(self):
        """Return the gymnasium space object"""
        return self.space