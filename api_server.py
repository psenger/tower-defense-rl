# api_server.py
"""
REST API Server for Summit Showdown ML/RL Integration

This API enables four AI agents to play Summit Showdown by providing:
- Game state access
- Action submission endpoints
- Real-time battle monitoring
- Async game progression

Designed for Machine Learning and Reinforcement Learning applications.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from game_simulator.game_state import GameState
from game_simulator.entities.summit_battle import SummitBattle

app = Flask(__name__)
CORS(app)

# Global game state
game_state: Optional[GameState] = None
game_thread: Optional[threading.Thread] = None
game_running = False
game_speed = 1.0

# API session tracking
api_sessions: Dict[str, Dict] = {}
battle_subscriptions: Dict[str, List[str]] = {}  # session_id -> battle_ids

def init_game():
    """Initialize a new game instance"""
    global game_state
    game_state = GameState()
    return game_state

def game_loop():
    """Background game loop for autonomous progression"""
    global game_state, game_running
    
    while game_running and game_state:
        start_time = time.time()
        
        # Update game state (battles, timers, etc.)
        dt = 0.1 * game_speed  # 100ms updates scaled by speed
        game_state.game_time += dt
        
        if hasattr(game_state, 'update_battles'):
            game_state.update_battles(dt)
        
        # Sleep to maintain update rate
        elapsed = time.time() - start_time
        sleep_time = max(0, 0.1 - elapsed)
        time.sleep(sleep_time)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'game_active': game_state is not None,
        'game_running': game_running
    })

@app.route('/api/session', methods=['POST'])
def create_session():
    """Create a new API session for an AI agent"""
    data = request.get_json() or {}
    
    session_id = str(uuid.uuid4())
    alliance_id = data.get('alliance_id')
    agent_name = data.get('agent_name', f'Agent_{session_id[:8]}')
    
    if not alliance_id or alliance_id not in [1, 2, 3, 4]:
        return jsonify({'error': 'Valid alliance_id (1-4) required'}), 400
    
    api_sessions[session_id] = {
        'alliance_id': alliance_id,
        'agent_name': agent_name,
        'created_at': datetime.utcnow().isoformat(),
        'last_action': None,
        'actions_count': 0
    }
    
    return jsonify({
        'session_id': session_id,
        'alliance_id': alliance_id,
        'agent_name': agent_name,
        'message': 'Session created successfully'
    })

@app.route('/api/session/<session_id>', methods=['DELETE'])
def end_session(session_id: str):
    """End an API session"""
    if session_id in api_sessions:
        del api_sessions[session_id]
        if session_id in battle_subscriptions:
            del battle_subscriptions[session_id]
        return jsonify({'message': 'Session ended'})
    return jsonify({'error': 'Session not found'}), 404

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game instance"""
    global game_state, game_thread, game_running
    
    if game_running:
        return jsonify({'error': 'Game already running'}), 400
    
    game_state = init_game()
    game_running = True
    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()
    
    return jsonify({
        'message': 'Game started',
        'game_time': game_state.game_time,
        'half': game_state.current_half,
        'alliances': {
            alliance_id: alliance.name 
            for alliance_id, alliance in game_state.alliances.items()
        }
    })

@app.route('/api/game/stop', methods=['POST'])
def stop_game():
    """Stop the current game"""
    global game_running
    game_running = False
    return jsonify({'message': 'Game stopped'})

@app.route('/api/game/status', methods=['GET'])
def get_game_status():
    """Get current game status"""
    if not game_state:
        return jsonify({'error': 'No active game'}), 404
    
    status = game_state.get_game_status()
    status['api_sessions'] = len(api_sessions)
    status['game_speed'] = game_speed
    
    return jsonify(status)

@app.route('/api/game/speed', methods=['POST'])
def set_game_speed():
    """Set game simulation speed"""
    global game_speed
    
    data = request.get_json() or {}
    new_speed = data.get('speed', 1.0)
    
    if not isinstance(new_speed, (int, float)) or new_speed < 0:
        return jsonify({'error': 'Speed must be a non-negative number'}), 400
    
    game_speed = float(new_speed)
    return jsonify({'speed': game_speed, 'message': 'Speed updated'})

