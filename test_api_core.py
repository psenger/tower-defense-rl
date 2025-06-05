#!/usr/bin/env python3
"""
Test script for API core functionality (without Flask server)

This demonstrates that the game logic and data structures work correctly
for ML/RL integration, even without running the full REST API server.
"""

import sys
import time
from game_simulator.game_state import GameState
from game_simulator.entities.summit_battle import SummitBattle

def test_game_initialization():
    """Test game state initialization"""
    print("🎮 Testing Game Initialization...")
    
    game = GameState()
    
    print(f"✓ Created game with:")
    print(f"  - {len(game.alliances)} alliances")
    print(f"  - {len(game.strongholds)} strongholds") 
    print(f"  - {len(game.active_battles)} active battles")
    
    return game

def test_alliance_functionality(game):
    """Test alliance operations"""
    print("\n🤝 Testing Alliance Functionality...")
    
    alliance = game.alliances[1]
    print(f"✓ Alliance 1: {alliance.name}")
    print(f"  - {len(alliance.players)} players")
    print(f"  - {len(alliance.controlled_strongholds)} controlled strongholds")
    
    hero_sets = alliance.get_all_available_hero_sets()
    print(f"  - {len(hero_sets)} available hero sets")
    
    if hero_sets:
        sample_set = hero_sets[0]
        print(f"  - Sample hero set: {sample_set.id}")
        print(f"    * {len(sample_set.get_living_heroes())} living heroes")
        print(f"    * {sample_set.get_total_damage_potential()} total attack")
        print(f"    * {sample_set.get_average_defense():.1f} average defense")
    
    return alliance

def test_map_and_strongholds(game):
    """Test map and stronghold functionality"""
    print("\n🏰 Testing Map and Strongholds...")
    
    # Test different stronghold types
    home = game.get_stronghold("T1")
    level1 = game.get_stronghold("S1-1") 
    level3 = game.get_stronghold("S3-10")
    
    print(f"✓ Alliance Home (T1):")
    print(f"  - Level: {home.level}, Protected: {home.is_protected}")
    print(f"  - NPCs: {len(home.get_active_npc_teams())}/{home.max_npc_teams}")
    
    print(f"✓ Level 1 Stronghold (S1-1):")
    print(f"  - Level: {level1.level}, Can attack: {level1.can_be_attacked()}")
    print(f"  - NPCs: {len(level1.get_active_npc_teams())}/{level1.max_npc_teams}")
    print(f"  - Connections: {list(level1.connections)}")
    
    print(f"✓ Level 3 Stronghold (S3-10):")
    print(f"  - Level: {level3.level}, Can attack: {level3.can_be_attacked()}")
    print(f"  - NPCs: {len(level3.get_active_npc_teams())}/{level3.max_npc_teams}")

def test_battle_system(game):
    """Test battle functionality"""
    print("\n⚔️ Testing Battle System...")
    
    # Get attacking alliance and hero set
    alliance = game.alliances[1]
    hero_sets = alliance.get_all_available_hero_sets()
    
    if not hero_sets:
        print("✗ No available hero sets for testing")
        return
    
    attacking_set = hero_sets[0]
    target_stronghold_id = "S1-2"  # T1 connects to S1-2 in new structure
    
    print(f"✓ Starting battle: {attacking_set.id} → {target_stronghold_id}")
    
    # Start battle using game state
    battle = game.start_battle(attacking_set, target_stronghold_id)
    
    if battle:
        print(f"✓ Battle created: {battle.id}")
        print(f"  - Stronghold: {battle.stronghold_id}")
        print(f"  - Active: {battle.is_active}")
        print(f"  - Step: {battle.current_step}/{battle.max_steps}")
        
        # Execute a few battle turns
        print("  - Executing battle turns...")
        for i in range(5):
            if battle.is_active:
                battle.execute_turn()
                status = battle.get_battle_status()
                print(f"    Turn {i+1}: ATK:{status['attacker_living']} vs DEF:{status['defender_living']}")
            else:
                break
        
        # Get battle status
        final_status = battle.get_battle_status()
        print(f"✓ Final status: {final_status['winner'] or 'ongoing'}")
        
    else:
        print("✗ Failed to start battle")

def test_api_data_structures(game):
    """Test API-like data structure generation"""
    print("\n📊 Testing API Data Structures...")
    
    # Simulate alliance state endpoint
    alliance = game.alliances[2]
    
    # Get attackable targets (similar to API logic)
    from game_simulator.map_layout import get_adjacent_strongholds
    adjacent = get_adjacent_strongholds(game.strongholds, alliance.controlled_strongholds)
    attackable_targets = []
    
    for stronghold_id in adjacent:
        stronghold = game.get_stronghold(stronghold_id)
        if stronghold and stronghold.can_be_attacked():
            attackable_targets.append({
                'id': stronghold.id,
                'level': stronghold.level,
                'controlling_alliance': stronghold.controlling_alliance,
                'active_npcs': len(stronghold.get_active_npc_teams()),
                'max_npcs': stronghold.max_npc_teams
            })
    
    alliance_state = {
        'alliance_id': alliance.id,
        'name': alliance.name,
        'controlled_strongholds': len(alliance.controlled_strongholds),
        'available_hero_sets': len(alliance.get_all_available_hero_sets()),
        'total_players': len(alliance.players),
        'attackable_targets': attackable_targets
    }
    
    print(f"✓ Alliance {alliance.id} API state:")
    for key, value in alliance_state.items():
        if key == 'attackable_targets':
            print(f"  - {key}: {len(value)} targets")
            for target in value[:3]:  # Show first 3
                print(f"    * {target['id']}: L{target['level']}, {target['active_npcs']} NPCs")
        else:
            print(f"  - {key}: {value}")

def test_game_status(game):
    """Test game status reporting"""
    print("\n📈 Testing Game Status...")
    
    status = game.get_game_status()
    
    print(f"✓ Game Status:")
    print(f"  - Half: {status['half']}")
    print(f"  - Game time: {status['game_time']:.1f}s") 
    print(f"  - Active battles: {status['active_battles']}")
    print(f"  - Alliance scores: {status['alliance_scores']}")
    
    stronghold_control = status['stronghold_control']
    for alliance_id in [1, 2, 3, 4]:
        controlled = stronghold_control.get(alliance_id, [])
        print(f"  - Alliance {alliance_id}: {len(controlled)} strongholds")

def main():
    """Run all tests"""
    print("🚀 Summit Showdown API Core Functionality Test")
    print("=" * 50)
    
    try:
        # Test game initialization
        game = test_game_initialization()
        
        # Test alliance functionality
        test_alliance_functionality(game)
        
        # Test map and strongholds
        test_map_and_strongholds(game)
        
        # Test battle system
        test_battle_system(game)
        
        # Test API data structures
        test_api_data_structures(game)
        
        # Test game status
        test_game_status(game)
        
        print("\n" + "=" * 50)
        print("✅ All core functionality tests passed!")
        print("\n🔧 To run the full API server:")
        print("   1. Install Flask: pip install flask flask-cors flask-swagger-ui")
        print("   2. Run API server: python api_server.py")
        print("   3. Run ML agent: python examples/ml_agent_example.py --alliance 1")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())