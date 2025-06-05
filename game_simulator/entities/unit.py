# game_simulator/entities/unit.py
import pygame

class Unit:
    def __init__(self, id, unit_type, team, hp=100, attack=10, defense=5):
        self.id = id
        self.type = unit_type
        self.team = team
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.pos = pygame.math.Vector2(0, 0)
        self.target_pos = None
        self.speed = 50  # pixels per second
        self.current_tower = None
        self.target_tower = None
        
    def move_towards_target(self, dt):
        if self.target_pos and self.pos.distance_to(self.target_pos) > 1:
            direction = (self.target_pos - self.pos).normalize()
            self.pos += direction * self.speed * dt
        
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return self.hp <= 0
        
    def is_alive(self):
        return self.hp > 0
        
    def __repr__(self):
        return f"Unit({self.id}, {self.type}, Team: {self.team}, HP: {self.hp}/{self.max_hp})"