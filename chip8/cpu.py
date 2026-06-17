class CPU:
    def __init__(self, ram):
        self.ram = ram
        
        #GENERAL REGISTERS
        self.v_registers = [0] * 16
        
        
        #---- Especial Registers ----
        
        #Index Register
        self.i = 0   #16 bits
        
        #PC Register
        self.pc = 0x200  
        
        #Stack
        self.stack = [0]* 16
        
        #Stack Pointer 
        self.stack_pointer = 0  #8 bits
        
        # --- TIMERS ----
        
        self.delay = 0
        self.sounder = 0
        
    def fetch(self):
        high_byte = self.ram.read(self.pc)
        low_byte = self.ram.read(self.pc + 1)
        instruction = (high_byte << 8) | low_byte
        return instruction        
    
    def decode(self, instruction):
        first_nibble = (instruction & 0xF000) >> 12
        x = (instruction & 0x0F00) >> 8
        y = (instruction & 0x00F0) >> 4
        n = instruction & 0x000F
        nn = instruction & 0x00FF
        nnn = instruction & 0x0FFF
        
        return first_nibble, x, y, n, nn, nnn
    

    
        
        
    