#!/usr/bin/env python3
"""
Test script to verify protection visual indicators work correctly
"""

import pygame
import sys
import time
from game_simulator.game_state import GameState
from game_simulator.graphics.map_renderer import MapRenderer

def main():
    pygame.init()
    
    # Set up display
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Protection Indicator Test")
    clock = pygame.time.Clock()
    
    # Create game state and renderer
    game_state = GameState()
    renderer = MapRenderer()
    
    # Manually trigger a stronghold capture to show protection
    stronghold = game_state.get_stronghold("S1-2")
    print(f"Testing protection on stronghold {stronghold.id}")
    
    # Clear NPCs and simulate capture
    stronghold.npc_defense_teams = []
    stronghold.npc_teams_defeated_by_alliance = {1: 5}
    capturing_alliance_id = stronghold.capture_by_alliance(1, protection_duration_minutes=60)
    
    print(f"Stronghold captured by Alliance {capturing_alliance_id}")
    print(f"Protection status: {stronghold.is_protected}")
    print(f"Protection end time: {stronghold.protection_end_time}")
    print(f"Current time: {time.time()}")
    
    # Test another stronghold manually
    stronghold2 = game_state.get_stronghold("S1-5")
    stronghold2.start_protection(30)  # 30 minute protection for testing
    
    print("\nProtection indicators should now be visible!")
    print("Look for:")
    print("- Pulsing yellow rings around protected strongholds")
    print("- Gold shield icons with cross patterns")
    print("- 'PROTECTED: Xm' text below strongholds")
    print("- Time countdown")
    print("\nPress ESC to exit, SPACE to manually protect S1-1")
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Manually protect S1-1 for demonstration
                    test_stronghold = game_state.get_stronghold("S1-1")
                    test_stronghold.start_protection(45)  # 45 minutes
                    print(f"Manually protected S1-1 for 45 minutes")
        
        # Update protection status
        for stronghold in game_state.strongholds.values():
            stronghold.update_protection_status()
        
        # Render
        renderer.draw(screen, game_state, time_scale=1.0)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Protection visual test completed!")

if __name__ == "__main__":
    main()