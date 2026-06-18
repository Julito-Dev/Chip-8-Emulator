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
        
    