# rl_interface/action_space.py
from gymnasium import spaces

class ActionSpaceHelper:
    """Helper class to define and manage action space for the RL environment"""
    
    def __init__(self, num_towers):
        self.num_towers = num_towers
        
        # Define possible actions:
        # 0: Do nothing
        # 1-N: Send units from player tower to specific tower
        # This can be expanded based on game mechanics
        self.num_actions = 1 + num_towers  # Do nothing + send to each tower
        
        self.space = spaces.Discrete(self.num_actions)
        
        # Create action mappings
        self.action_mappings = self._create_action_mappings()
    
    def _create_action_mappings(self):
        """Create mappings from action indices to game actions"""
        mappings = {}
        mappings[0] = {"type": "do_nothing"}
        
        action_idx = 1
        # For simplicity, assume we can send units to any tower
        for i in range(self.num_towers):
            mappings[action_idx] = {
                "type": "send_units",
                "target_tower_idx": i
            }
            action_idx += 1
            
        return mappings
    
    def decode_action(self, action_idx):
        """Convert action index to game action"""
        if action_idx in self.action_mappings:
            return self.action_mappings[action_idx]
        else:
            return {"type": "do_nothing"}  # Default fallback
    
    def get_space(self):
        """Return the gymnasium space object"""
        return self.space
    
    def get_action_description(self, action_idx):
        """Get human-readable description of action"""
        action = self.decode_action(action_idx)
        if action["type"] == "do_nothing":
            return "Do nothing"
        elif action["type"] == "send_units":
            return f"Send units to tower {action['target_tower_idx']}"
        else:
            return "Unknown action"