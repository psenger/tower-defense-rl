# game_simulator/graphics/battle_renderer.py
import pygame
import config

class BattleRenderer:
    def __init__(self):
        self.title_font = pygame.font.SysFont(None, 36)
        self.header_font = pygame.font.SysFont(None, 28)
        self.text_font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        self.detail_font = pygame.font.SysFont(None, 16)

        # Colors
        self.bg_color = (30, 30, 40)
        self.panel_color = (50, 50, 60)
        self.border_color = (80, 80, 90)
        self.attacker_color = (200, 100, 100)
        self.defender_color = (100, 100, 200)
        self.npc_color = (150, 100, 50)
        self.neutral_color = (150, 150, 150)
        self.text_color = (255, 255, 255)
        self.hp_bar_bg = (60, 60, 60)
        self.hp_bar_full = (100, 200, 100)
        self.hp_bar_damaged = (200, 150, 50)
        self.hp_bar_critical = (200, 50, 50)

        # Alliance colors
        self.alliance_colors = {
            1: (200, 100, 100),  # Red
            2: (100, 100, 200),  # Blue
            3: (100, 200, 100),  # Green
            4: (200, 200, 100),  # Yellow
        }

    def draw_stronghold_battle_view(self, surface, battle, stronghold, battle_index, total_battles, game_state):
        """Draw a battle happening at a specific stronghold"""
        # Clear background
        surface.fill(self.bg_color)

        # Get battle status
        status = battle.get_battle_status()

        # Title with stronghold and battle info
        title_text = f"Battle {battle_index + 1}/{total_battles} at {stronghold.id} (Level {stronghold.level})"
        self._draw_text(surface, title_text, self.title_font, self.text_color, 20, 20)

        # Stronghold control info
        if stronghold.controlling_alliance:
            alliance = game_state.get_alliance(stronghold.controlling_alliance)
            control_color = self.alliance_colors.get(stronghold.controlling_alliance, self.neutral_color)
            control_text = f"Controlled by {alliance.name if alliance else f'Alliance {stronghold.controlling_alliance}'}"
        else:
            control_color = self.neutral_color
            control_text = "Neutral Stronghold"

        self._draw_text(surface, control_text, self.text_font, control_color, 20, 55)

        # Battle progress
        battle_status = "Active" if status['is_active'] else f"Ended - {status['winner']} wins"
        status_text = f"Step: {status['step']}/{status['max_steps']} | Turn: {status['current_turn']} | Status: {battle_status}"
        self._draw_text(surface, status_text, self.header_font, self.text_color, 20, 85)

        # Damage totals
        damage_text = f"Total Damage - Attackers: {status['attacker_damage']:.0f} | Defenders: {status['defender_damage']:.0f}"
        self._draw_text(surface, damage_text, self.text_font, self.text_color, 20, 115)

        # Draw combatants
        panel_width = (surface.get_width() - 60) // 2
        panel_height = 280

        # Attackers panel
        attacker_rect = pygame.Rect(20, 150, panel_width, panel_height)
        attacking_alliance = self._get_alliance_by_set(battle.attacking_set, game_state)
        attacker_title = f"ATTACKERS - {attacking_alliance.name if attacking_alliance else 'Unknown'}"
        attacker_color = self.alliance_colors.get(attacking_alliance.id if attacking_alliance else 0, self.attacker_color)
        self._draw_hero_set_panel(surface, attacker_rect, battle.attacking_set, attacker_title, attacker_color)

        # Defenders panel
        defender_rect = pygame.Rect(40 + panel_width, 150, panel_width, panel_height)
        if battle.defending_set.is_npc:
            defender_title = f"DEFENDERS - NPC Team (Level {stronghold.level})"
            defender_color = self.npc_color
        else:
            defending_alliance = self._get_alliance_by_set(battle.defending_set, game_state)
            defender_title = f"DEFENDERS - {defending_alliance.name if defending_alliance else 'Unknown'}"
            defender_color = self.alliance_colors.get(defending_alliance.id if defending_alliance else 0, self.defender_color)

        self._draw_hero_set_panel(surface, defender_rect, battle.defending_set, defender_title, defender_color)

        # Battle log
        log_y = 450
        self._draw_battle_log(surface, battle, 20, log_y, surface.get_width() - 40)

        # Navigation instructions
        nav_y = surface.get_height() - 60
        if total_battles > 1:
            nav_text = f"UP/DOWN: Navigate battles at {stronghold.id} | ENTER: Detailed view | ESC: Return to map"
        else:
            nav_text = "ENTER: Detailed view | ESC: Return to map"
        self._draw_text(surface, nav_text, self.small_font, self.neutral_color, 20, nav_y)

    def draw_stronghold_status_view(self, surface, stronghold, game_state):
        """Draw stronghold status when no battles are active"""
        # Clear background
        surface.fill(self.bg_color)

        # Title
        title_text = f"Stronghold {stronghold.id} (Level {stronghold.level}) - No Active Battles"
        self._draw_text(surface, title_text, self.title_font, self.text_color, 20, 20)

        # Control status
        if stronghold.controlling_alliance:
            alliance = game_state.get_alliance(stronghold.controlling_alliance)
            control_color = self.alliance_colors.get(stronghold.controlling_alliance, self.neutral_color)
            control_text = f"Controlled by {alliance.name if alliance else f'Alliance {stronghold.controlling_alliance}'}"
        elif stronghold.is_alliance_home:
            control_color = self.alliance_colors.get(stronghold.home_alliance_id, self.neutral_color)
            control_text = f"Alliance {stronghold.home_alliance_id} Home Base"
        else:
            control_color = self.neutral_color
            control_text = "Neutral Stronghold"

        self._draw_text(surface, control_text, self.header_font, control_color, 20, 60)

        # Protection status
        stronghold.update_protection_status(game_state.game_time)
        y_offset = 100

        if stronghold.is_protected:
            time_remaining = stronghold.get_protection_time_remaining(game_state.game_time)
            protection_text = f"🛡️ Protected for {int(time_remaining)} minutes"
            self._draw_text(surface, protection_text, self.text_font, (255, 215, 0), 20, y_offset)
            y_offset += 30

        # Stronghold details in columns
        left_column_x = 50
        right_column_x = 400
        detail_y = y_offset + 20
        line_height = 25

        # Left column - Defenders
        self._draw_text(surface, "DEFENDERS:", self.header_font, self.text_color, left_column_x, detail_y)
        detail_y += 35

        # NPC Teams
        active_npcs = stronghold.get_active_npc_teams()
        npc_text = f"NPC Defense Teams: {len(active_npcs)}/{stronghold.max_npc_teams}"
        self._draw_text(surface, npc_text, self.text_font, self.npc_color, left_column_x, detail_y)
        detail_y += line_height

        # Show some NPC team details
        for i, npc_team in enumerate(active_npcs[:5]):  # Show first 5 NPC teams
            living_heroes = len(npc_team.get_living_heroes())
            npc_detail = f"  • {npc_team.id}: {living_heroes}/5 heroes alive"
            self._draw_text(surface, npc_detail, self.small_font, self.npc_color, left_column_x + 20, detail_y)
            detail_y += 20

        if len(active_npcs) > 5:
            more_text = f"  ... and {len(active_npcs) - 5} more NPC teams"
            self._draw_text(surface, more_text, self.small_font, self.npc_color, left_column_x + 20, detail_y)
            detail_y += 20

        detail_y += 15

        # Player Garrison
        garrison_count = len(stronghold.garrisoned_hero_sets)
        garrison_text = f"Player Garrison: {garrison_count}/{stronghold.max_garrison_size}"
        garrison_color = self.text_color if garrison_count > 0 else self.neutral_color
        self._draw_text(surface, garrison_text, self.text_font, garrison_color, left_column_x, detail_y)
        detail_y += line_height

        # Show garrison details
        for garrison_set in stronghold.garrisoned_hero_sets[:3]:  # Show first 3 garrison sets
            living_heroes = len(garrison_set.get_living_heroes())
            garrison_alliance = self._get_alliance_by_set(garrison_set, game_state)
            alliance_name = garrison_alliance.name if garrison_alliance else "Unknown"
            garrison_detail = f"  • {garrison_set.id} ({alliance_name}): {living_heroes}/5 heroes"
            garrison_color = self.alliance_colors.get(garrison_alliance.id if garrison_alliance else 0, self.text_color)
            self._draw_text(surface, garrison_detail, self.small_font, garrison_color, left_column_x + 20, detail_y)
            detail_y += 20

        # Right column - Stronghold Info
        info_y = y_offset + 55
        self._draw_text(surface, "STRONGHOLD INFO:", self.header_font, self.text_color, right_column_x, info_y)
        info_y += 35

        # Can be attacked
        attackable = stronghold.can_be_attacked()
        attack_text = f"Can be attacked: {'Yes' if attackable else 'No'}"
        attack_color = (100, 200, 100) if attackable else (200, 100, 100)
        self._draw_text(surface, attack_text, self.text_font, attack_color, right_column_x, info_y)
        info_y += line_height

        # Capturable status
        capturable = stronghold.check_capturable()
        capture_text = f"Can be captured: {'Yes' if capturable else 'No'}"
        capture_color = (100, 200, 100) if capturable else (200, 100, 100)
        self._draw_text(surface, capture_text, self.text_font, capture_color, right_column_x, info_y)
        info_y += line_height

        # NPC defeats tracking
        if stronghold.npc_teams_defeated_by_alliance:
            info_y += 10
            self._draw_text(surface, "NPC Teams Defeated:", self.text_font, self.text_color, right_column_x, info_y)
            info_y += 25

            for alliance_id, count in stronghold.npc_teams_defeated_by_alliance.items():
                alliance = game_state.get_alliance(alliance_id)
                alliance_name = alliance.name if alliance else f"Alliance {alliance_id}"
                defeat_text = f"  • {alliance_name}: {count} teams"
                defeat_color = self.alliance_colors.get(alliance_id, self.text_color)
                self._draw_text(surface, defeat_text, self.small_font, defeat_color, right_column_x, info_y)
                info_y += 20

        # Connections
        info_y += 15
        self._draw_text(surface, "Connected to:", self.text_font, self.text_color, right_column_x, info_y)
        info_y += 25

        # Show connections in groups
        connections = stronghold.connections
        for i in range(0, len(connections), 3):  # Show 3 connections per line
            connection_group = connections[i:i+3]
            connection_text = ", ".join(connection_group)
            self._draw_text(surface, f"  {connection_text}", self.small_font, self.neutral_color, right_column_x, info_y)
            info_y += 20

        # Who can attack this stronghold
        info_y += 15
        self._draw_text(surface, "Can be attacked by:", self.text_font, self.text_color, right_column_x, info_y)
        info_y += 25

        attacking_alliances = []
        for alliance_id, alliance in game_state.alliances.items():
            if game_state.can_alliance_attack_stronghold(alliance_id, stronghold.id):
                available_sets = len(alliance.get_all_available_hero_sets())
                if available_sets > 0:
                    attacking_alliances.append((alliance, available_sets))

        if attacking_alliances:
            for alliance, available_sets in attacking_alliances:
                attack_info = f"  • {alliance.name}: {available_sets} hero sets available"
                attack_color = self.alliance_colors.get(alliance.id, self.text_color)
                self._draw_text(surface, attack_info, self.small_font, attack_color, right_column_x, info_y)
                info_y += 20
        else:
            self._draw_text(surface, "  No alliances can currently attack", self.small_font, self.neutral_color, right_column_x, info_y)

        # Instructions
        nav_y = surface.get_height() - 40
        nav_text = "ESC: Return to map | Click other strongholds to observe them"
        self._draw_text(surface, nav_text, self.small_font, self.neutral_color, 20, nav_y)

    def draw_battle_with_stronghold_info(self, surface, battle_instance, game_state):
        """Enhanced battle view showing stronghold context"""
        if not battle_instance:
            self._draw_no_battle(surface)
            return

        # Clear background
        surface.fill(self.bg_color)

        # Get battle status and stronghold info
        status = battle_instance.get_battle_status()
        stronghold = game_state.get_stronghold(battle_instance.stronghold_id)

        # Enhanced title with stronghold info
        if stronghold:
            title_text = f"Battle at {stronghold.id} (Level {stronghold.level}) - Step {status['step']}/{status['max_steps']}"

            # Show stronghold control
            if stronghold.controlling_alliance:
                alliance = game_state.get_alliance(stronghold.controlling_alliance)
                control_text = f"Stronghold controlled by {alliance.name if alliance else f'Alliance {stronghold.controlling_alliance}'}"
                control_color = self.alliance_colors.get(stronghold.controlling_alliance, self.neutral_color)
            else:
                control_text = "Neutral Stronghold"
                control_color = self.neutral_color
        else:
            title_text = f"Battle at {status['stronghold']} - Step {status['step']}/{status['max_steps']}"
            control_text = ""
            control_color = self.neutral_color

        self._draw_text(surface, title_text, self.title_font, self.text_color, 20, 20)

        if control_text:
            self._draw_text(surface, control_text, self.text_font, control_color, 20, 55)

        # Battle status info
        battle_status = "Active" if status['is_active'] else f"Ended - {status['winner']} wins"
        status_text = f"Turn: {status['current_turn']} | Status: {battle_status}"
        self._draw_text(surface, status_text, self.header_font, self.text_color, 20, 85)

        # Show if there are multiple battles at this stronghold
        if stronghold:
            battles_here = [b for b in game_state.active_battles if b.stronghold_id == stronghold.id]
            if len(battles_here) > 1:
                current_battle_index = battles_here.index(battle_instance) + 1 if battle_instance in battles_here else 1
                multi_battle_text = f"Battle {current_battle_index}/{len(battles_here)} at this stronghold (Press B to cycle)"
                self._draw_text(surface, multi_battle_text, self.small_font, (200, 200, 100), 20, 115)
                damage_y = 145
            else:
                damage_y = 115
        else:
            damage_y = 115

        # Damage totals
        damage_text = f"Total Damage - Attackers: {status['attacker_damage']:.0f} | Defenders: {status['defender_damage']:.0f}"
        self._draw_text(surface, damage_text, self.text_font, self.text_color, 20, damage_y)

        # Draw combatants with alliance info
        panel_width = (surface.get_width() - 60) // 2
        panel_height = 280
        panel_y = damage_y + 35

        # Attackers panel with alliance identification
        attacker_rect = pygame.Rect(20, panel_y, panel_width, panel_height)
        attacking_alliance = self._get_alliance_by_set(battle_instance.attacking_set, game_state)
        if attacking_alliance:
            attacker_title = f"ATTACKERS - {attacking_alliance.name}"
            attacker_color = self.alliance_colors.get(attacking_alliance.id, self.attacker_color)
        else:
            attacker_title = "ATTACKERS - Unknown"
            attacker_color = self.attacker_color

        self._draw_hero_set_panel(surface, attacker_rect, battle_instance.attacking_set,
                                 attacker_title, attacker_color)

        # Defenders panel with NPC/alliance identification
        defender_rect = pygame.Rect(40 + panel_width, panel_y, panel_width, panel_height)
        if battle_instance.defending_set.is_npc:
            defender_title = f"DEFENDERS - NPC Team"
            if stronghold:
                defender_title += f" (Level {stronghold.level})"
            defender_color = self.npc_color
        else:
            defending_alliance = self._get_alliance_by_set(battle_instance.defending_set, game_state)
            if defending_alliance:
                defender_title = f"DEFENDERS - {defending_alliance.name} Garrison"
                defender_color = self.alliance_colors.get(defending_alliance.id, self.defender_color)
            else:
                defender_title = "DEFENDERS - Unknown Garrison"
                defender_color = self.defender_color

        self._draw_hero_set_panel(surface, defender_rect, battle_instance.defending_set,
                                 defender_title, defender_color)

        # Battle log
        log_y = panel_y + panel_height + 20
        self._draw_battle_log(surface, battle_instance, 20, log_y, surface.get_width() - 40)

        # Enhanced instructions
        nav_y = surface.get_height() - 40
        nav_text = "ESC: Return to map | B: Cycle battles | Click other strongholds to view their battles"
        self._draw_text(surface, nav_text, self.small_font, self.neutral_color, 20, nav_y)
        """Find which alliance owns a hero set"""
        if hero_set.is_npc:
            return None

        for alliance in game_state.alliances.values():
            for player in alliance.players:
                if hero_set in player.selected_hero_sets:
                    return alliance
        return None

    def draw(self, surface, battle_instance, game_state):
        if not battle_instance:
            self._draw_no_battle(surface)
            return

        # Clear background
        surface.fill(self.bg_color)
        
        # Get battle status
        status = battle_instance.get_battle_status()
        
        # Main title
        title_text = f"Battle at {status['stronghold']} - Step {status['step']}/{status['max_steps']}"
        self._draw_text(surface, title_text, self.title_font, self.text_color, 20, 20)
        
        # Battle status info
        battle_status = "Active" if status['is_active'] else f"Ended - {status['winner']} wins"
        status_text = f"Turn: {status['current_turn']} | Status: {battle_status}"
        self._draw_text(surface, status_text, self.header_font, self.text_color, 20, 60)
        
        # Damage totals
        damage_text = f"Total Damage - Attackers: {status['attacker_damage']:.0f} | Defenders: {status['defender_damage']:.0f}"
        self._draw_text(surface, damage_text, self.text_font, self.text_color, 20, 90)
        
        # Draw two panels side by side
        panel_width = (surface.get_width() - 60) // 2
        panel_height = 300
        
        # Attackers panel
        attacker_rect = pygame.Rect(20, 130, panel_width, panel_height)
        self._draw_hero_set_panel(surface, attacker_rect, battle_instance.attacking_set, 
                                 "ATTACKERS", self.attacker_color)
        
        # Defenders panel  
        defender_rect = pygame.Rect(40 + panel_width, 130, panel_width, panel_height)
        self._draw_hero_set_panel(surface, defender_rect, battle_instance.defending_set,
                                 "DEFENDERS", self.defender_color)
        
        # Battle log
        log_y = 450
        self._draw_battle_log(surface, battle_instance, 20, log_y, surface.get_width() - 40)
    
    def _draw_no_battle(self, surface):
        surface.fill(self.bg_color)
        text = "No active battle selected."
        text_surf = self.header_font.render(text, True, self.neutral_color)
        x = (surface.get_width() - text_surf.get_width()) // 2
        y = (surface.get_height() - text_surf.get_height()) // 2
        surface.blit(text_surf, (x, y))
        
        instruction = "Press 'B' to cycle through battles or 'M' for map view"
        inst_surf = self.text_font.render(instruction, True, self.neutral_color)
        x = (surface.get_width() - inst_surf.get_width()) // 2
        surface.blit(inst_surf, (x, y + 40))
    
    def _draw_hero_set_panel(self, surface, rect, hero_set, title, title_color):
        # Panel background
        pygame.draw.rect(surface, self.panel_color, rect)
        pygame.draw.rect(surface, self.border_color, rect, 2)
        
        # Title
        title_surf = self.header_font.render(title, True, title_color)
        surface.blit(title_surf, (rect.x + 10, rect.y + 10))
        
        # Set info
        living_count = len(hero_set.get_living_heroes())
        set_info = f"{hero_set.id} ({living_count}/5 alive)"
        info_surf = self.text_font.render(set_info, True, self.text_color)
        surface.blit(info_surf, (rect.x + 10, rect.y + 40))
        
        # Owner info
        if hero_set.is_npc:
            owner_text = f"NPC Team (Level {getattr(hero_set, 'stronghold_level', '?')})"
        else:
            owner_text = f"Player Set: {hero_set.owner_id}"
        owner_surf = self.small_font.render(owner_text, True, self.neutral_color)
        surface.blit(owner_surf, (rect.x + 10, rect.y + 65))
        
        # Heroes
        y_offset = 90
        for i, hero in enumerate(hero_set.heroes):
            hero_y = rect.y + y_offset + (i * 35)
            if hero_y + 30 > rect.bottom - 10:
                break  # Don't overflow panel
                
            self._draw_hero_info(surface, hero, rect.x + 10, hero_y, rect.width - 20)
    
    def _draw_hero_info(self, surface, hero, x, y, width):
        # Hero name and status
        status_color = self.text_color if hero.is_alive else (100, 100, 100)
        hero_text = f"{hero.id}: ATK {hero.attack} | DEF {hero.defense}"
        text_surf = self.small_font.render(hero_text, True, status_color)
        surface.blit(text_surf, (x, y))
        
        # HP bar
        hp_bar_width = width - 20
        hp_bar_height = 12
        hp_bar_y = y + 18
        
        # Background
        hp_bg_rect = pygame.Rect(x, hp_bar_y, hp_bar_width, hp_bar_height)
        pygame.draw.rect(surface, self.hp_bar_bg, hp_bg_rect)
        
        if hero.is_alive and hero.max_hp > 0:
            # HP fill
            hp_percent = hero.current_hp / hero.max_hp
            hp_fill_width = int(hp_bar_width * hp_percent)
            
            # Color based on HP percentage
            if hp_percent > 0.6:
                hp_color = self.hp_bar_full
            elif hp_percent > 0.3:
                hp_color = self.hp_bar_damaged
            else:
                hp_color = self.hp_bar_critical
            
            if hp_fill_width > 0:
                hp_fill_rect = pygame.Rect(x, hp_bar_y, hp_fill_width, hp_bar_height)
                pygame.draw.rect(surface, hp_color, hp_fill_rect)
        
        # HP text
        hp_text = f"{hero.current_hp:.0f}/{hero.max_hp}"
        hp_surf = self.small_font.render(hp_text, True, status_color)
        surface.blit(hp_surf, (x + hp_bar_width + 5, hp_bar_y - 2))
    
    def _draw_battle_log(self, surface, battle_instance, x, y, width):
        # Log header
        log_title = self.header_font.render("Battle Log", True, self.text_color)
        surface.blit(log_title, (x, y))
        
        # Log background
        log_height = surface.get_height() - y - 60
        log_rect = pygame.Rect(x, y + 30, width, log_height)
        pygame.draw.rect(surface, self.panel_color, log_rect)
        pygame.draw.rect(surface, self.border_color, log_rect, 1)
        
        # Recent log entries
        recent_entries = battle_instance.get_recent_log_entries(15)
        
        entry_y = y + 40
        line_height = 20
        
        for entry in recent_entries[-15:]:  # Show last 15 entries
            if entry_y + line_height > log_rect.bottom - 10:
                break
                
            # Truncate long entries
            if len(entry) > 80:
                entry = entry[:77] + "..."
                
            entry_surf = self.small_font.render(entry, True, self.text_color)
            surface.blit(entry_surf, (x + 5, entry_y))
            entry_y += line_height
    
    def _draw_text(self, surface, text, font, color, x, y):
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, (x, y))
        return text_surf.get_height()

    def draw_battle_list(self, surface, active_battles, selected_battle_index=0):
        """Draw a list of active battles for selection"""
        surface.fill(self.bg_color)
        
        title = "Active Battles"
        self._draw_text(surface, title, self.title_font, self.text_color, 20, 20)
        
        if not active_battles:
            no_battles_text = "No battles currently active"
            self._draw_text(surface, no_battles_text, self.header_font, self.neutral_color, 20, 80)
            return
        
        # Instructions
        instructions = "Use UP/DOWN arrows to select, ENTER to view, M for map"
        self._draw_text(surface, instructions, self.text_font, self.neutral_color, 20, 60)
        
        # Battle list
        y_offset = 100
        for i, battle in enumerate(active_battles):
            status = battle.get_battle_status()
            
            # Highlight selected battle
            bg_color = self.attacker_color if i == selected_battle_index else self.panel_color
            battle_rect = pygame.Rect(20, y_offset, surface.get_width() - 40, 60)
            pygame.draw.rect(surface, bg_color, battle_rect)
            pygame.draw.rect(surface, self.border_color, battle_rect, 1)
            
            # Battle info
            battle_text = f"{status['battle_id']} - {status['stronghold']}"
            self._draw_text(surface, battle_text, self.header_font, self.text_color, 30, y_offset + 10)
            
            progress_text = f"Step {status['step']}/{status['max_steps']} | {status['attacker_living']} vs {status['defender_living']} | {status['current_turn']} turn"
            self._draw_text(surface, progress_text, self.text_font, self.neutral_color, 30, y_offset + 35)
            
            y_offset += 70