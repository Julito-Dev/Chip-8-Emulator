from unittest.mock import MagicMock, patch

import pytest

from chip8.cpu import CPU
from chip8.memory import memory


@pytest.fixture
def ram():
    return memory()


@pytest.fixture
def disp():
    return MagicMock()


@pytest.fixture
def kb():
    return MagicMock()


@pytest.fixture
def cpu(ram, disp, kb):
    return CPU(ram, disp, kb)


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
        cpu.pc = 0x202
        cpu.op_2NNN_call(0x300)

        cpu.pc = 0x302
        cpu.op_2NNN_call(0x400)

        assert cpu.stack_pointer == 2
        assert cpu.stack[0] == 0x202
        assert cpu.stack[1] == 0x302

        cpu.op_00EE_return()
        assert cpu.pc == 0x302
        assert cpu.stack_pointer == 1

        cpu.op_00EE_return()
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
        cpu.stack[0] = 0x202
        cpu.stack_pointer = 1

        first_nibble, x, y, n, nn, nnn = cpu.decode(0x00EE)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)

        assert cpu.pc == 0x202
        assert cpu.stack_pointer == 0

    def test_00E0_routes_correctly(self, cpu):
        first_nibble, x, y, n, nn, nnn = cpu.decode(0x00E0)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)
        cpu.display.clear.assert_called_once()

    def test_full_cycle_call_then_return(self, cpu, ram):
        ram.write(0x200, 0x23)
        ram.write(0x201, 0x00)

        instruction = cpu.fetch()
        cpu.pc += 2
        first_nibble, x, y, n, nn, nnn = cpu.decode(instruction)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)

        assert cpu.pc == 0x300
        assert cpu.stack[0] == 0x202

        ram.write(0x300, 0x00)
        ram.write(0x301, 0xEE)

        instruction = cpu.fetch()
        cpu.pc += 2
        first_nibble, x, y, n, nn, nnn = cpu.decode(instruction)
        cpu.execute_instruction(first_nibble, x, y, n, nn, nnn)

        assert cpu.pc == 0x202
        assert cpu.stack_pointer == 0


class TestOp1NNN:
    def test_jumps_to_address(self, cpu):
        cpu.op_1NNN_jump(0xABC)
        assert cpu.pc == 0xABC

    def test_jumps_to_zero(self, cpu):
        cpu.op_1NNN_jump(0x000)
        assert cpu.pc == 0x000


class TestOp3XNN:
    def test_skip_when_equal(self, cpu):
        cpu.v_registers[5] = 0x42
        pc_before = cpu.pc
        cpu.op_3XNN_cond_jump(5, 0x42)
        assert cpu.pc == pc_before + 2

    def test_no_skip_when_different(self, cpu):
        cpu.v_registers[5] = 0x42
        pc_before = cpu.pc
        cpu.op_3XNN_cond_jump(5, 0x43)
        assert cpu.pc == pc_before


class TestOp4XNN:
    def test_skip_when_not_equal(self, cpu):
        cpu.v_registers[3] = 0x10
        pc_before = cpu.pc
        cpu.op_4XNN_cond_jump(3, 0x20)
        assert cpu.pc == pc_before + 2

    def test_no_skip_when_equal(self, cpu):
        cpu.v_registers[3] = 0x10
        pc_before = cpu.pc
        cpu.op_4XNN_cond_jump(3, 0x10)
        assert cpu.pc == pc_before


class TestOp5XNN:
    def test_skip_when_equal(self, cpu):
        cpu.v_registers[2] = 0x55
        cpu.v_registers[3] = 0x55
        pc_before = cpu.pc
        cpu.op_5XNN_cond_jump(2, 3)
        assert cpu.pc == pc_before + 2

    def test_no_skip_when_different(self, cpu):
        cpu.v_registers[2] = 0x55
        cpu.v_registers[3] = 0xAA
        pc_before = cpu.pc
        cpu.op_5XNN_cond_jump(2, 3)
        assert cpu.pc == pc_before


