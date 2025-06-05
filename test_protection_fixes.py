#!/usr/bin/env python3
"""
Test script to verify protection countdown and expiration fixes
"""

import pygame
import sys
import time
from game_simulator.engine import GameEngine

def main():
    pygame.init()
    
    # Set up display
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Protection Countdown & Expiration Test")
    clock = pygame.time.Clock()
    
    # Create game engine (includes game state and renderer)
    engine = GameEngine(headless=False)
    
    print("=== PROTECTION COUNTDOWN & EXPIRATION TEST ===")
    print("Testing both fixes:")
    print("1. Countdown timer should update in real-time")
    print("2. Protection should expire after time limit")
    print()
    
    # Create test scenarios with different protection times
    test_strongholds = [
        ("S1-1", 2),   # 2 minutes - should expire quickly
        ("S1-2", 5),   # 5 minutes - medium test
        ("S1-3", 10),  # 10 minutes - longer test
    ]
    
    # Set up test strongholds with different protection durations
    for stronghold_id, minutes in test_strongholds:
        stronghold = engine.game_state.get_stronghold(stronghold_id)
        
        # Simulate capture to trigger protection
        stronghold.npc_defense_teams = []
        stronghold.npc_teams_defeated_by_alliance = {1: 5}
        capturing_alliance_id = stronghold.capture_by_alliance(1, protection_duration_minutes=minutes)
        
        print(f"Protected {stronghold_id} for {minutes} minutes (captured by Alliance {capturing_alliance_id})")
        print(f"  Protection end time: {stronghold.protection_end_time}")
        print(f"  Current time: {time.time()}")
        print(f"  Time remaining: {(stronghold.protection_end_time - time.time()) / 60:.1f} minutes")
    
    print("\nWatch for:")
    print("- Real-time countdown timers updating every second")
    print("- Protection indicators disappearing when time expires")
    print("- 'PROTECTED: Xm' text counting down: 2m -> 1m -> 0m -> gone")
    print("\nPress ESC to exit, SPACE to speed up time 10x")
    
    start_time = time.time()
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Speed up time to test expiration quickly
                    engine.time_scale = 10.0 if engine.time_scale == 1.0 else 1.0
                    print(f"Time scale changed to {engine.time_scale}x")
        
        # Update game engine (this now properly updates protection status)
        engine.update(dt)
        
        # Log protection status changes
        current_time = time.time()
        if int(current_time - start_time) % 30 == 0 and int(current_time * 10) % 10 == 0:  # Every 30 seconds
            print(f"\n--- Status Update (Real Time: {current_time - start_time:.1f}s, Game Time: {engine.game_state.game_time:.1f}s) ---")
            for stronghold_id, _ in test_strongholds:
                stronghold = engine.game_state.get_stronghold(stronghold_id)
                time_remaining = max(0, (stronghold.protection_end_time - time.time()) / 60)
                print(f"{stronghold_id}: Protected={stronghold.is_protected}, Time Remaining={time_remaining:.1f}m")
        
        # Render
        engine.map_renderer.draw(screen, engine.game_state, engine.time_scale)
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n=== TEST COMPLETED ===")
    print("Final status:")
    for stronghold_id, _ in test_strongholds:
        stronghold = engine.game_state.get_stronghold(stronghold_id)
        print(f"{stronghold_id}: Protected={stronghold.is_protected}")

if __name__ == "__main__":
    main()