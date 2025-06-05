# game_simulator/entities/tower.py
import pygame
import config

class Tower:
    def __init__(self, id, x, y, connections=None):
        self.id = id
        self.pos = pygame.math.Vector2(x, y)
        self.radius = config.TOWER_RADIUS
        self.owner = None  # e.g., "player", "enemy", None
        self.progress = 0  # 0 to 100
        self.units_stationed = []
        self.connections = connections if connections else [] # List of tower IDs it's connected to
        self.color = config.TOWER_COLOR_NEUTRAL

    def update_visuals(self):
        if self.owner == "player":
            self.color = config.TOWER_COLOR_PLAYER
        elif self.owner == "enemy":
            self.color = config.TOWER_COLOR_ENEMY
        else:
            self.color = config.TOWER_COLOR_NEUTRAL

    def __repr__(self):
        return f"Tower({self.id} at {self.pos}, Owner: {self.owner})"