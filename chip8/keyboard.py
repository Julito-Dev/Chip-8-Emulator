import pygame

KEYMAP = {
    0x0: pygame.K_x,
    0x1: pygame.K_1,
    0x2: pygame.K_2,
    0x3: pygame.K_3,
    0x4: pygame.K_q,
    0x5: pygame.K_w,
    0x6: pygame.K_e,
    0x7: pygame.K_a,
    0x8: pygame.K_s,
    0x9: pygame.K_d,
    0xA: pygame.K_z,
    0xB: pygame.K_c,
    0xC: pygame.K_4,
    0xD: pygame.K_r,
    0xE: pygame.K_f,
    0xF: pygame.K_v
}

class keyboard:
    def __init__(self):
        self.current_key = None
        
    def is_pressed(self, key):
        keys = pygame.key.get_pressed()
        if key in KEYMAP:
            return keys[KEYMAP[key]] ==1
        return False
    
    def wait_for_key(self):
        """Blocks the CPU until a keys is pushed
        """
        waiting =True
        self.current_key = None
        
        while self.wait_for_key:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None

                if event.type == pygame.KEYDOWN:
                    for chip_key, pygame_key in KEYMAP.items():
                        if event.key == pygame_key:
                            self.current_key = chip_key
                            waiting = False
                            return chip_key
            pygame.time.delay(10)
        
        return self.current_key
    