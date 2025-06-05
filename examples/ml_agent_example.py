#!/usr/bin/env python3
"""
ML/RL Agent Example for Summit Showdown API

This example demonstrates how to create an AI agent that interacts with
the Summit Showdown game through the REST API. It shows:

1. Session management
2. Game state monitoring
3. Decision making
4. Action execution
5. Battle monitoring

Usage:
    python examples/ml_agent_example.py --alliance 1 --agent-name "MyAI"
"""

import requests
import time
import random
import argparse
import json
from typing import Dict, List, Optional, Any


class SummitShowdownAgent:
    """Example AI agent for Summit Showdown"""
    
    def __init__(self, api_base_url: str, alliance_id: int, agent_name: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.alliance_id = alliance_id
        self.agent_name = agent_name
        self.session_id: Optional[str] = None
        self.last_action_time = 0
        self.action_cooldown = 5.0  # Minimum seconds between actions
        
    def create_session(self) -> bool:
        """Create an API session"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/session",
                json={
                    "alliance_id": self.alliance_id,
                    "agent_name": self.agent_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data['session_id']
                print(f"✓ Session created: {self.session_id}")
                print(f"  Alliance: {data['alliance_id']} ({data['agent_name']})")
                return True
            else:
                print(f"✗ Failed to create session: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating session: {e}")
            return False
    
    def end_session(self):
        """End the API session"""
        if not self.session_id:
            return
            
        try:
            response = requests.delete(
                f"{self.api_base_url}/api/session/{self.session_id}",
                timeout=10
            )
            print(f"✓ Session ended")
        except Exception as e:
            print(f"✗ Error ending session: {e}")
    
    def get_game_status(self) -> Optional[Dict]:
        """Get current game status"""
        try:
            response = requests.get(f"{self.api_base_url}/api/game/status", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"✗ Error getting game status: {e}")
            return None
    
    def get_alliance_state(self) -> Optional[Dict]:
        """Get current alliance state"""
        try:
            response = requests.get(
                f"{self.api_base_url}/api/alliances/{self.alliance_id}/state",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"✗ Error getting alliance state: {e}")
            return None
    
    def get_available_hero_sets(self) -> List[Dict]:
        """Get available hero sets for attacks"""
        try:
            response = requests.get(
                f"{self.api_base_url}/api/alliances/{self.alliance_id}/hero-sets",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('available_hero_sets', [])
            return []
        except Exception as e:
            print(f"✗ Error getting hero sets: {e}")
            return []
    
    def launch_attack(self, hero_set_id: str, target_stronghold_id: str) -> bool:
        """Launch an attack"""
        try:
            headers = {}
            if self.session_id:
                headers['X-Session-ID'] = self.session_id
                
            response = requests.post(
                f"{self.api_base_url}/api/alliances/{self.alliance_id}/attack",
                json={
                    "hero_set_id": hero_set_id,
                    "target_stronghold_id": target_stronghold_id
                },
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Attack launched: {hero_set_id} → {target_stronghold_id}")
                print(f"  Battle ID: {data.get('battle_id')}")
                self.last_action_time = time.time()
                return True
            else:
                print(f"✗ Attack failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error launching attack: {e}")
            return False
    
    def get_active_battles(self) -> List[Dict]:
        """Get list of active battles"""
        try:
            response = requests.get(f"{self.api_base_url}/api/battles", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('active_battles', [])
            return []
        except Exception as e:
            print(f"✗ Error getting battles: {e}")
            return []
    
    def make_decision(self) -> bool:
        """Make a strategic decision (example AI logic)"""
        # Check cooldown
        if time.time() - self.last_action_time < self.action_cooldown:
            return False
        
        # Get current state
        alliance_state = self.get_alliance_state()
        if not alliance_state:
            return False
        
        # Get available resources
        hero_sets = self.get_available_hero_sets()
        attackable_targets = alliance_state.get('attackable_targets', [])
        
        if not hero_sets or not attackable_targets:
            print("  No actions available (no hero sets or targets)")
            return False
        
        # Simple strategy: attack the weakest target with strongest hero set
        # Sort targets by difficulty (fewer NPCs + garrison = easier)
        def target_difficulty(target):
            return target.get('active_npcs', 0) + target.get('garrison_count', 0)
        
        easiest_target = min(attackable_targets, key=target_difficulty)
        
        # Sort hero sets by strength (total attack power)
        strongest_set = max(hero_sets, key=lambda hs: hs.get('total_attack', 0))
        
        print(f"  Strategy: Attack {easiest_target['id']} (difficulty: {target_difficulty(easiest_target)}) "
              f"with {strongest_set['id']} (attack: {strongest_set['total_attack']})")
        
        # Execute attack
        return self.launch_attack(strongest_set['id'], easiest_target['id'])
    
    def monitor_battles(self):
        """Monitor ongoing battles"""
        battles = self.get_active_battles()
        if battles:
            print(f"  Active battles: {len(battles)}")
            for battle in battles[:3]:  # Show first 3
                print(f"    {battle['battle_id']}: {battle['stronghold']} "
                      f"(ATK:{battle['attacker_living']} vs DEF:{battle['defender_living']})")
    
    def run(self, duration_seconds: int = 300):
        """Run the agent for a specified duration"""
        print(f"🤖 Starting {self.agent_name} for Alliance {self.alliance_id}")
        
        if not self.create_session():
            return
        
        start_time = time.time()
        last_status_time = 0
        status_interval = 10  # Print status every 10 seconds
        
        try:
            while time.time() - start_time < duration_seconds:
                current_time = time.time()
                
                # Print periodic status
                if current_time - last_status_time >= status_interval:
                    game_status = self.get_game_status()
                    if game_status:
                        print(f"\n📊 Game Status (t={game_status['game_time']:.1f}s, "
                              f"half={game_status['half']}):")
                        
                        alliance_state = self.get_alliance_state()
                        if alliance_state:
                            print(f"  {alliance_state['name']}: "
                                  f"{len(alliance_state['controlled_strongholds'])} strongholds, "
                                  f"score={alliance_state['score']}, "
                                  f"{alliance_state['available_hero_sets']} hero sets available")
                        
                        self.monitor_battles()
                    
                    last_status_time = current_time
                
                # Make decisions
                if self.make_decision():
                    print("  ⚔️ Action taken!")
                
                # Sleep briefly
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Agent interrupted by user")
        
        finally:
            self.end_session()
            print(f"✓ Agent {self.agent_name} finished")


def main():
    parser = argparse.ArgumentParser(description='Summit Showdown ML Agent Example')
    parser.add_argument('--alliance', type=int, choices=[1, 2, 3, 4], required=True,
                        help='Alliance ID (1-4)')
    parser.add_argument('--agent-name', type=str, default='ExampleAI',
                        help='Name for the AI agent')
    parser.add_argument('--api-url', type=str, default='http://localhost:5000',
                        help='API server URL')
    parser.add_argument('--duration', type=int, default=300,
                        help='Duration to run in seconds')
    parser.add_argument('--start-game', action='store_true',
                        help='Start a new game before running agent')
    
    args = parser.parse_args()
    
    # Check API health
    try:
        response = requests.get(f"{args.api_url}/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✓ API server healthy: {health['status']}")
            if not health.get('game_active') and not args.start_game:
                print("⚠️  No active game. Use --start-game to start one.")
                return
        else:
            print(f"✗ API server not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API server at {args.api_url}: {e}")
        print("  Make sure the API server is running: python api_server.py")
        return
    
    # Start game if requested
    if args.start_game:
        try:
            response = requests.post(f"{args.api_url}/api/game/start", timeout=10)
            if response.status_code == 200:
                print("✓ Game started")
            elif 'already running' in response.text.lower():
                print("✓ Game already running")
            else:
                print(f"✗ Failed to start game: {response.text}")
                return
        except Exception as e:
            print(f"✗ Error starting game: {e}")
            return
    
    # Create and run agent
    agent = SummitShowdownAgent(args.api_url, args.alliance, args.agent_name)
    agent.run(args.duration)


if __name__ == '__main__':
    main()