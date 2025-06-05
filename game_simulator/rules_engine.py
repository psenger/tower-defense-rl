# game_simulator/rules_engine.py
from .game_rules import tower_rules, battle_rules, unit_rules
from .game_rules.event_system import create_game_event_system

class RulesEngine:
    def __init__(self, game_state):
        self.game_state = game_state
        self.event_system = create_game_event_system()

    def update(self, dt_simulated):
        # This is where you orchestrate rule application
        # Could be event-driven or state-driven

        # Update tower progress for player towers
        tower_rules.update_tower_progress(self.game_state, dt_simulated)
        
        # Check for tower captures
        tower_rules.check_tower_capture(self.game_state)
        
        # Generate resources for teams
        tower_rules.generate_tower_resources(self.game_state, dt_simulated)
        
        # Move units towards their targets
        unit_rules.move_units(self.game_state, dt_simulated)
        
        # Check for new battles
        battle_rules.check_for_new_battles(self.game_state)
        
        # Resolve active battles
        battle_rules.resolve_active_battles(self.game_state, dt_simulated)
        
        # Update event system
        self.event_system.update(dt_simulated, self.game_state)
        
        # Update tower visuals based on current state
        for tower in self.game_state.towers.values():
            tower.update_visuals()
    
    def apply_player_action(self, action):
        """Apply a player action to the game state"""
        if action.get("type") == "send_units":
            from_tower = action.get("from_tower")
            to_tower = action.get("to_tower")
            num_units = action.get("num_units", 1)
            
            if from_tower and to_tower:
                return unit_rules.send_units_to_tower(
                    self.game_state, from_tower, to_tower, "player", num_units
                )
        
        elif action.get("type") == "spawn_unit":
            tower_id = action.get("tower_id")
            unit_type = action.get("unit_type", "basic")
            
            if tower_id:
                return unit_rules.spawn_unit(
                    self.game_state, tower_id, "player", unit_type
                )
        
        elif action.get("type") == "upgrade_tower":
            tower_id = action.get("tower_id")
            upgrade_type = action.get("upgrade_type", "basic")
            
            if tower_id:
                return tower_rules.upgrade_tower(
                    self.game_state, tower_id, upgrade_type
                )
        
        return False
    
    def get_valid_actions(self, team_name="player"):
        """Get list of valid actions for the specified team"""
        valid_actions = []
        team = self.game_state.teams.get(team_name)
        
        if not team:
            return valid_actions
        
        # Always allow do nothing
        valid_actions.append({"type": "do_nothing"})
        
        # Get player-controlled towers
        player_towers = [tid for tid, tower in self.game_state.towers.items() 
                        if tower.owner == team_name]
        
        for tower_id in player_towers:
            tower = self.game_state.get_tower(tower_id)
            
            # Can spawn units if have resources
            unit_cost = unit_rules.get_unit_cost("basic")
            if team.resources >= unit_cost:
                valid_actions.append({
                    "type": "spawn_unit",
                    "tower_id": tower_id,
                    "unit_type": "basic"
                })
            
            # Can send units to connected towers if have units
            if tower.units_stationed:
                for connected_id in tower.connections:
                    valid_actions.append({
                        "type": "send_units",
                        "from_tower": tower_id,
                        "to_tower": connected_id,
                        "num_units": 1
                    })
            
            # Can upgrade tower if have resources
            upgrade_cost = 50
            if team.resources >= upgrade_cost:
                valid_actions.append({
                    "type": "upgrade_tower",
                    "tower_id": tower_id,
                    "upgrade_type": "basic"
                })
        
        return valid_actions