class TestOp6XNN:
    def test_sets_register(self, cpu):
        cpu.op_6XNN_set(7, 0xAB)
        assert cpu.v_registers[7] == 0xAB

    def test_overwrites_previous_value(self, cpu):
        cpu.v_registers[7] = 0xFF
        cpu.op_6XNN_set(7, 0x12)
        assert cpu.v_registers[7] == 0x12

    def test_sets_value_zero(self, cpu):
        cpu.op_6XNN_set(0, 0x00)
        assert cpu.v_registers[0] == 0x00


class TestOp7XNN:
    def test_adds_to_register(self, cpu):
        cpu.v_registers[4] = 0x10
        cpu.op_7XNN_setsum(4, 0x20)
        assert cpu.v_registers[4] == 0x30

    def test_no_carry_flag(self, cpu):
        cpu.v_registers[4] = 0xFF
        cpu.op_7XNN_setsum(4, 0x01)
        assert cpu.v_registers[4] == 0x00

    def test_wraps_at_0xFF(self, cpu):
        cpu.v_registers[4] = 0xFE
        cpu.op_7XNN_setsum(4, 0x05)
        assert cpu.v_registers[4] == 0x03


class TestOp9XNN:
    def test_skip_when_not_equal(self, cpu):
        cpu.v_registers[0] = 0x10
        cpu.v_registers[1] = 0x20
        pc_before = cpu.pc
        cpu.op_9XNN_cond_jump(0, 1)
        assert cpu.pc == pc_before + 2

    def test_no_skip_when_equal(self, cpu):
        cpu.v_registers[0] = 0x10
        cpu.v_registers[1] = 0x10
        pc_before = cpu.pc
        cpu.op_9XNN_cond_jump(0, 1)
        assert cpu.pc == pc_before


class TestOpANNN:
    def test_sets_index_register(self, cpu):
        cpu.op_ANNN(0xABC)
        assert cpu.i == 0xABC

    def test_sets_index_to_zero(self, cpu):
        cpu.i = 0xABC
        cpu.op_ANNN(0x000)
        assert cpu.i == 0x000


class TestOpBNNN:
    def test_jumps_to_v0_plus_nnn(self, cpu):
        cpu.v_registers[0] = 0x10
        cpu.op_BNNN(0x300)
        assert cpu.pc == 0x310

    def test_jumps_with_zero_v0(self, cpu):
        cpu.v_registers[0] = 0x00
        cpu.op_BNNN(0x200)
        assert cpu.pc == 0x200


class TestOpCXNN:
    def test_result_masked_by_nn(self, cpu):
        with patch("chip8.cpu.random.randint", return_value=0xFF):
            cpu.op_CXNN(2, 0x80)
        assert cpu.v_registers[2] & 0x80 == cpu.v_registers[2]
        assert cpu.v_registers[2] <= 0x80

    def test_result_when_nn_is_zero(self, cpu):
        cpu.op_CXNN(3, 0x00)
        assert cpu.v_registers[3] == 0x00


class TestOpDXYN:
    def test_draw_calls_display_draw(self, cpu, disp):
        cpu.v_registers[0] = 10
        cpu.v_registers[1] = 5
        for i in range(2):
            cpu.ram.write(cpu.i + i, 0xFF)
        cpu.op_DXYN(0, 1, 2)
        assert disp.draw.call_count == 16

    def test_draw_sets_vf_on_collision(self, cpu, disp):
        cpu.v_registers[0] = 0
        cpu.v_registers[1] = 0
        cpu.ram.write(cpu.i, 0x80)
        disp.draw.return_value = True
        cpu.op_DXYN(0, 1, 1)
        assert cpu.v_registers[0xF] == 1

    def test_draw_clears_vf_on_no_collision(self, cpu, disp):
        cpu.v_registers[0] = 0
        cpu.v_registers[1] = 0
        cpu.ram.write(cpu.i, 0x80)
        disp.draw.return_value = False
        cpu.op_DXYN(0, 1, 1)
        assert cpu.v_registers[0xF] == 0


