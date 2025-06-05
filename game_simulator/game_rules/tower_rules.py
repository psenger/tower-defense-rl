# game_simulator/game_rules/tower_rules.py

def update_tower_progress(game_state, dt):
    """Update progress for all player-owned towers"""
    for tower in game_state.towers.values():
        if tower.owner == "player" and tower.progress < 100:
            tower.progress += 5 * dt  # 5 progress units per second
            tower.progress = min(100, tower.progress)

def check_tower_capture(game_state):
    """Check if any towers should be captured based on progress"""
    for tower in game_state.towers.values():
        if tower.progress >= 100 and tower.owner != "player":
            tower.owner = "player"
            tower.progress = 0
            # Update team tower lists
            if "player" in game_state.teams:
                game_state.teams["player"].add_tower(tower.id)
            if "enemy" in game_state.teams and tower.id in game_state.teams["enemy"].towers_controlled:
                game_state.teams["enemy"].remove_tower(tower.id)

def generate_tower_resources(game_state, dt):
    """Generate resources for teams based on towers controlled"""
    for team_name, team in game_state.teams.items():
        # Generate 1 resource per second per tower controlled
        resources_per_second = len(team.towers_controlled)
        team.resources += resources_per_second * dt

def upgrade_tower(game_state, tower_id, upgrade_type):
    """Upgrade a tower if player has enough resources"""
    tower = game_state.get_tower(tower_id)
    if not tower or tower.owner != "player":
        return False
    
    player_team = game_state.teams.get("player")
    if not player_team:
        return False
    
    upgrade_cost = 50  # Base upgrade cost
    
    if player_team.resources >= upgrade_cost:
        player_team.resources -= upgrade_cost
        # Apply upgrade effects (placeholder)
        tower.max_hp = getattr(tower, 'max_hp', 100) + 25
        tower.defense_bonus = getattr(tower, 'defense_bonus', 0) + 5
        return True
    
    return False

def get_connected_towers(game_state, tower_id):
    """Get all towers connected to the given tower"""
    tower = game_state.get_tower(tower_id)
    if not tower:
        return []
    
    connected = []
    for connected_id in tower.connections:
        connected_tower = game_state.get_tower(connected_id)
        if connected_tower:
            connected.append(connected_tower)
    
    return connected