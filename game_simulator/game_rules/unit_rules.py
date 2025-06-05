# game_simulator/game_rules/unit_rules.py
import random
import pygame
from ..entities.unit import Unit

def spawn_unit(game_state, tower_id, team_name, unit_type="basic"):
    """Spawn a unit at the specified tower"""
    tower = game_state.get_tower(tower_id)
    team = game_state.teams.get(team_name)
    
    if not tower or not team or tower.owner != team_name:
        return None
    
    # Check if team has enough resources
    unit_cost = get_unit_cost(unit_type)
    if team.resources < unit_cost:
        return None
    
    # Create unit
    unit_id = f"{team_name}_{unit_type}_{random.randint(1000, 9999)}"
    unit = Unit(unit_id, unit_type, team_name)
    unit.pos.x = tower.pos.x
    unit.pos.y = tower.pos.y
    unit.current_tower = tower_id
    
    # Deduct resources and add unit to team
    team.resources -= unit_cost
    team.add_unit(unit)
    tower.units_stationed.append(unit)
    
    return unit

def get_unit_cost(unit_type):
    """Get the resource cost for spawning a unit"""
    costs = {
        "basic": 10,
        "archer": 15,
        "cavalry": 25,
        "siege": 50
    }
    return costs.get(unit_type, 10)

def move_units(game_state, dt):
    """Update movement for all units"""
    for team in game_state.teams.values():
        for unit in team.units:
            if unit.is_alive() and unit.target_pos:
                unit.move_towards_target(dt)
                
                # Check if unit reached target tower
                if unit.target_tower and unit.pos.distance_to(unit.target_pos) < 5:
                    arrive_at_tower(game_state, unit, unit.target_tower)

def send_units_to_tower(game_state, from_tower_id, to_tower_id, team_name, num_units=1):
    """Send units from one tower to another"""
    from_tower = game_state.get_tower(from_tower_id)
    to_tower = game_state.get_tower(to_tower_id)
    team = game_state.teams.get(team_name)
    
    if not from_tower or not to_tower or not team:
        return False
    
    if from_tower.owner != team_name:
        return False
    
    # Get available units at the tower
    available_units = [unit for unit in team.units 
                      if unit.current_tower == from_tower_id and unit.is_alive()]
    
    if len(available_units) < num_units:
        num_units = len(available_units)
    
    if num_units == 0:
        return False
    
    # Send the units
    for i in range(num_units):
        unit = available_units[i]
        unit.target_tower = to_tower_id
        unit.target_pos = pygame.math.Vector2(to_tower.pos.x, to_tower.pos.y)
        unit.current_tower = None
        from_tower.units_stationed.remove(unit)
    
    return True

def arrive_at_tower(game_state, unit, tower_id):
    """Handle unit arriving at a tower"""
    tower = game_state.get_tower(tower_id)
    if not tower:
        return
    
    unit.current_tower = tower_id
    unit.target_tower = None
    unit.target_pos = None
    unit.pos.x = tower.pos.x
    unit.pos.y = tower.pos.y
    
    # Check if this creates a battle
    if tower.owner != unit.team and tower.owner is not None:
        # Enemy tower - start battle
        from .battle_rules import start_battle_at_tower
        start_battle_at_tower(game_state, tower_id)
    else:
        # Friendly or neutral tower
        tower.units_stationed.append(unit)
        if tower.owner is None:
            # Neutral tower - claim it
            tower.owner = unit.team
            game_state.teams[unit.team].add_tower(tower_id)

def get_units_at_tower(game_state, tower_id, team_name=None):
    """Get all units stationed at a specific tower"""
    tower = game_state.get_tower(tower_id)
    if not tower:
        return []
    
    if team_name:
        return [unit for unit in tower.units_stationed 
                if unit.team == team_name and unit.is_alive()]
    else:
        return [unit for unit in tower.units_stationed if unit.is_alive()]