class TestOpEx9E:
    def test_skip_when_key_pressed(self, cpu, kb):
        cpu.v_registers[3] = 0xA
        kb.is_pressed.return_value = True
        pc_before = cpu.pc
        cpu.op_Ex9E(3)
        assert cpu.pc == pc_before + 2

    def test_no_skip_when_key_not_pressed(self, cpu, kb):
        cpu.v_registers[3] = 0xA
        kb.is_pressed.return_value = False
        pc_before = cpu.pc
        cpu.op_Ex9E(3)
        assert cpu.pc == pc_before

    def test_checks_correct_key(self, cpu, kb):
        cpu.v_registers[3] = 0xA
        cpu.op_Ex9E(3)
        kb.is_pressed.assert_called_with(0xA)


class TestOpExA1:
    def test_skip_when_key_not_pressed(self, cpu, kb):
        cpu.v_registers[3] = 0xA
        kb.is_pressed.return_value = False
        pc_before = cpu.pc
        cpu.op_ExA1(3)
        assert cpu.pc == pc_before + 2

    def test_no_skip_when_key_pressed(self, cpu, kb):
        cpu.v_registers[3] = 0xA
        kb.is_pressed.return_value = True
        pc_before = cpu.pc
        cpu.op_ExA1(3)
        assert cpu.pc == pc_before

    def test_checks_correct_key(self, cpu, kb):
        cpu.v_registers[3] = 0xA
        cpu.op_ExA1(3)
        kb.is_pressed.assert_called_with(0xA)


class TestOpFX07:
    def test_loads_delay_into_register(self, cpu):
        cpu.delay = 0x2F
        cpu.op_FX07(4)
        assert cpu.v_registers[4] == 0x2F

    def test_loads_zero_when_delay_is_zero(self, cpu):
        cpu.delay = 0
        cpu.op_FX07(5)
        assert cpu.v_registers[5] == 0


class TestOpFX0A:
    def test_stores_key_in_register(self, cpu, kb):
        kb.wait_for_key.return_value = 0x7
        cpu.op_FX0A(2)
        assert cpu.v_registers[2] == 0x7

    def test_blocks_if_key_is_none(self, cpu, kb):
        kb.wait_for_key.return_value = None
        cpu.op_FX0A(2)
        assert cpu.v_registers[2] == 0


class TestOpFX15:
    def test_sets_delay_from_register(self, cpu):
        cpu.v_registers[6] = 0x3B
        cpu.op_FX15(6)
        assert cpu.delay == 0x3B

    def test_sets_delay_to_zero(self, cpu):
        cpu.v_registers[6] = 0x00
        cpu.op_FX15(6)
        assert cpu.delay == 0


class TestOpFX18:
    def test_sets_sound_from_register(self, cpu):
        cpu.v_registers[7] = 0x1A
        cpu.op_FX18(7)
        assert cpu.sounder == 0x1A

    def test_sets_sound_to_zero(self, cpu):
        cpu.v_registers[7] = 0x00
        cpu.op_FX18(7)
        assert cpu.sounder == 0


class TestOpFX1E:
    def test_adds_vx_to_i(self, cpu):
        cpu.v_registers[2] = 0x100
        cpu.i = 0x200
        cpu.op_FX1E(2)
        assert cpu.i == 0x300

    def test_wraps_at_16_bits(self, cpu):
        cpu.i = 0xFFFF
        cpu.v_registers[3] = 0x0001
        cpu.op_FX1E(3)
        assert cpu.i == 0x0000


class TestOpFX29:
    def test_sets_i_to_vx_times_5(self, cpu):
        cpu.v_registers[4] = 0x0A
        cpu.op_FX29(4)
        assert cpu.i == 0x0A * 5

    def test_sets_i_to_zero_when_vx_is_zero(self, cpu):
        cpu.v_registers[4] = 0x00
        cpu.op_FX29(4)
        assert cpu.i == 0