@app.route('/api/alliances/<int:alliance_id>/state', methods=['GET'])
def get_alliance_state(alliance_id: int):
    """Get detailed state for a specific alliance"""
    if not game_state or alliance_id not in game_state.alliances:
        return jsonify({'error': 'Alliance not found'}), 404
    
    alliance = game_state.alliances[alliance_id]
    
    # Get available hero sets for attacking
    available_hero_sets = alliance.get_all_available_hero_sets()
    
    # Get controlled strongholds
    controlled_strongholds = []
    for stronghold_id in alliance.controlled_strongholds:
        stronghold = game_state.get_stronghold(stronghold_id)
        if stronghold:
            controlled_strongholds.append({
                'id': stronghold.id,
                'level': stronghold.level,
                'position': {'x': stronghold.x, 'y': stronghold.y},
                'is_protected': stronghold.is_protected,
                'garrison_count': len(stronghold.garrisoned_hero_sets),
                'max_garrison': stronghold.max_garrison_size
            })
    
    # Get attackable targets
    from game_simulator.map_layout import get_adjacent_strongholds
    adjacent = get_adjacent_strongholds(game_state.strongholds, alliance.controlled_strongholds)
    attackable_targets = []
    for stronghold_id in adjacent:
        stronghold = game_state.get_stronghold(stronghold_id)
        if stronghold and stronghold.can_be_attacked():
            attackable_targets.append({
                'id': stronghold.id,
                'level': stronghold.level,
                'controlling_alliance': stronghold.controlling_alliance,
                'active_npcs': len(stronghold.get_active_npc_teams()),
                'max_npcs': stronghold.max_npc_teams,
                'garrison_count': len(stronghold.garrisoned_hero_sets)
            })
    
    return jsonify({
        'alliance_id': alliance_id,
        'name': alliance.name,
        'color': alliance.color,
        'controlled_strongholds': controlled_strongholds,
        'available_hero_sets': len(available_hero_sets),
        'total_players': len(alliance.players),
        'attackable_targets': attackable_targets,
        'score': alliance.calculate_score({
            s.id: s.level for s in game_state.strongholds.values()
        })
    })

@app.route('/api/alliances/<int:alliance_id>/hero-sets', methods=['GET'])
def get_alliance_hero_sets(alliance_id: int):
    """Get available hero sets for an alliance"""
    if not game_state or alliance_id not in game_state.alliances:
        return jsonify({'error': 'Alliance not found'}), 404
    
    alliance = game_state.alliances[alliance_id]
    available_sets = alliance.get_all_available_hero_sets()
    
    hero_sets_data = []
    for hero_set in available_sets:
        living_heroes = hero_set.get_living_heroes()
        hero_sets_data.append({
            'id': hero_set.id,
            'owner_id': hero_set.owner_id,
            'living_heroes': len(living_heroes),
            'total_attack': sum(h.attack for h in living_heroes),
            'average_defense': hero_set.get_average_defense(),
            'total_hp': hero_set.get_total_hp(),
            'max_hp': hero_set.get_max_hp(),
            'can_attack': hero_set.can_attack(),
            'is_garrisoned': hero_set.is_garrisoned
        })
    
    return jsonify({
        'alliance_id': alliance_id,
        'available_hero_sets': hero_sets_data,
        'total_count': len(hero_sets_data)
    })

