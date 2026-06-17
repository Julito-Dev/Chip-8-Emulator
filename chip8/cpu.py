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
        
        
        
        
        
        
        
    