class TestOpFX33:
    def test_stores_bcd_hundreds(self, cpu, ram):
        cpu.i = 0x300
        cpu.v_registers[2] = 123
        cpu.op_FX33(2)
        assert ram.read(0x300) == 1
        assert ram.read(0x301) == 2
        assert ram.read(0x302) == 3

    def test_stores_bcd_zero(self, cpu, ram):
        cpu.i = 0x300
        cpu.v_registers[2] = 0
        cpu.op_FX33(2)
        assert ram.read(0x300) == 0
        assert ram.read(0x301) == 0
        assert ram.read(0x302) == 0

    def test_stores_bcd_255(self, cpu, ram):
        cpu.i = 0x300
        cpu.v_registers[2] = 255
        cpu.op_FX33(2)
        assert ram.read(0x300) == 2
        assert ram.read(0x301) == 5
        assert ram.read(0x302) == 5

    def test_stores_bcd_5(self, cpu, ram):
        cpu.i = 0x300
        cpu.v_registers[2] = 5
        cpu.op_FX33(2)
        assert ram.read(0x300) == 0
        assert ram.read(0x301) == 0
        assert ram.read(0x302) == 5


class TestOpFX55:
    def test_stores_registers_up_to_x(self, cpu, ram):
        cpu.i = 0x400
        for i in range(8):
            cpu.v_registers[i] = i * 10
        cpu.op_FX55(7)
        for i in range(8):
            assert ram.read(0x400 + i) == i * 10

    def test_does_not_write_beyond_x(self, cpu, ram):
        cpu.i = 0x400
        for i in range(16):
            cpu.v_registers[i] = 0xFF
        cpu.op_FX55(3)
        assert ram.read(0x404) == 0


class TestOpFX65:
    def test_loads_registers_from_memory(self, cpu, ram):
        cpu.i = 0x500
        for i in range(6):
            ram.write(0x500 + i, i + 10)
        cpu.op_FX65(5)
        for i in range(6):
            assert cpu.v_registers[i] == i + 10

    def test_does_not_load_beyond_x(self, cpu, ram):
        cpu.i = 0x500
        for i in range(16):
            ram.write(0x500 + i, 0xFF)
        cpu.v_registers[5] = 0x00
        cpu.op_FX65(4)
        assert cpu.v_registers[5] == 0


class TestOp8XY0:
    def test_copies_vy_to_vx(self, cpu):
        cpu.v_registers[1] = 0x42
        cpu.op_8XY0(0, 1)
        assert cpu.v_registers[0] == 0x42

    def test_original_vy_unchanged(self, cpu):
        cpu.v_registers[1] = 0x42
        cpu.op_8XY0(0, 1)
        assert cpu.v_registers[1] == 0x42


class TestOp8XY1:
    def test_or_operation(self, cpu):
        cpu.v_registers[0] = 0xF0
        cpu.v_registers[1] = 0x0F
        cpu.op_8XY1(0, 1)
        assert cpu.v_registers[0] == 0xFF

    def test_or_with_zero(self, cpu):
        cpu.v_registers[0] = 0xAA
        cpu.v_registers[1] = 0x00
        cpu.op_8XY1(0, 1)
        assert cpu.v_registers[0] == 0xAA


class TestOp8XY2:
    def test_and_operation(self, cpu):
        cpu.v_registers[0] = 0xF0
        cpu.v_registers[1] = 0xAA
        cpu.op_8XY2(0, 1)
        assert cpu.v_registers[0] == 0xA0

    def test_and_with_zero(self, cpu):
        cpu.v_registers[0] = 0xFF
        cpu.v_registers[1] = 0x00
        cpu.op_8XY2(0, 1)
        assert cpu.v_registers[0] == 0x00


class TestOp8XY3:
    def test_xor_operation(self, cpu):
        cpu.v_registers[0] = 0xF0
        cpu.v_registers[1] = 0x0F
        cpu.op_8XY3(0, 1)
        assert cpu.v_registers[0] == 0xFF

    def test_xor_self_is_zero(self, cpu):
        cpu.v_registers[0] = 0xAA
        cpu.v_registers[1] = 0xAA
        cpu.op_8XY3(0, 1)
        assert cpu.v_registers[0] == 0x00


