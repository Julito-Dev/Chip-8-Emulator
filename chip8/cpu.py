import random

class CPU:
    def __init__(self, ram, display):
        self.ram = ram
        self.display = display
        
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
            
        elif first_nibble == 0x3:
            self.op_3XNN_cond_jump(x, nn)
            
        elif first_nibble == 0x4:
            self.op_4XNN_cond_jump(x, nn)
        
        elif first_nibble == 0x5:
            self.op_5XNN_cond_jump(x, y)
        
        elif first_nibble == 0x6:
            self.op_6XNN_set(x, nn)
        
        elif first_nibble == 0x7:
            self.op_7XNN_setsum(x, nn)
        
        elif first_nibble == 0x8:
            self.op_8XYN(x, y, n)
                    
        elif first_nibble == 0x9:
            self.op_9XNN_cond_jump(x, y)
        
        elif first_nibble == 0xA:
            self.op_ANNN(nnn)
        
        elif first_nibble == 0xB:
            self.op_BNNN(nnn)
            
        elif first_nibble == 0xC:
            self.op_CXNN(x, nn)
        
        elif first_nibble == 0xD:
            self.op_DXYN(x, y, n)
        
        elif first_nibble == 0xE:
            if nn == 0x9E:
                self.op_Ex9E(x)
            
            elif nn == 0xA1:
                self.op_ExA1(x)
    
        elif first_nibble == 0xF:
            if nn == 0x07:
                self.op_FX07(x)
                
            elif nn == 0x0A:
                self.op_FX0A(x)
                
            elif nn == 0x15:
                self.op_FX15(x)
                
            elif nn == 0x18:
                self.op_FX18(x)
                
            elif nn == 0x1E:
                self.op_FX1E(x)
                
            elif nn == 0x29:
                self.op_FX29(x)
                
            elif nn == 0x33:
                self.op_FX33(x)
            elif nn == 0x55:
                self.op_FX55(x)
                
            elif nn == 0x65:
                self.op_FX65(x)
                
                
        
    def op_00E0_clear_screen(self):
        self.display.clear()
        
    def op_00EE_return(self):
        self.stack_pointer -= 1
        self.pc = self.stack[self.stack_pointer]
    
    def op_1NNN_jump(self, nnn):
        self.pc = nnn   #Moves the PC to nnn
        
    def op_2NNN_call(self, nnn):
        self.stack[self.stack_pointer] = self.pc
        self.stack_pointer += 1
        self.pc = nnn
    
    def op_3XNN_cond_jump(self, x, nn):
        if self.v_registers[x] == nn:
            self.pc += 2
            
    def op_4XNN_cond_jump(self, x, nn):
        if self.v_registers[x] != nn:
            self.pc += 2
        
    def op_5XNN_cond_jump(self, x, y):
        if self.v_registers[x] == self.v_registers[y]:
            self.pc += 2
    
    def op_6XNN_set(self, x, nn):
        self.v_registers[x] = nn
    
    def op_7XNN_setsum(self, x, nn):
        self.v_registers[x] = (self.v_registers[x] + nn) & 0xFF   #Prevents overflow
    
    def op_8XYN(self, x, y, n):
        if n == 0x0:
            self.op_8XY0(x,y)
            
        elif n == 0x1:
            self.op_8XY1(x, y)
        
        elif n == 0x2:
            self.op_8XY2(x, y)
        
        elif n == 0x3:
            self.op_8XY3(x, y)
        
        elif n == 0x4:
            self.op_8XY4(x, y)
        
        elif n == 0x5:
            self.op_8XY5(x, y)
        
        elif n == 0x6:
            self.op_8XY6(x, y)
        
        elif n == 0x7:
            self.op_8XY7(x, y)
        
        elif n == 0xE:
            self.op_8XYE(x, y)
            
            
    def op_9XNN_cond_jump(self, x, y):
        if self.v_registers[x] != self.v_registers[y]:
            self.pc += 2
        
    def op_ANNN(self, nnn):
        self.i = nnn
    
    def op_BNNN(self, nnn):
        self.pc = nnn + self.v_registers[0x0]
        
    def op_CXNN(self,x, nn):
        self.v_registers[x] = random.randint(0, 255) & nn
    
    def op_DXYN(self, x, y, nibble):
        x_pos = self.v_registers[x] % 64
        y_pos = self.v_registers[y] %32
        self.v_registers[0xF] = 0
        
        for row in range(nibble):
            byte = self.ram.read(self.i +row)
            for bit in range (8):
                pixel = (byte >> ( 7 -  bit)) & 1
                if pixel:
                    px = (x_pos + bit) %64
                    py = (y_pos + row) % 32
                    collision = self.display.draw(px, py, 1)
                    if collision:
                        self.v_registers[0xF] = 1
        
        
    
    #Family of 0xE opcodes
    def op_Ex9E(self, x):
        pass

    def op_ExA1(self, x):
        pass
    
    #Family of 0xF opcodes
    
    def op_FX07(self, x):
        self.v_registers[x] = self.delay
    
    def op_FX0A(self, x):
        pass
    
    def op_FX15(self, x):
        self.delay = self.v_registers[x]
    
    def op_FX18(self, x):
        self.sounder = self.v_registers[x]
    
    def op_FX1E(self, x):
        self.i = (self.i + self.v_registers[x]) & 0xFFFF
        
    def op_FX29(self, x):
        self.i = self.v_registers[x] * 5

    def op_FX33(self, x):
        value = self.v_registers[x]
        self.ram.write(self.i, value // 100)
        self.ram.write(self.i + 1, (value//10) %  10)
        self.ram.write(self.i + 2, value % 10)
    
    def op_FX55(self, x):
        for i in range(x + 1):
            self.ram.write(self.i + i, self.v_registers[i])
            
    def op_FX65(self, x):
        for i in range(x + 1):
            self.v_registers[i] = self.ram.read(self.i + i)
    
    
    # Family of 0x8 opcodes
    
    def op_8XY0(self, x, y):
        self.v_registers[x] = self.v_registers[y]    
    
    def op_8XY1(self, x, y):
        self.v_registers[x] = self.v_registers[x] | self.v_registers[y]
    
    def op_8XY2(self, x, y):
        self.v_registers[x] = self.v_registers[x] & self.v_registers[y]
    
    def op_8XY3(self, x, y):
        self.v_registers[x] = self.v_registers[x] ^ self.v_registers[y]
    
    def op_8XY4(self, x, y):
        result = self.v_registers[x] + self.v_registers[y]
        flag = 1 if result > 0xFF else 0
        self.v_registers[x] = result & 0xFF
        self.v_registers[0xF] = flag
    
    def op_8XY5(self, x, y):
        result = self.v_registers[x] - self.v_registers[y]
        flag = 1 if self.v_registers[x] >= self.v_registers[y] else 0
        self.v_registers[x] = result & 0xFF
        self.v_registers[0xF] = flag
    
    def op_8XY6(self, x, y):
        flag =  self.v_registers[y] & 0x1
        self.v_registers[x] = self.v_registers[y] >> 1
        self.v_registers[0xF] = flag
        
    def op_8XY7(self, x, y):
        result = self.v_registers[y] - self.v_registers[x]
        flag = 1 if self.v_registers[y] >= self.v_registers[x] else 0
        self.v_registers[x] = result & 0xFF
        self.v_registers[0xF] = flag
    
    def op_8XYE(self, x, y):
        flag = (self.v_registers[y] & 0x80) >> 7
        self.v_registers[x] = (self.v_registers[y] << 1) & 0xFF
        self.v_registers[0xF] = flag
        
    