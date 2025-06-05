# game_simulator/utils/vector.py
import math

class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
        
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
        
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
        
    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
        
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
        
    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)
        
    def distance_to(self, other):
        return (self - other).magnitude()
        
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"