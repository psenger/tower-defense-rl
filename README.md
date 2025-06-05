# Summit Showdown - Strategic Alliance Game

This is a **"Summit Showdown"** strategic alliance game built with Python, Pygame, and REST API integration. 

**Note**: Despite the repository name "tower_defense_rl", this implements a strategic alliance conquest game where 4 alliances compete to control strongholds on a map.

The project combines visual simulation with complex game rules, iterative development, AI agent integration via REST API, and time dilation features.

- [Features](#features)
- [How to Run](#how-to-run)
  * [Environment Setup](#environment-setup)
  * [Main Applications](#main-applications)
    + [1. Visual Simulator (Primary Entry Point)](#1-visual-simulator-primary-entry-point)
    + [2. REST API Server](#2-rest-api-server)
    + [3. RL Environment Testing](#3-rl-environment-testing)
  * [AI Agent Examples](#ai-agent-examples)
    + [ML Agent Example](#ml-agent-example)
  * [Testing](#testing)
    + [Core Testing](#core-testing)
    + [Unit Tests](#unit-tests)
  * [Typical Workflows](#typical-workflows)
    + [Development Workflow](#development-workflow)
    + [AI Training Workflow](#ai-training-workflow)
    + [Multi-Agent Testing](#multi-agent-testing)
- [I. Core Concepts](#i-core-concepts)
- [II. Player & Hero Attributes](#ii-player--hero-attributes)
- [III. Battle Mechanics (Engaging Hero Set vs. Opposing Hero Set)](#iii-battle-mechanics-engaging-hero-set-vs-opposing-hero-set)
- [IV. Game Play & Stronghold Interaction](#iv-game-play--stronghold-interaction)
- [V. Scoring Rules ("Summit Showdown Points")](#v-scoring-rules-summit-showdown-points)
- [VI. Map Structure](#vi-map-structure)

## Features

- **Visual Simulator**: See the game in action with time controls (pause/play, speed adjustment, attack initiation)
- **REST API Integration**: Comprehensive Flask-based API with 15+ endpoints for AI agent control
- **Multi-View Interface**: Map overview, battle list, and detailed battle screens
- **Real-time Battles**: Turn-based hero combat system with strategic depth
- **AI Agent Example**: Working ML agent demonstrating API usage and strategic decision-making

## How to Run

### Environment Setup
```bash
# Activate conda environment
conda activate tower_sim

# Or use the provided script
./start-shell.sh

# Install dependencies (if needed)
conda env create -f environment.yml
# OR
pip install -r requirements.txt
```

### Main Applications

#### 1. Visual Simulator (Primary Entry Point)
```bash
# Run interactive visual simulator with pygame graphics
python main.py

# Explicit modes
python main.py simulator
python main.py sim
```
**Controls**: Arrow keys (speed), Spacebar (pause/resume), 1-4 keys (test attacks), Mouse (navigate views)

#### 2. REST API Server
```bash
# Start API server for AI agents (port 5000)
python api_server.py

# Start API documentation server (port 5001)  
python swagger_spec.py
```
**Access**: Game API at `http://localhost:5000`, Swagger UI at `http://localhost:5001/api/docs`

#### 3. RL Environment Testing
```bash
# Test RL environment interface
python main.py test-rl
python main.py test

# Run RL training demo
python main.py demo
python main.py rl-demo
```

### AI Agent Examples

#### ML Agent Example
```bash
# Basic agent for alliance 1
python examples/ml_agent_example.py --alliance 1

# Named agent with custom duration
python examples/ml_agent_example.py --alliance 2 --agent-name "MyAI" --duration 600

# Start new game and run agent
python examples/ml_agent_example.py --alliance 3 --start-game --api-url http://localhost:5000
```

### Testing

#### Core Testing
```bash
# Test core game logic (no server required)
python test_api_core.py

# Test visual simulator
python test_visual.py
```

#### Unit Tests
```bash
# Run specific test files (requires pytest)
python -m pytest tests/test_alliance.py
python -m pytest tests/test_battle_rules.py
python -m pytest tests/test_game_state.py
python -m pytest tests/test_hero.py
python -m pytest tests/test_hero_set.py
python -m pytest tests/test_stronghold.py
python -m pytest tests/test_summit_battle.py
python -m pytest tests/test_tower_rules.py

# Run all tests
python -m pytest tests/
```

### Typical Workflows

#### Development Workflow
```bash
# 1. Start with visual simulator
python main.py

# 2. Test core functionality  
python test_api_core.py

# 3. Start API for agent development
python api_server.py
```

#### AI Training Workflow
```bash
# 1. Start API server
python api_server.py

# 2. Run example agent
python examples/ml_agent_example.py --alliance 1 --start-game

# 3. Monitor via Swagger UI
# Open http://localhost:5001/api/docs
```

#### Multi-Agent Testing
```bash
# Terminal 1: Start API server
python api_server.py

# Terminal 2-5: Run agents for each alliance
python examples/ml_agent_example.py --alliance 1 --agent-name "Agent1" &
python examples/ml_agent_example.py --alliance 2 --agent-name "Agent2" &
python examples/ml_agent_example.py --alliance 3 --agent-name "Agent3" &
python examples/ml_agent_example.py --alliance 4 --agent-name "Agent4" &
```

## I. Core Concepts

1.  **Objective:** Four Alliances compete to accumulate the most "Summit Showdown Points" by capturing and holding Strongholds.
2.  **Alliances:** Each Alliance consists of 50 individual Players.
3.  **Game Structure:** The game is divided into a First Half (11 hours 30 minutes) and a Second Half (11 hours 30 minutes), separated by a 30-minute Half-time break. Each half is a distinct phase for hero deployment for attacking purposes.

## II. Player & Hero Attributes

1.  **Player Hero Pool & Selection:**
    *   At the start of a game, each of the 50 Players in an Alliance is provided with 50 randomly generated Heroes.
    *   From these 50 Heroes, each Player selects 30 Heroes (organized as six Sets of five Heroes each) to use for the entire game (both halves). These are the Player's "Selected Hero Sets."
    *   The 20 unselected Heroes for each Player are not used further in the game.
2.  **Hero Skills (Simulated Generation for Player Heroes):**
    *   The stats for a Player's initially provided 50 Heroes are generated once at the start of the game and persist.
    *   Stats are generated randomly based on the following distributions:
        *   Attack: Average 4627, Standard Deviation 432
        *   Defense: Average 4195, Standard Deviation 346
        *   Hit Points (HP): Average 8088, Standard Deviation 783
3.  **Hero Set "Consumed for Attacking" Status:**
    *   Each of a Player's six Selected Hero Sets has a status per game half: "Available for Attack" or "Consumed for Attack."
    *   When a Player initiates an attack action using one of their Selected Hero Sets, that specific set becomes "Consumed for Attack" for the current game half once it engages in battle, regardless of the battle's outcome.
    *   A Player cannot use a Hero Set that is "Consumed for Attack" to initiate further attacks in the current game half.
    *   **All Hero Sets revert to "Available for Attack" at the start of the Second Half and all Heroes are restored to full health. Dead heroes are brought back to life.**

## III. Battle Mechanics (Engaging Hero Set vs. Opposing Hero Set)

*This section describes a battle between one 5-Hero Set and an opposing 5-Hero Set (e.g., Player's attacking set vs. NPC set, or Player's attacking set vs. Player's garrisoned set, or Player's garrisoned set vs. enemy Player's attacking set).*

1.  **Battle Initiation:**
    *   A battle consists of up to 50 "steps." A step involves one turn of actions for one side, followed by one turn of actions for the other side.
    *   The side that initiated the engagement is the initial attacker for the first turn of the first step.
2.  **Turn Structure (for the currently acting side):**
    *   A random living Hero from the currently acting set is chosen to perform actions.
    *   **Number of Hits:** This chosen Hero performs a random number of hits, ranging from 1 to 4. Each number of hits (1, 2, 3, or 4) is equally probable.
    *   For each hit performed by the acting Hero:
        *   Damage Calculation: `Damage_per_hit = ActingHero.Attack - AverageDefenseOfOpposingSet`
            *   `AverageDefenseOfOpposingSet` is the average Defense value of all *currently living* Heroes in the opposing set.
            *   If `AverageDefenseOfOpposingSet >= ActingHero.Attack`, then `Damage_per_hit` is 0 (the attack is ineffective for this hit).
        *   Damage Application (Area of Effect - AoE):
            *   If `Damage_per_hit > 0`, this damage amount is then distributed among all *currently living* Heroes in the opposing set. The distribution uses "truly random weighting": each living opposing hero is assigned a random weight (such that weights sum to 1), and receives that proportion of the `Damage_per_hit`.
            *   This damage portion is subtracted from their individual Hit Points.
    *   After one side completes its turn, the other side takes its turn. This completes one battle "step."
3.  **Hero Defeat:**
    *   When a Hero's Hit Points reach 0, they are removed from the current battle.
4.  **Battle Victory Conditions (for the specific 5v5 Set engagement):**
    *   The side with at least one Hero remaining when all opposing Heroes have 0 HP is the winner of this battle.
    *   If the 50-step limit is reached and Heroes remain on both sides: The side that has dealt the most accumulated damage during this battle wins.
    *   If the 50-step limit is reached, Heroes remain on both sides, AND accumulated damage is equal: The side that was the initial attacker for this battle loses (i.e., the defender wins this specific tie).
5.  **Immediate Defender Removal:**
    *   **CRITICAL STRATEGIC RULE**: When a Hero Set (NPC or Player garrison) is completely defeated in battle, it is **immediately removed** from the Stronghold **permanently**.
    *   This means other Alliances can observe the Stronghold and see it has fewer defenders after each battle, creating strategic opportunities.
    *   **Strategic Implication**: An Alliance could wait until multiple battles have weakened a Stronghold's defenses, then attack when only one or few defenders remain to easily capture it.

## IV. Game Play & Stronghold Interaction

1.  **Map & Initial Setup:**
    *   The game is played on a map of interconnected Strongholds.
    *   Each of the four Alliances starts at their "Alliance Home" located in one of the four corners of the map. These are their starting points and function as their initial controlled nodes.
    *   All other Strongholds are initially neutral and garrisoned by NPC Defense Teams.
2.  **Player Attacks:**
    *   Players can attack Strongholds adjacent to their Alliance's currently controlled Strongholds (including their Alliance Home).
    *   To attack, a Player selects one of their Hero Sets that is "Available for Attack." This set then engages one of the Stronghold's active Defense Teams (NPC or Player garrison) in a battle (as per Section III). Upon engagement, the attacking set becomes "Consumed for Attack" for the current half.
3.  **Attacking Strongholds:**
    *   Players can attack Strongholds adjacent to their Alliance's currently controlled Strongholds (including their Alliance Home).
    *   To attack, a Player selects one of their Hero Sets that is "Available for Attack." This set then engages one of the Stronghold's active Defense Teams (NPC or Player garrison) in a battle (as per Section III). Upon engagement, the attacking set becomes "Consumed for Attack" for the current half.
4.  **Stronghold Defense Teams (NPCs):**
    *   Each NPC Defense Team consists of 5 NPC Heroes.
    *   NPC Hero stats are generated using the same distributions as Player Heroes:
        *   Attack: Average 4627, Standard Deviation 432
        *   Defense: Average 4195, Standard Deviation 346
        *   Hit Points (HP): Average 8088, Standard Deviation 783
    *   Initial Number of NPC Teams:
        *   Level 3 Stronghold: 15 NPC Defense Teams
        *   Level 2 Stronghold: 12 NPC Defense Teams
        *   Level 1 Stronghold: 9 NPC Defense Teams
    *   **NPC Teams Do NOT Respawn:** Once defeated, NPC Defense Teams are permanently removed from the game. They do not respawn at any point, including the Second Half.
5.  **Capturing a Stronghold:**
    *   To make a Stronghold capturable, all its current NPC Defense Teams must be defeated.
    *   Once all NPC teams are cleared from a Stronghold, the Alliance that defeated the most NPC Defense Teams from that Stronghold (since those NPCs were last fully present) captures it.
    *   Ties for most NPC teams defeated are broken by which Alliance reached that count first.
6.  **Garrisoning Captured Strongholds (Player Teams):**
    *   When an Alliance captures a Stronghold, a single designated Lead Human Player for that Alliance manually assigns specific Player Hero Sets from any player within their Alliance to garrison the Stronghold.
    *   A Hero Set's "Consumed for Attack" status does *not* prevent it from being assigned to garrison duty by the Leader.
    *   Assigning a Hero Set to garrison duty does *not* change the set's "Consumed for Attack" status.
    *   **Garrisoned Set Availability and Interaction with Attacking:**
        *   A Player Hero Set assigned to garrison a Stronghold is considered "on duty" at that Stronghold and will participate in defensive battles if that Stronghold is attacked.
        *   A Player Hero Set cannot simultaneously be engaged in a defensive battle at its garrisoned Stronghold AND be used by its owner to initiate an offensive attack on another Stronghold.
        *   If a Player wishes to use one of their Hero Sets that is currently garrisoning a Stronghold to *initiate an attack* on another Stronghold:
            *   The Player can only select that Hero Set for an attack if it is currently "Available for Attack" (i.e., not yet consumed by a previous attack this half).
            *   If the Player selects such a garrisoned (and "Available for Attack") Hero Set to initiate an attack, that Hero Set is immediately removed from its garrison post at the Stronghold. It then engages in the attack on the new target. Upon engagement, this Hero Set becomes "Consumed for Attack" for the current half.
            *   The Alliance Leader would then need to assign a new Hero Set to fill the vacated garrison slot if desired.
    *   Maximum Garrison Size:
        *   Level 3 Strongholds: Up to 5 Allied Player Hero Sets
        *   Level 2 Strongholds: Up to 7 Allied Player Hero Sets
        *   Level 1 Strongholds: Up to 9 Allied Player Hero Sets
7.  **Stronghold Protection Period:**
    *   Upon being captured by an Alliance, a Stronghold enters a **1-hour (60-minute) cooling period** during which it cannot be attacked by other Alliances.
    *   During this protection, the capturing Alliance's leader and co-leader can manually adjust/swap the Player Hero Sets garrisoning the Stronghold. This adjustment does not cost stamina nor alter the "Consumed for Attack" status of the involved Hero Sets. Swapped-out sets are no longer garrisoning and are fully available to their owner (respecting their current "Consumed for Attack" status); swapped-in sets take up garrison duty.
    *   Decisive Phase: During the final 60 minutes of the First Half, the Protection Period for all Strongholds is reduced to 5 minutes.
8.  **Half-time and Second Half:**
    *   The First Half lasts 11 hours and 30 minutes.
    *   This is followed by a 30-minute Half-time period, during which **no attacks can be launched by any Alliance**.
    *   The Second Half begins after Half-time, inheriting the map status (Stronghold ownership and player garrisons) from the end of the First Half.
    *   **At the start of the Second Half:**
        *   **All Strongholds immediately lose any active protection.**
        *   **All Player Hero Sets revert to "Available for Attack" and all Heroes are restored to full health. Dead heroes are brought back to life.**
        *   **Strongholds remain garrisoned as they were - occupied strongholds continue to be occupied by the same alliances.**
        *   **No NPC respawning occurs - defeated NPCs remain permanently removed.**
    *   Other rules remain the same as the First Half.

## V. Scoring Rules ("Summit Showdown Points")

*The winning Alliance is determined by the total Summit Showdown Points accumulated throughout the game.*

|                     | Team Points | Occupation Points |
|:--------------------|:------------|:------------------|
| Level 3 Stronghold  | 80          | 720               |
| Level 2 Stronghold  | 60          | 420               |
| Level 1 Strong Hold | 40          | 200               |

1.  **Team Points (Defeating Stronghold Defense Teams):**
    *   Awarded to an Alliance each time one of its Players defeats any Defense Team (NPC or opposing Player's garrisoned set) within a Stronghold.
        *   Level 3 Stronghold Team Defeated: 80 Points
        *   Level 2 Stronghold Team Defeated: 60 Points
        *   Level 1 Stronghold Team Defeated: 40 Points
2.  **Occupation Points (Capturing a Stronghold):**
    *   Points awarded to an Alliance when it successfully captures a Stronghold (as per IV.5).
    *   **If an Alliance loses control of a Stronghold to another Alliance, they lose these points.**
    *   **Occupation Points are calculated at the end of the game based on which Strongholds each Alliance actually controls when time expires.**
        *   Level 3 Stronghold Controlled at Game End: 720 Points
        *   Level 2 Stronghold Controlled at Game End: 420 Points
        *   Level 1 Stronghold Controlled at Game End: 200 Points
3. **Game End Conditions:**
    * The game ends after the Second Half time limit expires (23 hours total game time).
    * If all neutral Strongholds are captured and no further expansion is possible, the game may end early.
    * The winning Alliance is determined by the total Summit Showdown Points accumulated throughout the game.

## VI. Map Structure

### Naming Convention

#### Node Types
- **Teams (Alliance Homes)**: `T#` where `#` is the team number (1-4)
  - Example: `T1` = Team 1's Alliance Home
- **Strongholds**: `S#-X` where `S` indicates Stronghold, `#` is the strong hold level ( 1-3 ), and `X` is a sequential identifier (1-19)
  - Example: `S1-5` = Stronghold level 1 with unique ID 5

#### Stronghold Levels
- **Level 1 Stronghold**: Basic defensive position
- **Level 2 Stronghold**: Enhanced defensive position with greater strategic value
- **Level 3 Stronghold**: Premium defensive position, typically central hub locations

### How to Read the Table

- **Node Name**: Unique identifier following the naming convention above
- **Type**: Full description of the node (Alliance Home or Stronghold with level)
- **Connected To**: Comma-separated list of all nodes directly connected by edges/paths

### Strategic Notes
- Teams are positioned at the corners of the network
- The Level 3 Stronghold (S3-10) serves as the central hub
- Level 2 Strongholds (S2-11, S2-9) provide key intermediate positions
- Connections represent possible movement paths or strategic relationships between positions

### Network Node Table

| Node Name | Type                 | Connected To            |
|-----------|----------------------|-------------------------|
| T1        | Team 1 Alliance Home | S1-2                    |
| T2        | Team 2 Alliance Home | S1-5                    |
| T3        | Team 3 Alliance Home | S1-15                   |
| T4        | Team 4 Alliance Home | S1-18                   |
| S1-1      | Level 1 Stronghold   | S1-3, S1-4              |
| S1-2      | Level 1 Stronghold   | T1, S1-3, S1-6, S2-11   |
| S1-3      | Level 1 Stronghold   | S1-1, S1-2, S1-4        |
| S1-4      | Level 1 Stronghold   | S1-1, S1-3, S1-5        |
| S1-5      | Level 1 Stronghold   | T2, S1-4, S1-7, S2-9    |
| S1-6      | Level 1 Stronghold   | S1-2, S1-12, S1-13      |
| S1-7      | Level 1 Stronghold   | S1-5, S1-8, S1-14       |
| S1-8      | Level 1 Stronghold   | S1-7, S1-14             |
| S1-12     | Level 1 Stronghold   | S1-6, S1-13             |
| S1-13     | Level 1 Stronghold   | S1-6, S1-12, S1-18      |
| S1-14     | Level 1 Stronghold   | S1-7, S1-8, S1-15       |
| S1-15     | Level 1 Stronghold   | T3, S1-14, S1-16, S2-9  |
| S1-16     | Level 1 Stronghold   | S1-17, S1-19, S1-15     |
| S1-17     | Level 1 Stronghold   | S1-16, S1-19, S1-18     |
| S1-18     | Level 1 Stronghold   | T4, S1-13, S1-17, S2-11 |
| S1-19     | Level 1 Stronghold   | S1-16, S1-17            |
| S2-9      | Level 2 Stronghold   | S1-5, S1-15, S3-10      |
| S2-11     | Level 2 Stronghold   | S1-2, S1-18, S3-10      |
| S3-10     | Level 3 Stronghold   | S2-9, S2-11             |

### Layout

Using a grid-style-layout the Towers and Strongholds on the Map should look like this.

|   |       |       |   |       |       |       |   |       |      |
|---|-------|-------|---|-------|-------|-------|---|-------|------|
|   | T1    |       |   |       | S1-1  |       |   |       | T2   |
|   |       | S1-2  |   | S1-3  |       | S1-4  |   | S1-5  |      |
|   |       | S1-6  |   |       |       |       |   | S1-7  |      |
|   | S1-12 |       |   | S2-11 | S3-10 | S2-9  |   |       | S1-8 |
|   |       | S1-13 |   |       |       |       |   | S1-14 |      |
|   |       | S1-18 |   | S1-17 |       | S1-16 |   | S1-15 |      |
|   | T4    |       |   |       | S1-#  |       |   |       | T3   |


Visual representation of the map as a SVG can be found at ![](./assets/images/map.svg)