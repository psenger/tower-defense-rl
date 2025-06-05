# game_simulator/map_layout.py
from .entities.stronghold import Stronghold

def create_game_map():
    """Create the complete game map with all strongholds and connections based on SVG layout"""
    strongholds = {}
    
    # Create a 10x7 grid layout for map area (1280x520) - dedicated map section
    map_width = 1280
    map_height = 520  # Reserve bottom 200px for info panels
    grid_width = 10
    grid_height = 7
    cell_width = map_width // grid_width   # 128 pixels per cell
    cell_height = map_height // grid_height  # 74 pixels per cell
    
    def grid_pos(col, row):
        """Convert grid coordinates to pixel coordinates (centered in cell)"""
        return (col * cell_width + cell_width // 2, row * cell_height + cell_height // 2)
    
    # Alliance Homes (per README grid layout)
    alliance_homes = {
        "T1": Stronghold("T1", 1, *grid_pos(1, 0)),    # (1,0)
        "T2": Stronghold("T2", 1, *grid_pos(9, 0)),    # (9,0) 
        "T3": Stronghold("T3", 1, *grid_pos(9, 6)),    # (9,6)
        "T4": Stronghold("T4", 1, *grid_pos(1, 6))     # (1,6)
    }
    
    # Set as alliance homes
    alliance_homes["T1"].set_as_alliance_home(1)
    alliance_homes["T2"].set_as_alliance_home(2)
    alliance_homes["T3"].set_as_alliance_home(3)
    alliance_homes["T4"].set_as_alliance_home(4)
    
    # Level 1 Strongholds positioned according to README grid layout
    level1_positions = [
        # Row 0: S1-1 at center-top
        ("S1-1", *grid_pos(5, 0)),   # (5,0)
        
        # Row 1: S1-2, S1-3, S1-4, S1-5
        ("S1-2", *grid_pos(2, 1)),   # (2,1)
        ("S1-3", *grid_pos(4, 1)),   # (4,1)
        ("S1-4", *grid_pos(6, 1)),   # (6,1)
        ("S1-5", *grid_pos(8, 1)),   # (8,1)
        
        # Row 2: S1-6, S1-7
        ("S1-6", *grid_pos(2, 2)),   # (2,2)
        ("S1-7", *grid_pos(8, 2)),   # (8,2)
        
        # Row 3: S1-12, S1-8
        ("S1-12", *grid_pos(1, 3)),  # (1,3)
        ("S1-8", *grid_pos(9, 3)),   # (9,3)
        
        # Row 4: S1-13, S1-14
        ("S1-13", *grid_pos(2, 4)),  # (2,4)
        ("S1-14", *grid_pos(8, 4)),  # (8,4)
        
        # Row 5: S1-18, S1-17, S1-16, S1-15
        ("S1-18", *grid_pos(2, 5)),  # (2,5)
        ("S1-17", *grid_pos(4, 5)),  # (4,5)
        ("S1-16", *grid_pos(6, 5)),  # (6,5)
        ("S1-15", *grid_pos(8, 5)),  # (8,5)
        
        # S1-19 - placing at (5,5) since it's missing from grid but in connections
        ("S1-19", *grid_pos(5, 6)),  # (5,5) - estimated position
    ]
    
    level1_strongholds = {}
    for sid, x, y in level1_positions:
        level1_strongholds[sid] = Stronghold(sid, 1, x, y)
    
    # Level 2 Strongholds (per README: S2-11 and S2-9)
    level2_strongholds = {
        "S2-11": Stronghold("S2-11", 2, *grid_pos(4, 3)),   # (4,3) - center-left
        "S2-9": Stronghold("S2-9", 2, *grid_pos(6, 3)),     # (6,3) - center-right
    }
    
    # Level 3 Stronghold (per README: S3-10 at center)
    level3_strongholds = {
        "S3-10": Stronghold("S3-10", 3, *grid_pos(5, 3)),   # (5,3) - true center
    }
    
    # Combine all strongholds
    strongholds.update(alliance_homes)
    strongholds.update(level1_strongholds)
    strongholds.update(level2_strongholds)
    strongholds.update(level3_strongholds)
    
    # Set up connections based on README Network Node Table
    connections = {
        # Alliance Homes
        "T1": ["S1-2"],
        "T2": ["S1-5"],
        "T3": ["S1-15"],
        "T4": ["S1-18"],
        
        # Level 1 Strongholds
        "S1-1":  ["S1-3", "S1-4" ],
        "S1-2":  ["T1", "S1-3", "S1-6", "S2-11" ],
        "S1-3":  ["S1-1", "S1-2", "S1-4" ],
        "S1-4":  ["S1-1", "S1-3", "S1-5" ],
        "S1-5":  ["T2", "S1-4", "S1-7", "S2-9" ],
        "S1-6":  ["S1-2", "S1-12", "S1-13" ],
        "S1-7":  ["S1-5", "S1-8", "S1-14" ],
        "S1-8":  ["S1-7", "S1-14" ],
        "S1-12": ["S1-6", "S1-13" ],
        "S1-13": ["S1-6", "S1-12", "S1-18" ],
        "S1-14": ["S1-7", "S1-8", "S1-15" ],
        "S1-15": ["T3", "S1-14", "S1-16", "S2-9" ],
        "S1-16": ["S1-17", "S1-19", "S1-15" ],
        "S1-17": ["S1-16", "S1-19", "S1-18" ],
        "S1-18": ["T4", "S1-13", "S1-17", "S2-11" ],
        "S1-19": ["S1-16", "S1-17" ],
        
        # Level 2 Strongholds
        "S2-9":  ["S1-5", "S1-15", "S3-10"],
        "S2-11": ["S1-2", "S1-18", "S3-10"],
        
        # Level 3 Stronghold
        "S3-10": ["S2-9", "S2-11"],
    }
    
    # Apply connections to strongholds
    for stronghold_id, connected_ids in connections.items():
        if stronghold_id in strongholds:
            strongholds[stronghold_id].connections = connected_ids
    
    return strongholds

def get_stronghold_layout_info():
    """Get information about the map layout for display purposes"""
    return {
        "alliance_homes": ["T1", "T2", "T3", "T4"],
        "level_1": ["S1-1", "S1-2", "S1-3", "S1-4", "S1-5", "S1-6", "S1-7", "S1-8", 
                    "S1-12", "S1-13", "S1-14", "S1-15", "S1-16", "S1-17", "S1-18", "S1-19"],
        "level_2": ["S2-9", "S2-11"],
        "level_3": ["S3-10"],
        "total_strongholds": 23,  # 4 homes + 16 L1 + 2 L2 + 1 L3
    }

def get_adjacent_strongholds(strongholds, alliance_controlled_strongholds):
    """Get strongholds that can be attacked by an alliance"""
    attackable = set()
    for controlled_id in alliance_controlled_strongholds:
        if controlled_id in strongholds:
            for connected_id in strongholds[controlled_id].connections:
                if connected_id in strongholds:
                    # Can attack if not controlled by same alliance
                    target = strongholds[connected_id]
                    if target.controlling_alliance != strongholds[controlled_id].controlling_alliance:
                        attackable.add(connected_id)
    return list(attackable)