class TestOp8XY4:
    def test_add_no_carry(self, cpu):
        cpu.v_registers[2] = 0x10
        cpu.v_registers[3] = 0x20
        cpu.op_8XY4(2, 3)
        assert cpu.v_registers[2] == 0x30
        assert cpu.v_registers[0xF] == 0

    def test_add_with_carry(self, cpu):
        cpu.v_registers[2] = 0xFF
        cpu.v_registers[3] = 0x01
        cpu.op_8XY4(2, 3)
        assert cpu.v_registers[2] == 0x00
        assert cpu.v_registers[0xF] == 1

    def test_add_edge_carry(self, cpu):
        cpu.v_registers[2] = 0xFE
        cpu.v_registers[3] = 0x02
        cpu.op_8XY4(2, 3)
        assert cpu.v_registers[2] == 0x00
        assert cpu.v_registers[0xF] == 1


class TestOp8XY5:
    def test_sub_no_borrow(self, cpu):
        cpu.v_registers[2] = 0x30
        cpu.v_registers[3] = 0x10
        cpu.op_8XY5(2, 3)
        assert cpu.v_registers[2] == 0x20
        assert cpu.v_registers[0xF] == 1

    def test_sub_with_borrow(self, cpu):
        cpu.v_registers[2] = 0x10
        cpu.v_registers[3] = 0x20
        cpu.op_8XY5(2, 3)
        assert cpu.v_registers[2] == 0xF0
        assert cpu.v_registers[0xF] == 0

    def test_sub_equal(self, cpu):
        cpu.v_registers[2] = 0x50
        cpu.v_registers[3] = 0x50
        cpu.op_8XY5(2, 3)
        assert cpu.v_registers[2] == 0x00
        assert cpu.v_registers[0xF] == 1


class TestOp8XY6:
    def test_shifts_right_and_sets_lsb_flag(self, cpu):
        cpu.v_registers[1] = 0x03
        cpu.op_8XY6(0, 1)
        assert cpu.v_registers[0] == 0x01
        assert cpu.v_registers[0xF] == 1

    def test_shifts_right_lsb_zero(self, cpu):
        cpu.v_registers[1] = 0x02
        cpu.op_8XY6(0, 1)
        assert cpu.v_registers[0] == 0x01
        assert cpu.v_registers[0xF] == 0

    def test_shifts_zero(self, cpu):
        cpu.v_registers[1] = 0x00
        cpu.op_8XY6(0, 1)
        assert cpu.v_registers[0] == 0x00
        assert cpu.v_registers[0xF] == 0


class TestOp8XY7:
    def test_sub_vy_minus_vx_no_borrow(self, cpu):
        cpu.v_registers[2] = 0x10
        cpu.v_registers[3] = 0x30
        cpu.op_8XY7(2, 3)
        assert cpu.v_registers[2] == 0x20
        assert cpu.v_registers[0xF] == 1

    def test_sub_vy_minus_vx_with_borrow(self, cpu):
        cpu.v_registers[2] = 0x30
        cpu.v_registers[3] = 0x10
        cpu.op_8XY7(2, 3)
        assert cpu.v_registers[2] == 0xE0
        assert cpu.v_registers[0xF] == 0

    def test_sub_vy_minus_vx_equal(self, cpu):
        cpu.v_registers[2] = 0x50
        cpu.v_registers[3] = 0x50
        cpu.op_8XY7(2, 3)
        assert cpu.v_registers[2] == 0x00
        assert cpu.v_registers[0xF] == 1


class TestOp8XYE:
    def test_shifts_left_and_sets_msb_flag(self, cpu):
        cpu.v_registers[1] = 0x80
        cpu.op_8XYE(0, 1)
        assert cpu.v_registers[0] == 0x00
        assert cpu.v_registers[0xF] == 1

    def test_shifts_left_msb_zero(self, cpu):
        cpu.v_registers[1] = 0x40
        cpu.op_8XYE(0, 1)
        assert cpu.v_registers[0] == 0x80
        assert cpu.v_registers[0xF] == 0

    def test_shifts_left_zero(self, cpu):
        cpu.v_registers[1] = 0x00
        cpu.op_8XYE(0, 1)
        assert cpu.v_registers[0] == 0x00
        assert cpu.v_registers[0xF] == 0
