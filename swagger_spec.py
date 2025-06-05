# swagger_spec.py
"""
OpenAPI/Swagger specification for Summit Showdown ML/RL API

This generates comprehensive API documentation for the ML/RL integration endpoints.
"""

from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import json

def create_swagger_spec():
    """Create the OpenAPI 3.0 specification"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Summit Showdown ML/RL API",
            "version": "1.0.0",
            "description": "REST API for integrating AI agents with Summit Showdown tower defense game. Enables Machine Learning and Reinforcement Learning applications through comprehensive game state access and action submission endpoints.",
            "contact": {
                "name": "Summit Showdown API Support",
                "email": "support@summitshowdown.ai"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Development server"
            }
        ],
        "tags": [
            {
                "name": "Game Management",
                "description": "Operations for managing game sessions"
            },
            {
                "name": "Alliance Operations",
                "description": "Alliance-specific state and actions"
            },
            {
                "name": "Battle System",
                "description": "Battle monitoring and information"
            },
            {
                "name": "Map & Strongholds",
                "description": "Map layout and stronghold information"
            },
            {
                "name": "Session Management",
                "description": "API session management for AI agents"
            }
        ],
        "paths": {
            "/api/health": {
                "get": {
                    "tags": ["Game Management"],
                    "summary": "Health check",
                    "description": "Check API server health and game status",
                    "responses": {
                        "200": {
                            "description": "Server is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "game_active": {"type": "boolean"},
                                            "game_running": {"type": "boolean"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/session": {
                "post": {
                    "tags": ["Session Management"],
                    "summary": "Create AI agent session",
                    "description": "Create a new API session for an AI agent to interact with the game",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["alliance_id"],
                                    "properties": {
                                        "alliance_id": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 4,
                                            "description": "Alliance ID (1-4) for the AI agent"
                                        },
                                        "agent_name": {
                                            "type": "string",
                                            "description": "Optional name for the AI agent"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Session created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "session_id": {"type": "string", "format": "uuid"},
                                            "alliance_id": {"type": "integer"},
                                            "agent_name": {"type": "string"},
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid alliance_id",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/session/{session_id}": {
                "delete": {
                    "tags": ["Session Management"],
                    "summary": "End AI agent session",
                    "description": "End an existing API session",
                    "parameters": [
                        {
                            "name": "session_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string", "format": "uuid"},
                            "description": "Session ID to end"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Session ended successfully"
                        },
                        "404": {
                            "description": "Session not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/game/start": {
                "post": {
                    "tags": ["Game Management"],
                    "summary": "Start new game",
                    "description": "Initialize and start a new Summit Showdown game instance",
                    "responses": {
                        "200": {
                            "description": "Game started successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"},
                                            "game_time": {"type": "number"},
                                            "half": {"type": "integer"},
                                            "alliances": {
                                                "type": "object",
                                                "additionalProperties": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Game already running",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/game/stop": {
                "post": {
                    "tags": ["Game Management"],
                    "summary": "Stop current game",
                    "description": "Stop the currently running game",
                    "responses": {
                        "200": {
                            "description": "Game stopped successfully"
                        }
                    }
                }
            },
            "/api/game/status": {
                "get": {
                    "tags": ["Game Management"],
                    "summary": "Get game status",
                    "description": "Get comprehensive status of the current game",
                    "responses": {
                        "200": {
                            "description": "Current game status",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/GameStatus"}
                                }
                            }
                        },
                        "404": {
                            "description": "No active game",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/game/speed": {
                "post": {
                    "tags": ["Game Management"],
                    "summary": "Set game speed",
                    "description": "Adjust the simulation speed (time dilation)",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["speed"],
                                    "properties": {
                                        "speed": {
                                            "type": "number",
                                            "minimum": 0,
                                            "description": "Speed multiplier (0=paused, 1=normal, 2=2x speed, etc.)"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Speed updated successfully"
                        },
                        "400": {
                            "description": "Invalid speed value",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/alliances/{alliance_id}/state": {
                "get": {
                    "tags": ["Alliance Operations"],
                    "summary": "Get alliance state",
                    "description": "Get detailed state information for a specific alliance",
                    "parameters": [
                        {
                            "name": "alliance_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer", "minimum": 1, "maximum": 4},
                            "description": "Alliance ID (1-4)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Alliance state information",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AllianceState"}
                                }
                            }
                        },
                        "404": {
                            "description": "Alliance not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/alliances/{alliance_id}/hero-sets": {
                "get": {
                    "tags": ["Alliance Operations"],
                    "summary": "Get alliance hero sets",
                    "description": "Get available hero sets for an alliance that can be used for attacks",
                    "parameters": [
                        {
                            "name": "alliance_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer", "minimum": 1, "maximum": 4},
                            "description": "Alliance ID (1-4)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Available hero sets",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HeroSets"}
                                }
                            }
                        },
                        "404": {
                            "description": "Alliance not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/alliances/{alliance_id}/attack": {
                "post": {
                    "tags": ["Alliance Operations"],
                    "summary": "Launch attack",
                    "description": "Launch an attack against a target stronghold using a specific hero set",
                    "parameters": [
                        {
                            "name": "alliance_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer", "minimum": 1, "maximum": 4},
                            "description": "Alliance ID (1-4)"
                        },
                        {
                            "name": "X-Session-ID",
                            "in": "header",
                            "required": False,
                            "schema": {"type": "string", "format": "uuid"},
                            "description": "API session ID for tracking"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["hero_set_id", "target_stronghold_id"],
                                    "properties": {
                                        "hero_set_id": {
                                            "type": "string",
                                            "description": "ID of the hero set to use for attack"
                                        },
                                        "target_stronghold_id": {
                                            "type": "string",
                                            "description": "ID of the stronghold to attack"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Attack launched successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "battle_id": {"type": "string"},
                                            "attacking_set": {"type": "string"},
                                            "target_stronghold": {"type": "string"},
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "404": {
                            "description": "Alliance, hero set, or target not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/battles": {
                "get": {
                    "tags": ["Battle System"],
                    "summary": "Get active battles",
                    "description": "Get list of all currently active battles",
                    "responses": {
                        "200": {
                            "description": "List of active battles",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/BattleList"}
                                }
                            }
                        },
                        "404": {
                            "description": "No active game",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/battles/{battle_id}": {
                "get": {
                    "tags": ["Battle System"],
                    "summary": "Get battle details",
                    "description": "Get detailed information about a specific battle",
                    "parameters": [
                        {
                            "name": "battle_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Battle ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Battle details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/BattleDetails"}
                                }
                            }
                        },
                        "404": {
                            "description": "Battle not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/strongholds": {
                "get": {
                    "tags": ["Map & Strongholds"],
                    "summary": "Get all strongholds",
                    "description": "Get information about all strongholds on the map",
                    "responses": {
                        "200": {
                            "description": "Stronghold information",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/StrongholdList"}
                                }
                            }
                        },
                        "404": {
                            "description": "No active game",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/map/layout": {
                "get": {
                    "tags": ["Map & Strongholds"],
                    "summary": "Get map layout",
                    "description": "Get the complete map layout including stronghold positions and connections",
                    "responses": {
                        "200": {
                            "description": "Map layout information",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MapLayout"}
                                }
                            }
                        },
                        "404": {
                            "description": "No active game",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "description": "Error message"}
                    }
                },
                "GameStatus": {
                    "type": "object",
                    "properties": {
                        "half": {"type": "integer", "description": "Current game half (1 or 2)"},
                        "game_time": {"type": "number", "description": "Elapsed game time in seconds"},
                        "active_battles": {"type": "integer", "description": "Number of active battles"},
                        "alliance_scores": {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                            "description": "Scores for each alliance"
                        },
                        "stronghold_control": {
                            "type": "object",
                            "description": "Stronghold control by alliance"
                        },
                        "api_sessions": {"type": "integer", "description": "Number of active API sessions"},
                        "game_speed": {"type": "number", "description": "Current simulation speed"}
                    }
                },
                "AllianceState": {
                    "type": "object",
                    "properties": {
                        "alliance_id": {"type": "integer"},
                        "name": {"type": "string"},
                        "color": {"type": "array", "items": {"type": "integer"}},
                        "controlled_strongholds": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ControlledStronghold"}
                        },
                        "available_hero_sets": {"type": "integer"},
                        "total_players": {"type": "integer"},
                        "attackable_targets": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/AttackableTarget"}
                        },
                        "score": {"type": "integer"}
                    }
                },
                "ControlledStronghold": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "level": {"type": "integer"},
                        "position": {"$ref": "#/components/schemas/Position"},
                        "is_protected": {"type": "boolean"},
                        "garrison_count": {"type": "integer"},
                        "max_garrison": {"type": "integer"}
                    }
                },
                "AttackableTarget": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "level": {"type": "integer"},
                        "controlling_alliance": {"type": "integer", "nullable": True},
                        "active_npcs": {"type": "integer"},
                        "max_npcs": {"type": "integer"},
                        "garrison_count": {"type": "integer"}
                    }
                },
                "Position": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number"},
                        "y": {"type": "number"}
                    }
                },
                "HeroSets": {
                    "type": "object",
                    "properties": {
                        "alliance_id": {"type": "integer"},
                        "available_hero_sets": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/HeroSet"}
                        },
                        "total_count": {"type": "integer"}
                    }
                },
                "HeroSet": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "owner_id": {"type": "string"},
                        "living_heroes": {"type": "integer"},
                        "total_attack": {"type": "integer"},
                        "average_defense": {"type": "number"},
                        "total_hp": {"type": "number"},
                        "max_hp": {"type": "number"},
                        "can_attack": {"type": "boolean"},
                        "is_garrisoned": {"type": "boolean"}
                    }
                },
                "BattleList": {
                    "type": "object",
                    "properties": {
                        "active_battles": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/BattleSummary"}
                        },
                        "total_count": {"type": "integer"}
                    }
                },
                "BattleSummary": {
                    "type": "object",
                    "properties": {
                        "battle_id": {"type": "string"},
                        "stronghold": {"type": "string"},
                        "step": {"type": "integer"},
                        "max_steps": {"type": "integer"},
                        "is_active": {"type": "boolean"},
                        "winner": {"type": "string", "nullable": True},
                        "attacker_living": {"type": "integer"},
                        "defender_living": {"type": "integer"},
                        "current_turn": {"type": "string"}
                    }
                },
                "BattleDetails": {
                    "type": "object",
                    "properties": {
                        "battle_id": {"type": "string"},
                        "stronghold_id": {"type": "string"},
                        "status": {"$ref": "#/components/schemas/BattleSummary"},
                        "recent_log": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "attacking_set": {"$ref": "#/components/schemas/BattleHeroSet"},
                        "defending_set": {"$ref": "#/components/schemas/BattleHeroSet"}
                    }
                },
                "BattleHeroSet": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "living_heroes": {"type": "integer"},
                        "total_hp": {"type": "number"},
                        "max_hp": {"type": "number"}
                    }
                },
                "StrongholdList": {
                    "type": "object",
                    "properties": {
                        "strongholds": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Stronghold"}
                        },
                        "total_count": {"type": "integer"}
                    }
                },
                "Stronghold": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "level": {"type": "integer"},
                        "position": {"$ref": "#/components/schemas/Position"},
                        "controlling_alliance": {"type": "integer", "nullable": True},
                        "is_alliance_home": {"type": "boolean"},
                        "is_protected": {"type": "boolean"},
                        "can_be_attacked": {"type": "boolean"},
                        "active_npcs": {"type": "integer"},
                        "max_npcs": {"type": "integer"},
                        "garrison_count": {"type": "integer"},
                        "max_garrison": {"type": "integer"},
                        "connections": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "MapLayout": {
                    "type": "object",
                    "properties": {
                        "map_width": {"type": "integer"},
                        "map_height": {"type": "integer"},
                        "strongholds": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/MapStronghold"}
                        },
                        "connections": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/MapConnection"}
                        }
                    }
                },
                "MapStronghold": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "level": {"type": "integer"},
                        "is_home": {"type": "boolean"},
                        "controlling_alliance": {"type": "integer", "nullable": True}
                    }
                },
                "MapConnection": {
                    "type": "object",
                    "properties": {
                        "from": {"type": "string"},
                        "to": {"type": "string"}
                    }
                }
            }
        }
    }

def create_swagger_app():
    """Create Flask app with Swagger UI"""
    app = Flask(__name__)
    
    # Swagger UI blueprint
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/swagger.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Summit Showdown ML/RL API"
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    @app.route('/api/swagger.json')
    def swagger_spec():
        return jsonify(create_swagger_spec())
    
    return app

if __name__ == '__main__':
    # Generate swagger.json file
    spec = create_swagger_spec()
    with open('swagger.json', 'w') as f:
        json.dump(spec, f, indent=2)
    print("Generated swagger.json file")
    
    # Run swagger UI server
    app = create_swagger_app()
    print("Starting Swagger UI server at http://localhost:5001/api/docs")
    app.run(host='0.0.0.0', port=5001, debug=True)