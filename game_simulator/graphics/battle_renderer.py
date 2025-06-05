# game_simulator/graphics/battle_renderer.py
import pygame
import config

class BattleRenderer:
    def __init__(self):
        self.title_font = pygame.font.SysFont(None, 36)
        self.header_font = pygame.font.SysFont(None, 28)
        self.text_font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.panel_color = (50, 50, 60)
        self.border_color = (80, 80, 90)
        self.attacker_color = (200, 100, 100)
        self.defender_color = (100, 100, 200)
        self.neutral_color = (150, 150, 150)
        self.text_color = (255, 255, 255)
        self.hp_bar_bg = (60, 60, 60)
        self.hp_bar_full = (100, 200, 100)
        self.hp_bar_damaged = (200, 150, 50)
        self.hp_bar_critical = (200, 50, 50)

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