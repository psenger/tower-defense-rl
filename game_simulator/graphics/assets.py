# game_simulator/graphics/assets.py
import pygame
import os

class AssetManager:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.assets_path = "assets"
        
    def load_image(self, filename, colorkey=None):
        """Load an image and return it"""
        fullname = os.path.join(self.assets_path, "images", filename)
        try:
            image = pygame.image.load(fullname)
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey, pygame.RLEACCEL)
            self.images[filename] = image
            return image
        except pygame.error:
            print(f"Cannot load image: {fullname}")
            # Return a placeholder surface
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta placeholder
            return placeholder
            
    def get_image(self, filename):
        """Get a previously loaded image"""
        if filename in self.images:
            return self.images[filename]
        else:
            return self.load_image(filename)
            
    def load_font(self, font_name, size):
        """Load a font and return it"""
        font_key = f"{font_name}_{size}"
        if font_key not in self.fonts:
            fullname = os.path.join(self.assets_path, "fonts", font_name)
            try:
                font = pygame.font.Font(fullname, size)
                self.fonts[font_key] = font
            except pygame.error:
                print(f"Cannot load font: {fullname}, using default")
                font = pygame.font.Font(None, size)
                self.fonts[font_key] = font
        return self.fonts[font_key]
        
    def get_font(self, font_name, size):
        """Get a previously loaded font"""
        font_key = f"{font_name}_{size}"
        if font_key in self.fonts:
            return self.fonts[font_key]
        else:
            return self.load_font(font_name, size)