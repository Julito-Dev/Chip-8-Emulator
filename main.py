import sys
from chip8.memory import memory
from chip8.cpu import CPU
from chip8.display import display
from chip8.keyboard import keyboard

FONTSET = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
]

MAX_ROM_SIZE = 0xE00  # Avaliable space: 0x200 < x < 0xFFF


def main(rom_path):
    ram = memory()
    ram.load_program(0x000, FONTSET)

    try:
        with open(rom_path, "rb") as f:
            rom = list(f.read())
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{rom_path}'")
        sys.exit(1)

    if len(rom) > MAX_ROM_SIZE:
        print(f"Error: The Rom its To big: ({len(rom)} bytes, máx: {MAX_ROM_SIZE})")
        sys.exit(1)

    ram.load_program(0x200, rom)

    screen = display()
    keys = keyboard()
    cpu = CPU(ram, screen, keys)

    running = True
    while running:
        running = screen.check_events()

        # ~500 Hz: ejecutar varios ciclos por frame
        for _ in range(10):
            instruction = cpu.fetch()
            cpu.pc += 2
            first_nibble, x, y, n, nn, nnn = cpu.decode(instruction)
            cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)

        # timers a 60 Hz (el clock del display ya hace tick a 60)
        if cpu.delay > 0:
            cpu.delay -= 1
        if cpu.sounder > 0:
            cpu.sounder -= 1

        screen.render()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("1. Create a new folder in the root of the project.")
        print("2. Download some ROMs from the web.")
        print("3. In the terminal, run: python main.py roms/rom_name.ch8")
        sys.exit(1)
    main(sys.argv[1])