# game_simulator/graphics/ui_elements.py
import pygame

class UIElements:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 16)
        
    def draw_time_info(self, surface, game_time, time_scale):
        time_text = self.font.render(f"Time: {game_time:.2f}s | Scale: x{time_scale:.2f}", True, (255,255,255))
        surface.blit(time_text, (10,10))
        
    def draw_scrubber(self, surface, scrubber_rect, game_time, max_game_time=None):
        # Draw scrubber background
        pygame.draw.rect(surface, (100,100,100), scrubber_rect)
        
        # Draw scrubber handle if we have a max time
        if max_game_time and max_game_time > 0:
            handle_x = scrubber_rect.x + (game_time / max_game_time) * scrubber_rect.width
            handle_rect = pygame.Rect(handle_x - 5, scrubber_rect.y - 5, 10, scrubber_rect.height + 10)
            pygame.draw.rect(surface, (200,200,200), handle_rect)
            
    def draw_battle_info(self, surface, active_battles):
        if active_battles:
            y_offset = 50
            battles_text = self.font.render(f"Active Battles: {len(active_battles)}", True, (255,255,255))
            surface.blit(battles_text, (10, y_offset))
            
    def draw_controls_help(self, surface):
        help_texts = [
            "Controls:",
            "SPACE - Pause/Resume",
            "LEFT/RIGHT - Adjust speed",
            "M - Map view",  
            "B - Cycle battles",
            "L - Battle list",
            "1-4 - Test attacks",
            "ESC - Exit"
        ]
        
        y_offset = surface.get_height() - len(help_texts) * 18 - 10
        for text in help_texts:
            text_surf = self.small_font.render(text, True, (200, 200, 200))
            surface.blit(text_surf, (10, y_offset))
            y_offset += 18