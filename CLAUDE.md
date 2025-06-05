# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a "Summit Showdown" strategic alliance game built with Python, Pygame, and REST API integration. The project combines visual simulation with complex game rules, iterative development, AI agent integration via REST API, and time dilation features.

**Note**: Despite the repository name "tower_defense_rl", this implements a strategic alliance conquest game called "Summit Showdown" where 4 alliances compete to control strongholds on a map.

## Environment Setup

The project uses conda for environment management:

```bash
# Activate the environment
conda activate tower_sim

# Or use the provided script
./start-shell.sh
```

Key dependencies:
- `pygame` (2.6.1) - Main graphics and game loop
- `flask` (3.1.0) - REST API server for AI agent integration
- `numpy` (2.2.6) - Numerical operations
- `pygame-gui` (0.6.14) - UI components
- `flasgger` (0.9.7.1) - Swagger API documentation

**Note**: The RL interface (`gymnasium`) is currently broken and needs to be rewritten to work with stronghold/alliance mechanics instead of non-existent tower system.

## Development Commands

The project has multiple entry points:

```bash
# Run visual simulator
python main.py

# Run REST API server for AI agents
python api_server.py

# Run example ML agent
python examples/ml_agent_example.py

# Run tests
python -m pytest tests/
```

## Architecture

The project follows a separation of concerns design pattern:

### Core Components
- **Game Simulator** (`game_simulator/`) - Core game logic with entities (alliances, strongholds, heroes, battles) and rules engine
- **REST API** (`api_server.py`) - Flask-based API for AI agent integration with 15+ endpoints
- **Graphics** (`game_simulator/graphics/`) - Pygame rendering for map view and battle details with time controls
- **Game Rules** (`game_simulator/game_rules/`) - Modular rule system for battle mechanics and game progression
- **Examples** (`examples/`) - Working ML agent example that uses the REST API
- **RL Interface** (`rl_interface/`) - **BROKEN** - Needs complete rewrite for stronghold/alliance mechanics

### Key Design Principles
- **Time Dilation**: Game supports variable time scales (arrow keys), pause/play (spacebar), and speed controls
- **Multi-View Interface**: Map overview, battle list, and individual battle detail screens
- **Modular Rules**: Rules engine allows iterative addition of game mechanics
- **API Integration**: REST API enables AI agents to control alliances and monitor battles
- **Real-time Simulation**: Supports both visual simulation and headless API-driven gameplay
- **Session Management**: Multiple AI agent sessions can run simultaneously via API

### Iterative Development Workflow
1. ✅ Basic visual simulator with time controls
2. ✅ Core game mechanics (stronghold capture, alliance competition)
3. ✅ Battle system with turn-based hero combat
4. ✅ REST API interface for AI agent integration
5. ✅ Example ML agent demonstrating API usage
6. 🔄 **Current**: Refine game balance and add advanced features
7. ❌ **Broken**: RL environment interface needs complete rewrite

### Development Acceleration Instructions

For maximum efficiency when working with this codebase:

1. **Parallel Tool Execution**: When performing multiple independent operations, invoke all relevant tools simultaneously rather than sequentially. Use batch tool calls for reading multiple files, running multiple commands, or performing parallel searches.

2. **Reflection-Based Iteration**: After receiving tool results, carefully analyze their quality and completeness. Use thinking time to plan optimal next steps based on new information before proceeding with actions.

3. **Proactive Web Search**: Use the web search tool when:
   - User asks about API references for third-party tools (pygame, flask, etc.)
   - Questions require factual information after January 2025
   - Any query needs real-time or current data
   - Be proactive in identifying when searches would enhance response quality

The project is designed for complex rule development where game mechanics can be added incrementally while maintaining a stable core simulation engine.