# game_simulator/game_rules/battle_rules.py
from ..entities.battle import Battle

def check_for_new_battles(game_state):
    """Check if any new battles should start"""
    for tower_id, tower in game_state.towers.items():
        # Check if there are opposing units at the same tower
        teams_present = set()
        for unit in tower.units_stationed:
            if unit.is_alive():
                teams_present.add(unit.team)
        
        # If multiple teams are present, start a battle
        if len(teams_present) > 1 and not _is_battle_active_at_tower(game_state, tower_id):
            start_battle_at_tower(game_state, tower_id)

def start_battle_at_tower(game_state, tower_id):
    """Start a battle at the specified tower"""
    tower = game_state.get_tower(tower_id)
    if not tower:
        return None
    
    # Separate units by team
    team_units = {}
    for unit in tower.units_stationed:
        if unit.is_alive():
            if unit.team not in team_units:
                team_units[unit.team] = []
            team_units[unit.team].append(unit)
    
    if len(team_units) < 2:
        return None  # Need at least 2 teams for a battle
    
    # For simplicity, assume first team is attackers, second is defenders
    teams = list(team_units.keys())
    attackers = team_units[teams[0]]
    defenders = team_units[teams[1]]
    
    # Remove units from tower (they're now in battle)
    for unit_list in team_units.values():
        for unit in unit_list:
            if unit in tower.units_stationed:
                tower.units_stationed.remove(unit)
    
    battle = Battle(tower_id, attackers, defenders)
    game_state.add_battle(battle)
    
    return battle

def resolve_active_battles(game_state, dt):
    """Update all active battles"""
    battles_to_remove = []
    
    for battle in game_state.active_battles:
        battle.update(dt)
        
        if battle.is_over():
            resolve_battle_outcome(game_state, battle)
            battles_to_remove.append(battle)
    
    # Remove completed battles
    for battle in battles_to_remove:
        game_state.remove_battle(battle)

def resolve_battle_outcome(game_state, battle):
    """Apply the outcome of a completed battle"""
    tower = game_state.get_tower(battle.tower_id)
    if not tower:
        return
    
    outcome = battle.get_outcome()
    
    if outcome == "attackers":
        # Attackers win - they capture the tower
        if battle.attackers:
            winning_team = battle.attackers[0].team
            tower.owner = winning_team
            tower.progress = 0
            
            # Add surviving attackers back to tower
            survivors = [unit for unit in battle.attackers if unit.is_alive()]
            for unit in survivors:
                unit.current_tower = battle.tower_id
                tower.units_stationed.append(unit)
            
            # Update team tower lists
            game_state.teams[winning_team].add_tower(battle.tower_id)
            
    elif outcome == "defenders":
        # Defenders win - tower remains with defending team
        if battle.defenders:
            defending_team = battle.defenders[0].team
            
            # Add surviving defenders back to tower
            survivors = [unit for unit in battle.defenders if unit.is_alive()]
            for unit in survivors:
                unit.current_tower = battle.tower_id
                tower.units_stationed.append(unit)
    
    # Handle draw case (all units dead)
    # Tower becomes neutral or remains with current owner

def get_battle_at_tower(game_state, tower_id):
    """Get the active battle at a specific tower, if any"""
    for battle in game_state.active_battles:
        if battle.tower_id == tower_id:
            return battle
    return None

def _is_battle_active_at_tower(game_state, tower_id):
    """Check if there's already an active battle at the tower"""
    return get_battle_at_tower(game_state, tower_id) is not None

def calculate_battle_advantage(attackers, defenders):
    """Calculate combat advantages based on unit composition"""
    attacker_strength = sum(unit.attack + unit.hp/10 for unit in attackers if unit.is_alive())
    defender_strength = sum(unit.attack + unit.hp/10 + unit.defense for unit in defenders if unit.is_alive())
    
    # Defenders get a small bonus for holding the position
    defender_strength *= 1.1
    
    return attacker_strength / (defender_strength + 1)  # Avoid division by zero