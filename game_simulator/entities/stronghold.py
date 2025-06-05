# game_simulator/entities/stronghold.py
import time
from .hero_set import HeroSet

class Stronghold:
    def __init__(self, stronghold_id, level, x, y, connections=None):
        self.id = stronghold_id
        self.level = level  # 1, 2, or 3
        self.x = x
        self.y = y
        self.connections = connections or []
        
        # Control and status
        self.controlling_alliance = None
        self.is_alliance_home = False
        self.home_alliance_id = None
        
        # Protection
        self.protection_end_time = 0  # Timestamp when protection ends
        self.is_protected = False
        
        # NPC Defense Teams
        self.npc_defense_teams = []
        self.max_npc_teams = self._get_max_npc_teams()
        self.npc_teams_defeated_by_alliance = {}  # Track which alliance defeated which NPCs
        
        # Player Garrison
        self.garrisoned_hero_sets = []
        self.max_garrison_size = self._get_max_garrison_size()
        
        # Initialize with full NPC complement
        self._generate_npc_teams()
    
    def _get_max_npc_teams(self):
        """Get maximum NPC teams based on stronghold level"""
        npc_counts = {1: 9, 2: 12, 3: 15}
        return npc_counts.get(self.level, 9)
    
    def _get_max_garrison_size(self):
        """Get maximum garrison size based on stronghold level"""
        garrison_limits = {1: 9, 2: 7, 3: 5}
        return garrison_limits.get(self.level, 9)
    
    def _generate_npc_teams(self):
        """Generate initial NPC defense teams"""
        self.npc_defense_teams = []
        for i in range(self.max_npc_teams):
            team_id = f"{self.id}_NPC_{i+1}"
            npc_team = HeroSet(team_id, "NPC", is_npc=True, stronghold_level=self.level)
            self.npc_defense_teams.append(npc_team)
    
    def is_neutral(self):
        """Check if stronghold is neutral (no alliance control)"""
        return self.controlling_alliance is None and not self.is_alliance_home
    
    def has_npc_teams(self):
        """Check if stronghold has any NPC defense teams"""
        return len(self.npc_defense_teams) > 0
    
    def get_active_npc_teams(self):
        """Get NPC teams that are still alive"""
        return [team for team in self.npc_defense_teams if not team.is_defeated()]
    
    def remove_defeated_npc_team(self, npc_team, defeating_alliance_id):
        """Remove a defeated NPC team and track which alliance defeated it"""
        if npc_team in self.npc_defense_teams:
            self.npc_defense_teams.remove(npc_team)
            
            # Track which alliance defeated this team
            if defeating_alliance_id not in self.npc_teams_defeated_by_alliance:
                self.npc_teams_defeated_by_alliance[defeating_alliance_id] = 0
            self.npc_teams_defeated_by_alliance[defeating_alliance_id] += 1
    
    def check_capturable(self):
        """Check if stronghold can be captured (all NPCs defeated)"""
        return len(self.get_active_npc_teams()) == 0 and not self.is_alliance_home
    
    def capture_by_alliance(self, alliance_id, protection_duration_minutes=20):
        """Capture stronghold by alliance - returns the ID of alliance that actually captures"""
        if not self.check_capturable():
            return None
        
        # Determine capturing alliance based on who defeated most NPCs
        if not self.npc_teams_defeated_by_alliance:
            return None
        
        # Find alliance that defeated most NPC teams
        defeating_alliance = max(self.npc_teams_defeated_by_alliance.items(), key=lambda x: x[1])
        capturing_alliance_id = defeating_alliance[0]
        
        # Handle ties by first to reach the count (simplified: use lexicographic order)
        max_defeats = defeating_alliance[1]
        tied_alliances = [aid for aid, count in self.npc_teams_defeated_by_alliance.items() if count == max_defeats]
        if len(tied_alliances) > 1:
            capturing_alliance_id = min(tied_alliances)  # Simplified tie-breaking
        
        # The alliance that defeated the most NPCs gets to capture
        self.controlling_alliance = capturing_alliance_id
        self.start_protection(protection_duration_minutes)
        
        # Clear NPC defeat tracking for future captures
        self.npc_teams_defeated_by_alliance = {}
        
        return capturing_alliance_id  # Return the ID of the alliance that actually captured
    
    def start_protection(self, duration_minutes):
        """Start protection period"""
        self.protection_end_time = time.time() + (duration_minutes * 60)
        self.is_protected = True
    
    def update_protection_status(self):
        """Update protection status based on current time"""
        if self.is_protected and time.time() >= self.protection_end_time:
            self.is_protected = False
    
    def can_be_attacked(self):
        """Check if stronghold can currently be attacked"""
        self.update_protection_status()
        return not self.is_protected
    
    def add_garrison_set(self, hero_set):
        """Add a hero set to garrison"""
        if len(self.garrisoned_hero_sets) < self.max_garrison_size:
            if hero_set not in self.garrisoned_hero_sets:
                self.garrisoned_hero_sets.append(hero_set)
                hero_set.assign_to_garrison(self.id)
                return True
        return False
    
    def remove_garrison_set(self, hero_set):
        """Remove a hero set from garrison"""
        if hero_set in self.garrisoned_hero_sets:
            self.garrisoned_hero_sets.remove(hero_set)
            hero_set.remove_from_garrison()
            return True
        return False
    
    def get_all_defending_sets(self):
        """Get all defending sets (NPCs + garrisoned players)"""
        defending_sets = list(self.get_active_npc_teams())
        # Only include non-defeated garrisoned sets
        active_garrison = [hero_set for hero_set in self.garrisoned_hero_sets if not hero_set.is_defeated()]
        defending_sets.extend(active_garrison)
        return defending_sets
    
    def cleanup_defeated_defenders(self):
        """Remove all defeated hero sets from stronghold immediately"""
        # NOTE: NPCs are already properly removed by remove_defeated_npc_team() during battle resolution
        # Do NOT remove them here as it interferes with capture tracking
        
        # Remove defeated garrison sets immediately  
        defeated_garrison = [hero_set for hero_set in self.garrisoned_hero_sets if hero_set.is_defeated()]
        for defeated_set in defeated_garrison:
            self.garrisoned_hero_sets.remove(defeated_set)
            defeated_set.remove_from_garrison()
    
    def respawn_npcs_if_neutral(self):
        """Respawn NPCs if stronghold is neutral (for second half)"""
        if self.is_neutral():
            self._generate_npc_teams()
            self.npc_teams_defeated_by_alliance = {}
    
    def set_as_alliance_home(self, alliance_id):
        """Set this stronghold as an alliance home"""
        self.is_alliance_home = True
        self.home_alliance_id = alliance_id
        self.controlling_alliance = alliance_id
        # Alliance homes have no NPCs and can't be captured
        self.npc_defense_teams = []
    
    def end_all_protection(self):
        """End protection immediately (for second half start)"""
        self.is_protected = False
        self.protection_end_time = 0
    
    def __repr__(self):
        status_parts = []
        if self.is_alliance_home:
            status_parts.append(f"Home of Alliance {self.home_alliance_id}")
        elif self.controlling_alliance:
            status_parts.append(f"Controlled by Alliance {self.controlling_alliance}")
        else:
            status_parts.append("Neutral")
        
        if self.is_protected:
            status_parts.append("Protected")
        
        npc_count = len(self.get_active_npc_teams())
        garrison_count = len(self.garrisoned_hero_sets)
        
        status = ", ".join(status_parts)
        return f"Stronghold({self.id}, L{self.level}, NPCs:{npc_count}/{self.max_npc_teams}, Garrison:{garrison_count}/{self.max_garrison_size}, {status})"