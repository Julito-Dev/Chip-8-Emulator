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
        self.clock = pygame.time.Clock()
    
    def clear(self):
        self.pixels = [0] * (WIDTH* HEIGHT)
        
    def get_pixel(self, x, y):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            return self.pixels[y * WIDTH + x]
        return 0

    def set_pixel(self, x,y, value):
        if 0<= x < WIDTH and 0 <= y < HEIGHT:
            self.pixels[y * WIDTH + x ] = value
            
    def toggle_pixel(self, x, y):
        if 0<= x < WIDTH and 0 <= y < HEIGHT:
            index = y * WIDTH + x
            collision = self.pixels[index] == 1
            self.pixels[index] ^= 1 # Toggle
            return collision
        return False
    
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
                y = (i // WIDTH) * SCALE
                pygame.draw.rect(self.screen, (255,255,255), (x, y, SCALE, SCALE))
                
        pygame.display.flip()
        self.clock.tick(60)
    
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        
        return True

    
                