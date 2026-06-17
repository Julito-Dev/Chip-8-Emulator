import pytest
from chip8.cpu import CPU
from chip8.memory import memory


@pytest.fixture
def ram():
    return memory()


@pytest.fixture
def cpu(ram):
    return CPU(ram)


class TestCPUInit:
    def test_registers_initialized_to_zero(self, cpu):
        assert cpu.v_registers == [0] * 16

    def test_index_register_is_zero(self, cpu):
        assert cpu.i == 0

    def test_program_counter_starts_at_0x200(self, cpu):
        assert cpu.pc == 0x200

    def test_stack_is_all_zeros(self, cpu):
        assert cpu.stack == [0] * 16

    def test_stack_pointer_is_zero(self, cpu):
        assert cpu.stack_pointer == 0

    def test_delay_timer_is_zero(self, cpu):
        assert cpu.delay == 0

    def test_sound_timer_is_zero(self, cpu):
        assert cpu.sounder == 0


class TestFetch:
    def test_reads_two_bytes_and_combines(self, cpu, ram):
        ram.write(0x200, 0xA2)
        ram.write(0x201, 0xF0)

        instruction = cpu.fetch()
        assert instruction == 0xA2F0

    def test_fetches_from_pc_position(self, cpu, ram):
        cpu.pc = 0x300
        ram.write(0x300, 0x12)
        ram.write(0x301, 0x34)

        instruction = cpu.fetch()
        assert instruction == 0x1234

    def test_fetches_sequentially(self, cpu, ram):
        ram.write(0x200, 0xAB)
        ram.write(0x201, 0xCD)
        ram.write(0x202, 0x12)
        ram.write(0x203, 0x34)

        first = cpu.fetch()
        cpu.pc += 2
        second = cpu.fetch()

        assert first == 0xABCD
        assert second == 0x1234


class TestDecode:
    @pytest.mark.parametrize(
        "instruction, expected",
        [
            (0x8123, (0x8, 0x1, 0x2, 0x3, 0x23, 0x123)),
            (0x00E0, (0x0, 0x0, 0xE, 0x0, 0xE0, 0x0E0)),
            (0x1ABC, (0x1, 0xA, 0xB, 0xC, 0xBC, 0xABC)),
            (0x2ABC, (0x2, 0xA, 0xB, 0xC, 0xBC, 0xABC)),
            (0x6F42, (0x6, 0xF, 0x4, 0x2, 0x42, 0xF42)),
            (0xFFFF, (0xF, 0xF, 0xF, 0xF, 0xFF, 0xFFF)),
            (0x0000, (0x0, 0x0, 0x0, 0x0, 0x00, 0x000)),
        ],
    )
    def test_decode_returns_correct_fields(self, cpu, instruction, expected):
        result = cpu.decode(instruction)
        assert result == expected

    def test_decode_xyz_nibbles(self, cpu):
        result = cpu.decode(0x5AB1)
        assert result[0] == 0x5
        assert result[1] == 0xA
        assert result[2] == 0xB

    def test_decode_nn_is_low_byte(self, cpu):
        result = cpu.decode(0x4C3F)
        assert result[4] == 0x3F

    def test_decode_nnn_is_low_12_bits(self, cpu):
        result = cpu.decode(0xD234)
        assert result[5] == 0x234
    
class TestCallAndReturn:
    def test_op_2NNN_call(self, cpu):
        cpu.pc = 0x202
        cpu.op_2NNN_call(0x300)
        assert cpu.pc == 0x300
        assert cpu.stack[0] == 0x202
        assert cpu.stack_pointer == 1
 
    def test_call_y_return_juntos(self, cpu):
        cpu.pc = 0x202
        cpu.op_2NNN_call(0x300)
        cpu.op_00EE_return()
        assert cpu.pc == 0x202
        assert cpu.stack_pointer == 0
 
    def test_nested_calls(self, cpu):
        # Simula subrutinas anidadas: call A, dentro de A call B, return, return
        cpu.pc = 0x202
        cpu.op_2NNN_call(0x300)   # guarda 0x202, salta a 0x300
 
        cpu.pc = 0x302            # simula que avanzó dentro de la subrutina A
        cpu.op_2NNN_call(0x400)   # guarda 0x302, salta a 0x400
 
        assert cpu.stack_pointer == 2
        assert cpu.stack[0] == 0x202
        assert cpu.stack[1] == 0x302
 
        cpu.op_00EE_return()      # vuelve a 0x302
        assert cpu.pc == 0x302
        assert cpu.stack_pointer == 1
 
        cpu.op_00EE_return()      # vuelve a 0x202
        assert cpu.pc == 0x202
        assert cpu.stack_pointer == 0
 
 
class TestExecuteInstructionRouting:
    def test_1NNN_routes_correctly(self, cpu):
        first_nibble, x, y, n, nn, nnn = cpu.decode(0x1300)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)
        assert cpu.pc == 0x300
 
    def test_2NNN_routes_correctly(self, cpu):
        cpu.pc = 0x202
        first_nibble, x, y, n, nn, nnn = cpu.decode(0x2300)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)
        assert cpu.pc == 0x300
        assert cpu.stack[0] == 0x202
        assert cpu.stack_pointer == 1
 
    def test_00EE_routes_correctly(self, cpu):
        # Preparamos manualmente el estado como si hubiera habido un CALL antes
        cpu.stack[0] = 0x202
        cpu.stack_pointer = 1
 
        first_nibble, x, y, n, nn, nnn = cpu.decode(0x00EE)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)
 
        assert cpu.pc == 0x202
        assert cpu.stack_pointer == 0
 
    def test_00E0_routes_correctly(self, cpu, capsys):
        # Como es un placeholder con print, solo verificamos que no explota
        # y que efectivamente se llamó (capturando stdout)
        first_nibble, x, y, n, nn, nnn = cpu.decode(0x00E0)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)
 
        captured = capsys.readouterr()
        assert "Clear Screen" in captured.out
 
    def test_full_cycle_call_then_return(self, cpu, ram):
        # Simula un ciclo más realista: CALL en 0x200, luego RETURN en 0x300
        ram.write(0x200, 0x23)
        ram.write(0x201, 0x00)  # opcode 0x2300 -> CALL 0x300
 
        instruction = cpu.fetch()
        cpu.pc += 2
        first_nibble, x, y, n, nn, nnn = cpu.decode(instruction)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)
 
        assert cpu.pc == 0x300
        assert cpu.stack[0] == 0x202
 
        ram.write(0x300, 0x00)
        ram.write(0x301, 0xEE)  # opcode 0x00EE -> RETURN
 
        instruction = cpu.fetch()
        cpu.pc += 2
        first_nibble, x, y, n, nn, nnn = cpu.decode(instruction)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)
 
        assert cpu.pc == 0x202
        assert cpu.stack_pointer == 0
