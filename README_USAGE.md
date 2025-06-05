# Tower Defense RL - Usage Guide

## Quick Start

### Environment Setup
```bash
# Activate the conda environment
conda activate tower_sim

# Or use the provided script
./start-shell.sh
```

### Running the Simulator

#### Visual Simulator (Default)
```bash
python main.py
# or
python main.py simulator
```

**Controls:**
- `SPACE` - Pause/Resume simulation
- `LEFT/RIGHT` arrows - Adjust simulation speed (0.1x to 10x)
- `M` - Switch to map view
- `B` - Cycle through active battles
- `L` - Battle list view (navigate with UP/DOWN, ENTER to select)
- `1-4` - Trigger test attacks by each alliance
- `ESC` - Exit

**Map Layout:**
- Now accurately reflects the provided SVG map structure
- 4 Alliance Homes (corners) + 17 Strongholds (14 Level 1, 2 Level 2, 1 Level 3)
- Properly connected network based on strategic positioning

#### Test RL Environment
```bash
python main.py test-rl
```

#### RL Training Demo
```bash
python main.py rl-demo
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_battle_rules.py

# Run with unittest
python -m unittest tests.test_game_state
```

## Project Structure

```
tower_defense_rl/
├── main.py                     # Entry point with multiple modes
├── config.py                   # Game settings and constants
├── game_simulator/            # Core game logic
│   ├── engine.py              # Main game engine
│   ├── game_state.py          # Game state management
│   ├── rules_engine.py        # Rules orchestration
│   ├── entities/              # Game entities (towers, units, battles)
│   ├── graphics/              # Rendering components
│   ├── game_rules/            # Modular game rules
│   └── utils/                 # Utility classes
├── rl_interface/              # RL environment wrapper
├── assets/                    # Images, fonts, sounds
└── tests/                     # Unit tests
```

## Development Workflow

1. **Visual Development**: Use `python main.py simulator` to visually test game mechanics
2. **RL Testing**: Use `python main.py test-rl` to validate the RL environment
3. **Rule Development**: Add new rules in `game_simulator/game_rules/` and integrate in `rules_engine.py`
4. **Testing**: Write tests in `tests/` and run with pytest

## Key Features

- **Time Dilation**: Variable speed simulation with pause/resume
- **Dual Views**: Map overview and detailed battle screens  
- **Modular Rules**: Easy addition of new game mechanics
- **RL Ready**: Gymnasium-compatible environment for training
- **Visual + Headless**: Supports both interactive and automated modes
- **ML/RL API**: REST API for AI agent integration with 4-player support

## ML/RL API Integration

### Quick Start API
```bash
# Start API server
python api_server.py

# Start game and run example AI agent
python examples/ml_agent_example.py --alliance 1 --start-game
```

### Multi-Agent Training
```bash
# Run 4 AI agents simultaneously (in separate terminals)
python examples/ml_agent_example.py --alliance 1 --agent-name "AI_Red" &
python examples/ml_agent_example.py --alliance 2 --agent-name "AI_Blue" &
python examples/ml_agent_example.py --alliance 3 --agent-name "AI_Green" &
python examples/ml_agent_example.py --alliance 4 --agent-name "AI_Yellow" &
```

**API Documentation**: Visit `http://localhost:5000/api/docs` for complete API reference.

**Detailed Guide**: See [API_README.md](API_README.md) for comprehensive ML/RL integration documentation.