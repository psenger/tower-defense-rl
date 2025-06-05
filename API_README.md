# Summit Showdown ML/RL API

This document describes the REST API for integrating Machine Learning and Reinforcement Learning agents with the Summit Showdown tower defense game.

## Overview

The API enables four AI agents to play Summit Showdown simultaneously by providing:

- **Game State Access**: Complete visibility into game state, alliances, strongholds, and battles
- **Action Submission**: Endpoints for launching attacks and managing hero sets
- **Real-time Monitoring**: Live battle tracking and event streaming
- **Session Management**: Multi-agent coordination and tracking

## Quick Start

### 1. Start the API Server

```bash
# Install dependencies
pip install flask flask-cors flask-swagger-ui

# Start the API server
python api_server.py
```

The server will start on `http://localhost:5000` with comprehensive API documentation at `http://localhost:5000/api/docs`.

### 2. Start a Game

```bash
curl -X POST http://localhost:5000/api/game/start
```

### 3. Create Agent Sessions

Each AI agent needs a session for one of the four alliances:

```bash
# Agent for Alliance 1
curl -X POST http://localhost:5000/api/session \
  -H "Content-Type: application/json" \
  -d '{"alliance_id": 1, "agent_name": "AI_Red"}'

# Response: {"session_id": "uuid", "alliance_id": 1, ...}
```

### 4. Monitor Game State

```bash
# Get overall game status
curl http://localhost:5000/api/game/status

# Get alliance-specific state
curl http://localhost:5000/api/alliances/1/state

# Get available hero sets for attacks
curl http://localhost:5000/api/alliances/1/hero-sets
```

### 5. Launch Attacks

```bash
curl -X POST http://localhost:5000/api/alliances/1/attack \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: your-session-id" \
  -d '{
    "hero_set_id": "P1_1_Set1",
    "target_stronghold_id": "S1"
  }'
```

## Example AI Agent

Run the provided example agent:

```bash
# Start agent for Alliance 1
python examples/ml_agent_example.py --alliance 1 --agent-name "MyAI" --start-game

# Multiple agents (run in separate terminals)
python examples/ml_agent_example.py --alliance 1 --agent-name "AI_Red" &
python examples/ml_agent_example.py --alliance 2 --agent-name "AI_Blue" &
python examples/ml_agent_example.py --alliance 3 --agent-name "AI_Green" &
python examples/ml_agent_example.py --alliance 4 --agent-name "AI_Yellow" &
```

## Game Mechanics for AI

### Alliance System
- 4 Alliances (Red, Blue, Green, Yellow)
- Each alliance has 50 players with 2 hero sets each (100 hero sets total)
- Each hero set contains 5 heroes with attack, defense, and HP stats

### Strongholds & Map
- 21 Strongholds total:
  - 4 Alliance Homes (corners)
  - 14 Level 1 Strongholds (1 point each)
  - 2 Level 2 Strongholds (2 points each)  
  - 1 Level 3 Stronghold (3 points each)
- Strongholds are connected in a network - you can only attack adjacent strongholds
- Controlling strongholds generates points for victory

### Battle System
- 5v5 Hero Set battles following specific damage rules
- Damage per hit = Attacker.Attack - Average_Defense_of_Opposing_Set
- Battles have 50 step limit with random turn order
- NPCs scale by stronghold level (80%/100%/120% of player stats)

### Constraints & Strategy
- **Stamina System**: Players have 4 stamina per half, consumed on attacks
- **Protection Periods**: 20-minute protection after stronghold capture
- **Adjacency Rule**: Can only attack strongholds adjacent to controlled territory
- **Resource Management**: Limited hero sets, stamina, and attack windows

## API Endpoints

### Game Management
- `GET /api/health` - Health check
- `POST /api/game/start` - Start new game
- `POST /api/game/stop` - Stop current game
- `GET /api/game/status` - Get game status
- `POST /api/game/speed` - Adjust simulation speed

### Session Management
- `POST /api/session` - Create agent session
- `DELETE /api/session/{id}` - End session

### Alliance Operations
- `GET /api/alliances/{id}/state` - Get alliance state
- `GET /api/alliances/{id}/hero-sets` - Get available hero sets
- `POST /api/alliances/{id}/attack` - Launch attack

### Battle System
- `GET /api/battles` - List active battles
- `GET /api/battles/{id}` - Get battle details

### Map & Strongholds
- `GET /api/strongholds` - List all strongholds
- `GET /api/map/layout` - Get map layout

## Complete API Documentation

Visit `http://localhost:5000/api/docs` when the server is running for interactive API documentation with request/response schemas and examples.

## ML/RL Integration Patterns

### Reinforcement Learning
```python
import requests

class SummitShowdownEnv:
    def __init__(self, api_url, alliance_id):
        self.api_url = api_url
        self.alliance_id = alliance_id
        self.session_id = None
    
    def reset(self):
        # Create session and get initial state
        response = requests.post(f"{self.api_url}/api/session", 
                               json={"alliance_id": self.alliance_id})
        self.session_id = response.json()["session_id"]
        return self.get_observation()
    
    def step(self, action):
        # Execute action and return (obs, reward, done, info)
        self.execute_action(action)
        obs = self.get_observation()
        reward = self.calculate_reward()
        done = self.is_game_over()
        return obs, reward, done, {}
    
    def get_observation(self):
        # Convert API response to ML-friendly format
        state = requests.get(f"{self.api_url}/api/alliances/{self.alliance_id}/state")
        return self.state_to_vector(state.json())
```

### Multi-Agent Learning
```python
# Each agent manages one alliance
agents = [
    SummitShowdownAgent(alliance_id=1, model=model1),
    SummitShowdownAgent(alliance_id=2, model=model2),
    SummitShowdownAgent(alliance_id=3, model=model3),
    SummitShowdownAgent(alliance_id=4, model=model4),
]

# Simultaneous training
for episode in range(num_episodes):
    for agent in agents:
        obs = agent.reset()
    
    while not game_over:
        actions = [agent.select_action(obs) for agent in agents]
        for agent, action in zip(agents, actions):
            agent.step(action)
```

## Performance & Scaling

- **Concurrent Requests**: API supports multiple simultaneous agent connections
- **Rate Limiting**: Built-in action cooldowns prevent spam
- **Game Speed Control**: Adjust simulation speed for faster training
- **Battle Monitoring**: Real-time battle updates for immediate feedback

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure API server is running on port 5000
2. **Alliance Not Found**: Use alliance IDs 1-4 only
3. **No Available Hero Sets**: Check stamina and hero set status
4. **Invalid Target**: Ensure target is adjacent and attackable
5. **Session Expired**: Create new session if old one becomes invalid

### Debug Mode

Run the API server with debug logging:
```bash
FLASK_DEBUG=1 python api_server.py
```

### Health Monitoring

```bash
# Check API health
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "game_active": true,
  "game_running": true
}
```

## Contributing

The API is designed to be extensible. To add new endpoints:

1. Add route handlers to `api_server.py`
2. Update OpenAPI spec in `swagger_spec.py`
3. Add tests for new functionality
4. Update documentation

For ML/RL researchers, consider contributing:
- Additional reward functions
- Alternative observation spaces
- Multi-objective optimization examples
- Advanced strategy implementations