# game_simulator/entities/alliance.py
from .player import Player

class Alliance:
    def __init__(self, alliance_id, name, color=(255, 255, 255)):
        self.id = alliance_id
        self.name = name
        self.color = color
        self.players = []
        
        # Stronghold control
        self.controlled_strongholds = []
        self.home_stronghold = None  # Alliance Home
        
        # Leadership
        self.leader_id = None
        self.co_leader_id = None
        
        # Scoring
        self.summit_showdown_points = 0
        
        # Generate 50 players for this alliance
        self._generate_players()
    
    def _generate_players(self):
        """Generate 50 players for this alliance"""
        self.players = []
        for i in range(50):
            player_id = f"A{self.id}_P{i+1}"
            player = Player(player_id, self.id)
            player.select_hero_sets()  # Auto-select first 30 heroes
            self.players.append(player)
        
        # Set first player as leader, second as co-leader
        if self.players:
            self.leader_id = self.players[0].id
            if len(self.players) > 1:
                self.co_leader_id = self.players[1].id
    
    def get_player(self, player_id):
        """Get a specific player by ID"""
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def get_all_available_hero_sets(self):
        """Get all hero sets available for attacks across all players"""
        available_sets = []
        for player in self.players:
            available_sets.extend(player.get_available_sets_for_attack())
        return available_sets
    
    def get_available_hero_sets_count(self):
        """Get count of hero sets available for attacks"""
        return len(self.get_all_available_hero_sets())
    
    def get_all_garrisoned_hero_sets(self):
        """Get all hero sets currently garrisoning strongholds"""
        garrisoned_sets = []
        for player in self.players:
            garrisoned_sets.extend(player.get_garrisoned_sets())
        return garrisoned_sets
    
    def add_stronghold(self, stronghold_id):
        """Add a stronghold to alliance control"""
        if stronghold_id not in self.controlled_strongholds:
            self.controlled_strongholds.append(stronghold_id)
    
    def remove_stronghold(self, stronghold_id):
        """Remove a stronghold from alliance control"""
        if stronghold_id in self.controlled_strongholds:
            self.controlled_strongholds.remove(stronghold_id)
    
    def set_home_stronghold(self, stronghold_id):
        """Set the alliance home stronghold"""
        self.home_stronghold = stronghold_id
        self.add_stronghold(stronghold_id)
    
    def get_total_power_rating(self):
        """Calculate total power rating of all players"""
        return sum(player.get_total_power_rating() for player in self.players)
    
    def get_active_players(self):
        """Get players who can still attack (have stamina and available sets)"""
        return [player for player in self.players if player.can_attack()]
    
    def restore_all_stamina_for_new_half(self):
        """Restore stamina for all players for new half"""
        for player in self.players:
            player.restore_stamina_for_new_half()
    
    def reset_all_hero_sets_for_new_half(self):
        """Reset all hero sets for new half"""
        for player in self.players:
            player.reset_hero_sets_for_new_half()
    
    def add_summit_points(self, points):
        """Add Summit Showdown Points"""
        self.summit_showdown_points += points
    
    def __repr__(self):
        active_players = len(self.get_active_players())
        return f"Alliance({self.id}, {self.name}, Players:{len(self.players)}, Active:{active_players}, Strongholds:{len(self.controlled_strongholds)}, Points:{self.summit_showdown_points})"