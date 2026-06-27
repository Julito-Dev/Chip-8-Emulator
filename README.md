# Chip 8 Emulator

A CHIP-8 emulator written in Python from scratch, with no emulation frameworks. It implements the full virtual machine: memory, a CPU with all 34 instructions of the standard set, a 64x32 display, and a hexadecimal keyboard, using Pygame only for rendering.

## What is CHIP-8?

CHIP-8 is a virtual machine from the 1970s, originally designed to run simple games on microcomputers of that era. It isn't real hardware: it's an instruction specification that any interpreter can implement, which is why it's one of the classic projects for learning how an emulator works under the hood.

## Features

- Full CPU implementing all 34 instructions of the standard CHIP-8 set
- 4096-byte memory with fontset and ROM loading
- 64x32 pixel display rendered with Pygame, with configurable scaling
- Hexadecimal keyboard (16 keys) mapped to a modern keyboard
- Delay and sound timer support running at 60Hz
- Modular architecture: each component (RAM, CPU, Display, Keyboard) is an independent, individually testable class

## Project structure

```
chip8-emulator/
├── chip8/
│   ├── __init__.py
│   ├── memory.py      # 4096-byte RAM
│   ├── cpu.py          # Registers, fetch-decode-execute, all 34 instructions
│   ├── display.py      # Pixel buffer and Pygame rendering
│   └── keyboard.py     # Hexadecimal keyboard mapping and input
├── tests/
│   └── ...              # Pytest tests for each component
├── roms/
│   └── ...              # .ch8 ROM files (not included, see note below)
├── main.py              # Emulator entry point
└── README.md
```

## Installation

Requires Python 3.10 or higher.

1. Clone the repository:
```bash
git clone https://github.com/Julito-Dev/Chip-8-Emulator.git
cd Chip-8-Emulator
```

2. Install dependencies:
```bash
pip install pygame
```

## Running a ROM

The emulator takes the path to a `.ch8` file as an argument, for example:

```bash
python main.py roms/IBM_Logo.ch8
```

Tested examples:

```bash
python main.py roms/IBM_Logo.ch8
python main.py roms/Pong.ch8
```

Note: ROMs must be downloaded separately from the internet. This repository does not include any ROM files.

If no ROM is specified, the program prints usage instructions and exits:

```bash
python main.py
```

## Controls

The original CHIP-8 used a 16-key hexadecimal keypad, laid out as follows:

```
CHIP-8 Keypad          Physical Keyboard
1  2  3  C             1  2  3  4
4  5  6  D             Q  W  E  R
7  8  9  E             A  S  D  F
A  0  B  F             Z  X  C  V
```

Each game uses a different subset of these keys for its own controls (for example, Pong typically uses `1`/`Q` and `4`/`R` to move the paddles).

## Internal architecture

The emulator follows the classic cycle of any CPU:

1. **Fetch**: reads 2 bytes from memory at the Program Counter's position and combines them into a 16-bit instruction.
2. **Decode**: breaks the instruction down into its components (nibble, X/Y registers, N/NN/NNN values) using bitwise operations.
3. **Execute**: applies the effect of the decoded instruction, whether that's modifying registers, jumping the PC, drawing to the screen, or interacting with the keyboard.

Each instruction is implemented as an independent method within `CPU`, grouped by family according to its first nibble (0x0 to 0xF), which makes each one easier to test and debug in isolation.

## Tests

The project includes a pytest suite covering CPU initialization, fetch, decode, and every implemented instruction.

```bash
pip install pytest
pytest
```

## Project status

All 34 instructions of the standard CHIP-8 set are implemented, including arithmetic with correct 8-bit overflow/underflow handling, sprite drawing with collision detection, and the keyboard-dependent instructions (`EX9E`, `EXA1`, `FX0A`).

Possible future improvements:
- Fine-tune timing to reduce flickering in certain games
- Real sound output for the `sound_timer`
- Validation against Timendus's CHIP-8 Test Suite

## References used

- [Cowgod's CHIP-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)
- [Guide to making a CHIP-8 emulator - Tobias V. Langhoff](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/)