import pytest

from chip8.memory import memory


def test_memoria_inicia_en_cero():
    ram = memory()
    assert ram.read(0x000) == 0


def test_write_y_read():
    ram = memory()
    ram.write(0x200, 0xFF)
    assert ram.read(0x200) == 0xFF


def test_load_program():
    ram = memory()
    ram.load_program(0x000, [0xF0, 0x90, 0x90, 0x90, 0xF0])
    assert ram.dump(0x000, 0x005) == [0xF0, 0x90, 0x90, 0x90, 0xF0]


def test_fuera_de_rango():
    ram = memory()
    with pytest.raises(IndexError):
        ram.read(5000)