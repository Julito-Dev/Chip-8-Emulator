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
    
    
    def execute_instruction(self, first_nibble, x, y, n, nn, nnn):
        
        if first_nibble == 0x0:
            if nn == 0xE0:
                self.op_00E0_clear_screen()
            elif nn == 0xEE:
                self.op_00EE_return()
                
        elif first_nibble == 0x1:
            self.op_1NNN_jump(nnn)
            
        elif first_nibble == 0x2:
            self.op_2NNN_call(nnn)
        
                
    # -----PLACEHOLDERS -----
    
    def op_00E0_clear_screen(self):
        print("Clear Screen called correctly")
        
    
    
    # -----FINALS------
    
    def op_00EE_return(self):
        self.stack_pointer -= 1
        self.pc = self.stack[self.stack_pointer]
    
    def op_1NNN_jump(self, nnn):
        self.pc = nnn   #Moves the PC to nnn
        
    def op_2NNN_call(self, nnn):
        self.stack[self.stack_pointer] = self.pc
        self.stack_pointer += 1
        self.pc = nnn
        
    
        
         
        
    

    
        
        
    