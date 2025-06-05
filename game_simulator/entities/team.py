# game_simulator/entities/team.py
class Team:
    def __init__(self, name, color=(255, 255, 255)):
        self.name = name
        self.color = color
        self.units = []
        self.resources = 100
        self.towers_controlled = []
        
    def add_unit(self, unit):
        self.units.append(unit)
        unit.team = self.name
        
    def remove_unit(self, unit):
        if unit in self.units:
            self.units.remove(unit)
            
    def add_tower(self, tower_id):
        if tower_id not in self.towers_controlled:
            self.towers_controlled.append(tower_id)
            
    def remove_tower(self, tower_id):
        if tower_id in self.towers_controlled:
            self.towers_controlled.remove(tower_id)
            
    def get_alive_units(self):
        return [unit for unit in self.units if unit.is_alive()]
        
    def __repr__(self):
        return f"Team({self.name}, Units: {len(self.units)}, Towers: {len(self.towers_controlled)})"