class memory:
    def __init__(self):
        self.data = [0] * 4096
        
    
    def read(self, address):
        if  0 <= address < len(self.data):
            return self.data[address]
        else:
            raise IndexError(f"Address Memory out of index: {address}")

    
    def write(self, address, data):
        if 0<= address < len(self.data):
            self.data[address] = data
        else:
            raise IndexError(f"Address Memory out of index: {address}")
    
    
    def load_program(self, address, programBytes):
        """Loads every byte in a real program
        """
        for i, byte in enumerate(programBytes):
            self.data[address + i] = byte
            
        
    def dump(self, start, end):
        return self.data[start:end]
    
    
            
            