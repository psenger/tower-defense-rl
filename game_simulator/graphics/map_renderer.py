# game_simulator/graphics/map_renderer.py
import pygame
import config

class MapRenderer:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 16)
        self.small_font = pygame.font.SysFont(None, 12)
        
        # Screen layout constants
        self.MAP_HEIGHT = 520  # Top section for map
        self.INFO_HEIGHT = 200  # Bottom section for info
        self.TOTAL_HEIGHT = 720
        self.SCREEN_WIDTH = 1280
        
        # Alliance colors
        self.alliance_colors = {
            1: (200, 100, 100),  # Red
            2: (100, 100, 200),  # Blue  
            3: (100, 200, 100),  # Green
            4: (200, 200, 100),  # Yellow
        }
        
        # Stronghold level sizes
        self.level_radii = {1: 20, 2: 25, 3: 30}
        self.home_radius = 35
        
        # Colors
        self.neutral_color = (150, 150, 150)
        self.connection_color = (80, 80, 80)
        self.npc_color = (120, 80, 40)
        self.protection_color = (255, 255, 0)
        self.battle_color = (255, 100, 100)

    def draw(self, surface, game_state, time_scale=1.0):
        # Clear entire screen
        surface.fill((40, 40, 50))
        
        # Create map surface (top section)
        map_surface = surface.subsurface((0, 0, self.SCREEN_WIDTH, self.MAP_HEIGHT))
        
        # Draw map elements on the map surface
        self._draw_map_section(map_surface, game_state)
        
        # Draw info section (bottom section)
        self._draw_info_section(surface, game_state, time_scale)
    
    def _draw_map_section(self, map_surface, game_state):
        """Draw the map in the top section"""
        # Clear map background
        map_surface.fill((40, 40, 50))
        
        # Draw connections first (behind strongholds)
        self._draw_connections(map_surface, game_state)
        
        # Draw strongholds
        self._draw_strongholds(map_surface, game_state)
        
        # Draw battle indicators
        self._draw_battle_indicators(map_surface, game_state)
        
        # Draw border between sections
        pygame.draw.line(map_surface.get_parent(), (100, 100, 100), 
                        (0, self.MAP_HEIGHT), (self.SCREEN_WIDTH, self.MAP_HEIGHT), 2)
    
    def _draw_connections(self, surface, game_state):
        """Draw connection lines between strongholds"""
        for stronghold_id, stronghold in game_state.strongholds.items():
            for connected_id in stronghold.connections:
                connected = game_state.get_stronghold(connected_id)
                if connected:
                    start_pos = (stronghold.x, stronghold.y)
                    end_pos = (connected.x, connected.y)
                    pygame.draw.line(surface, self.connection_color, start_pos, end_pos, 2)
    
    def _draw_strongholds(self, surface, game_state):
        """Draw all strongholds with their status"""
        for stronghold_id, stronghold in game_state.strongholds.items():
            self._draw_single_stronghold(surface, stronghold, game_state)
    
    def _draw_single_stronghold(self, surface, stronghold, game_state):
        """Draw a single stronghold"""
        x, y = stronghold.x, stronghold.y
        
        # Determine radius based on type
        if stronghold.is_alliance_home:
            radius = self.home_radius
        else:
            radius = self.level_radii.get(stronghold.level, 20)
        
        # Determine color based on control
        if stronghold.controlling_alliance:
            color = self.alliance_colors.get(stronghold.controlling_alliance, self.neutral_color)
        else:
            color = self.neutral_color
        
        # Draw stronghold circle
        pygame.draw.circle(surface, color, (x, y), radius)
        
        # Draw border (thicker for alliance homes)
        border_width = 4 if stronghold.is_alliance_home else 2
        pygame.draw.circle(surface, (0, 0, 0), (x, y), radius, border_width)
        
        # Protection indicator
        if stronghold.is_protected:
            pygame.draw.circle(surface, self.protection_color, (x, y), radius + 3, 2)
        
        # Draw stronghold ID
        id_text = self.font.render(stronghold.id, True, (255, 255, 255))
        text_rect = id_text.get_rect(center=(x, y - 5))
        surface.blit(id_text, text_rect)
        
        # Draw level indicator for non-home strongholds
        if not stronghold.is_alliance_home:
            level_text = self.small_font.render(f"L{stronghold.level}", True, (200, 200, 200))
            level_rect = level_text.get_rect(center=(x, y + 8))
            surface.blit(level_text, level_rect)
        
        # Draw NPC count and garrison info
        self._draw_stronghold_details(surface, stronghold, x, y + radius + 10)
    
    def _draw_stronghold_details(self, surface, stronghold, x, y):
        """Draw detailed info below stronghold"""
        details = []
        
        # NPC teams remaining
        active_npcs = len(stronghold.get_active_npc_teams())
        if active_npcs > 0:
            details.append(f"NPCs: {active_npcs}/{stronghold.max_npc_teams}")
        
        # Garrison count
        garrison_count = len(stronghold.garrisoned_hero_sets)
        if garrison_count > 0:
            details.append(f"Garrison: {garrison_count}/{stronghold.max_garrison_size}")
        
        # Draw details
        for i, detail in enumerate(details):
            detail_text = self.small_font.render(detail, True, (200, 200, 200))
            detail_rect = detail_text.get_rect(center=(x, y + i * 12))
            surface.blit(detail_text, detail_rect)
    
    def _draw_battle_indicators(self, surface, game_state):
        """Draw indicators for ongoing battles"""
        for battle in game_state.active_battles:
            stronghold = game_state.get_stronghold(battle.stronghold_id)
            if stronghold:
                # Pulsing battle indicator
                import time
                pulse = int(abs(time.time() * 3) % 2)
                battle_radius = 8 + pulse * 3
                
                pygame.draw.circle(surface, self.battle_color, 
                                 (stronghold.x + 25, stronghold.y - 25), battle_radius)
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (stronghold.x + 25, stronghold.y - 25), battle_radius, 1)
                
                # Battle text
                battle_text = self.small_font.render("!", True, (255, 255, 255))
                text_rect = battle_text.get_rect(center=(stronghold.x + 25, stronghold.y - 25))
                surface.blit(battle_text, text_rect)
    
    def _draw_info_section(self, surface, game_state, time_scale=1.0):
        """Draw all information in the bottom section"""
        info_y_start = self.MAP_HEIGHT
        
        # Clear info section background
        info_rect = pygame.Rect(0, info_y_start, self.SCREEN_WIDTH, self.INFO_HEIGHT)
        pygame.draw.rect(surface, (25, 25, 35), info_rect)
        
        # Game status
        status = game_state.get_game_status()
        
        # Enhanced speed status with scrubber info
        if hasattr(game_state, 'engine') and getattr(game_state.engine, 'scrubber_mode', False):
            scrubber_time = getattr(game_state.engine, 'target_game_minutes', 0)
            speed_status = f"SCRUBBER: {scrubber_time:.1f} min"
        else:
            speed_status = "PAUSED" if time_scale == 0 else f"Speed: x{time_scale:.1f}"
        
        # Left column - Game status and time
        left_col_x = 15
        left_col_y = info_y_start + 15
        line_height = 18
        
        # Convert game time to minutes for display
        game_minutes = status['game_time'] / 60.0
        game_hours = int(game_minutes // 60)
        remaining_minutes = game_minutes % 60
        
        game_info = [
            f"Half: {status['half']} | Game Time: {game_hours:02d}h {remaining_minutes:04.1f}m | {speed_status}",
            f"Active Battles: {status['active_battles']} | Neutral Strongholds: {status['stronghold_control'].get('neutral', 0)}"
        ]
        
        for i, line in enumerate(game_info):
            text = self.font.render(line, True, (255, 255, 255))
            surface.blit(text, (left_col_x, left_col_y + i * line_height))
        
        # Alliance status - arranged horizontally with more vertical space
        alliance_y = left_col_y + len(game_info) * line_height + 10
        alliance_x_spacing = 300
        alliance_line_height = 35  # Increased height for two lines per alliance
        
        for i, alliance_id in enumerate(sorted(game_state.alliances.keys())):
            alliance = game_state.alliances[alliance_id]
            controlled = len(status['stronghold_control'].get(alliance_id, []))
            score = status['alliance_scores'].get(alliance_id, 0)
            available_sets = alliance.get_available_hero_sets_count()
            
            x_pos = left_col_x + (i % 2) * alliance_x_spacing
            y_pos = alliance_y + (i // 2) * alliance_line_height
            
            # Draw colored indicator
            color = self.alliance_colors.get(alliance_id, (150, 150, 150))
            indicator_rect = pygame.Rect(x_pos, y_pos + 3, 15, 15)
            pygame.draw.rect(surface, color, indicator_rect)
            pygame.draw.rect(surface, (255, 255, 255), indicator_rect, 1)
            
            # Alliance name and strongholds (first line)
            alliance_text = f"{alliance.name}: {controlled} strongholds, {score} points"
            text = self.font.render(alliance_text, True, (255, 255, 255))
            surface.blit(text, (x_pos + 20, y_pos))
            
            # Hero sets available (second line)
            sets_text = f"Available Hero Sets: {available_sets}"
            sets_render = self.small_font.render(sets_text, True, (200, 200, 200))
            surface.blit(sets_render, (x_pos + 20, y_pos + 16))
        
        # Controls help - right side of info section
        controls_x = self.SCREEN_WIDTH - 650
        controls_y = info_y_start + 15
        
        controls = [
            "Controls:",
            "SPACE=Pause/Resume | M=Map View | B=Cycle Battles | L=Battle List",
            "LEFT/RIGHT=Speed/Scrub | S=Scrubber Mode | F=Fast View (5min)",
            "UP/DOWN=Navigate | ENTER=Select | ESC=Exit | 1-4=Test Attack"
        ]
        
        # Draw controls background
        controls_height = len(controls) * 16 + 10
        controls_rect = pygame.Rect(controls_x - 5, controls_y - 5, 640, controls_height)
        pygame.draw.rect(surface, (20, 20, 30, 180), controls_rect)
        pygame.draw.rect(surface, (100, 100, 100), controls_rect, 1)
        
        for i, control_text in enumerate(controls):
            color = (220, 220, 220) if i == 0 else (180, 180, 180)
            text = self.small_font.render(control_text, True, color)
            surface.blit(text, (controls_x, controls_y + i * 16))