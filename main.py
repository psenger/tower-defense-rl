# main.py
import pygame
from game_simulator.engine import GameEngine
from rl_interface.environment import TowerDefenseEnv # For testing the RL env
from gymnasium.utils.env_checker import check_env # To validate your custom env

def run_simulator():
    """Run the visual game simulator"""
    print("Starting Tower Defense Simulator...")
    engine = GameEngine()
    engine.run()

def test_rl_environment():
    """Test the RL environment setup"""
    print("Testing RL Environment...")
    # env = TowerDefenseEnv(render_mode='human')
    env = TowerDefenseEnv() # Default no rendering for check_env
    
    # Check if the environment follows Gymnasium API
    print("Running Gymnasium environment checker...")
    try:
        check_env(env)
        print("Environment check passed!")
    except Exception as e:
        print(f"Environment check failed: {e}")
        return

    # Simple test loop (optional)
    print("Running simple test episode...")
    obs, info = env.reset()
    print(f"Initial observation shape: {obs.shape}")
    print(f"Action space: {env.action_space}")
    
    for step in range(10):
        action = env.action_space.sample()  # Sample a random action
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {step}: Action={action}, Reward={reward:.3f}, Done={terminated or truncated}")
        
        if terminated or truncated:
            print("Episode finished.")
            obs, info = env.reset()
            break
    
    env.close()
    print("RL environment test completed.")

def run_rl_training_demo():
    """Demonstrate basic RL training setup"""
    print("RL Training Demo - Basic Random Agent")
    env = TowerDefenseEnv()
    
    total_episodes = 5
    for episode in range(total_episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0
        
        while steps < 100:  # Limit steps per episode
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            
            if terminated or truncated:
                break
        
        print(f"Episode {episode + 1}: {steps} steps, Total reward: {episode_reward:.3f}")
    
    env.close()
    print("Demo completed.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "simulator" or mode == "sim":
            # Run the visual simulator
            run_simulator()
        elif mode == "test-rl" or mode == "test":
            # Test the RL environment
            test_rl_environment()
        elif mode == "demo" or mode == "rl-demo":
            # Run RL training demo
            run_rl_training_demo()
        else:
            print("Unknown mode. Available modes:")
            print("  simulator, sim - Run visual simulator")
            print("  test-rl, test - Test RL environment")
            print("  demo, rl-demo - Run RL training demo")
    else:
        # Default: run the visual simulator
        print("Running visual simulator (default mode)")
        print("Use 'python main.py <mode>' for other modes:")
        print("  simulator, sim - Run visual simulator")
        print("  test-rl, test - Test RL environment") 
        print("  demo, rl-demo - Run RL training demo")
        print()
        run_simulator()