@app.route('/api/alliances/<int:alliance_id>/attack', methods=['POST'])
def launch_attack(alliance_id: int):
    """Launch an attack by an alliance"""
    if not game_state or alliance_id not in game_state.alliances:
        return jsonify({'error': 'Alliance not found'}), 404
    
    data = request.get_json() or {}
    hero_set_id = data.get('hero_set_id')
    target_stronghold_id = data.get('target_stronghold_id')
    
    if not hero_set_id or not target_stronghold_id:
        return jsonify({'error': 'hero_set_id and target_stronghold_id required'}), 400
    
    alliance = game_state.alliances[alliance_id]
    
    # Find the hero set
    attacking_set = None
    for hero_set in alliance.get_all_available_hero_sets():
        if hero_set.id == hero_set_id:
            attacking_set = hero_set
            break
    
    if not attacking_set:
        return jsonify({'error': 'Hero set not found or not available'}), 404
    
    # Validate target
    target_stronghold = game_state.get_stronghold(target_stronghold_id)
    if not target_stronghold:
        return jsonify({'error': 'Target stronghold not found'}), 404
    
    if not target_stronghold.can_be_attacked():
        return jsonify({'error': 'Target stronghold cannot be attacked (protected or invalid)'}), 400
    
    # Check adjacency
    from game_simulator.map_layout import get_adjacent_strongholds
    adjacent = get_adjacent_strongholds(game_state.strongholds, alliance.controlled_strongholds)
    if target_stronghold_id not in adjacent:
        return jsonify({'error': 'Target stronghold is not adjacent to your controlled territory'}), 400
    
    # Start the battle
    battle = game_state.start_battle(attacking_set, target_stronghold_id)
    if not battle:
        return jsonify({'error': 'Failed to start battle'}), 500
    
    # Update session tracking
    session_id = request.headers.get('X-Session-ID')
    if session_id in api_sessions:
        api_sessions[session_id]['last_action'] = {
            'type': 'attack',
            'hero_set_id': hero_set_id,
            'target': target_stronghold_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        api_sessions[session_id]['actions_count'] += 1
    
    return jsonify({
        'battle_id': battle.id,
        'attacking_set': hero_set_id,
        'target_stronghold': target_stronghold_id,
        'message': 'Attack launched successfully'
    })

@app.route('/api/battles', methods=['GET'])
def get_battles():
    """Get list of active battles"""
    if not game_state:
        return jsonify({'error': 'No active game'}), 404
    
    battles_data = []
    for battle in game_state.active_battles:
        status = battle.get_battle_status()
        battles_data.append({
            'battle_id': battle.id,
            'stronghold': battle.stronghold_id,
            'step': status['step'],
            'max_steps': status['max_steps'],
            'is_active': status['is_active'],
            'winner': status['winner'],
            'attacker_living': status['attacker_living'],
            'defender_living': status['defender_living'],
            'current_turn': status['current_turn']
        })
    
    return jsonify({
        'active_battles': battles_data,
        'total_count': len(battles_data)
    })

@app.route('/api/battles/<battle_id>', methods=['GET'])
def get_battle_details(battle_id: str):
    """Get detailed information about a specific battle"""
    if not game_state:
        return jsonify({'error': 'No active game'}), 404
    
    battle = None
    for b in game_state.active_battles:
        if b.id == battle_id:
            battle = b
            break
    
    if not battle:
        return jsonify({'error': 'Battle not found'}), 404
    
    status = battle.get_battle_status()
    recent_log = battle.get_recent_log_entries(20)
    
    return jsonify({
        'battle_id': battle.id,
        'stronghold_id': battle.stronghold_id,
        'status': status,
        'recent_log': recent_log,
        'attacking_set': {
            'id': battle.attacking_set.id,
            'living_heroes': len(battle.attacking_set.get_living_heroes()),
            'total_hp': battle.attacking_set.get_total_hp(),
            'max_hp': battle.attacking_set.get_max_hp()
        },
        'defending_set': {
            'id': battle.defending_set.id,
            'living_heroes': len(battle.defending_set.get_living_heroes()),
            'total_hp': battle.defending_set.get_total_hp(),
            'max_hp': battle.defending_set.get_max_hp()
        }
    })

@app.route('/api/strongholds', methods=['GET'])
def get_strongholds():
    """Get information about all strongholds"""
    if not game_state:
        return jsonify({'error': 'No active game'}), 404
    
    strongholds_data = []
    for stronghold_id, stronghold in game_state.strongholds.items():
        strongholds_data.append({
            'id': stronghold.id,
            'level': stronghold.level,
            'position': {'x': stronghold.x, 'y': stronghold.y},
            'controlling_alliance': stronghold.controlling_alliance,
            'is_alliance_home': stronghold.is_alliance_home,
            'is_protected': stronghold.is_protected,
            'can_be_attacked': stronghold.can_be_attacked(),
            'active_npcs': len(stronghold.get_active_npc_teams()),
            'max_npcs': stronghold.max_npc_teams,
            'garrison_count': len(stronghold.garrisoned_hero_sets),
            'max_garrison': stronghold.max_garrison_size,
            'connections': list(stronghold.connections)
        })
    
    return jsonify({
        'strongholds': strongholds_data,
        'total_count': len(strongholds_data)
    })

@app.route('/api/map/layout', methods=['GET'])
def get_map_layout():
    """Get the map layout for visualization"""
    if not game_state:
        return jsonify({'error': 'No active game'}), 404
    
    # Get map dimensions and stronghold positions
    strongholds = []
    connections = []
    
    for stronghold_id, stronghold in game_state.strongholds.items():
        strongholds.append({
            'id': stronghold.id,
            'x': stronghold.x,
            'y': stronghold.y,
            'level': stronghold.level,
            'is_home': stronghold.is_alliance_home,
            'controlling_alliance': stronghold.controlling_alliance
        })
        
        # Add connections
        for connected_id in stronghold.connections:
            connections.append({
                'from': stronghold.id,
                'to': connected_id
            })
    
    return jsonify({
        'map_width': 1200,
        'map_height': 800,
        'strongholds': strongholds,
        'connections': connections
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Summit Showdown API Server...")
    print("API Documentation will be available at: http://localhost:5000/api/docs")
    print("Health check: http://localhost:5000/api/health")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)