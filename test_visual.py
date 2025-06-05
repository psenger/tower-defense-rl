#!/usr/bin/env python3
"""
Simple test script to verify the visual simulator works
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_visual_simulator():
    """Test the visual simulator briefly"""
    try:
        from game_simulator.engine import GameEngine
        
        print("Creating game engine...")
        engine = GameEngine(headless=False)
        
        print("Game initialized successfully!")
        print(f"Strongholds: {len(engine.game_state.strongholds)}")
        print(f"Alliances: {len(engine.game_state.alliances)}")
        
        # Quick test of battle generation
        print("Testing battle generation...")
        engine._test_alliance_attack(1)
        
        print(f"Active battles: {len(engine.game_state.active_battles)}")
        
        print("Starting visual simulator...")
        print("Controls:")
        print("  M - Map view")
        print("  L - Battle list")  
        print("  B - Cycle battles")
        print("  1-4 - Test alliance attacks")
        print("  SPACE - Pause/resume")
        print("  ESC - Exit")
        
        # Run for a short time
        engine.run()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_visual_simulator()
    if success:
        print("Visual simulator test completed successfully!")
    else:
        print("Visual simulator test failed!")
        sys.exit(1)