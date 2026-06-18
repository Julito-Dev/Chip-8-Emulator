import pygame

SCALE = 10
WIDTH = 64
HEIGHT = 32

class display:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE))
        pygame.display.set_caption("Chip-8")
        self.pixels = [0] * (WIDTH * HEIGHT)
        
    
    def clear(self):
        self.pixels = [0] * (WIDTH* HEIGHT)
    
    def draw(self, x, y, value):
        index = y * WIDTH + x
        collision = self.pixels[index] & value
        self.pixels[index] ^= value
        return collision == 1
    
    def render(self):
        self.screen.fill((0,0,0))
        for i, pixel in enumerate(self.pixels):
            if pixel:
                x = (i % WIDTH) * SCALE
                y = (i // HEIGHT) * SCALE
                pygame.draw.rect(self.screen, (255,255,255), x, y, SCALE, SCALE)
                
        pygame.display.flip()
                