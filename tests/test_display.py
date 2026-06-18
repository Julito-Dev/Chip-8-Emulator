from unittest.mock import MagicMock, patch

import pygame
import pytest

from chip8.display import HEIGHT, WIDTH, display


@pytest.fixture
def disp():
    with (
        patch("chip8.display.pygame.init"),
        patch("chip8.display.pygame.display.set_mode"),
        patch("chip8.display.pygame.display.set_caption"),
        patch("chip8.display.pygame.time.Clock"),
    ):
        d = display()
    return d


class TestDisplayInit:
    def test_pixels_initialized_to_zero(self, disp):
        assert disp.pixels == [0] * (WIDTH * HEIGHT)

    def test_pixels_length(self, disp):
        assert len(disp.pixels) == WIDTH * HEIGHT


class TestClear:
    def test_resets_all_pixels_to_zero(self, disp):
        disp.pixels[100] = 1
        disp.pixels[500] = 1
        disp.clear()
        assert all(p == 0 for p in disp.pixels)

    def test_after_clear_length_stays_same(self, disp):
        disp.clear()
        assert len(disp.pixels) == WIDTH * HEIGHT


class TestGetPixel:
    def test_returns_zero_for_empty_pixel(self, disp):
        assert disp.get_pixel(10, 5) == 0

    def test_returns_one_for_set_pixel(self, disp):
        disp.pixels[5 * WIDTH + 10] = 1
        assert disp.get_pixel(10, 5) == 1

    def test_returns_zero_when_x_out_of_bounds(self, disp):
        assert disp.get_pixel(WIDTH, 0) == 0
        assert disp.get_pixel(-1, 0) == 0

    def test_returns_zero_when_y_out_of_bounds(self, disp):
        assert disp.get_pixel(0, HEIGHT) == 0
        assert disp.get_pixel(0, -1) == 0

    def test_returns_value_at_correct_position(self, disp):
        disp.pixels[0] = 1
        assert disp.get_pixel(0, 0) == 1
        disp.pixels[WIDTH - 1] = 1
        assert disp.get_pixel(WIDTH - 1, 0) == 1


class TestSetPixel:
    def test_sets_pixel_to_one(self, disp):
        disp.set_pixel(10, 5, 1)
        assert disp.pixels[5 * WIDTH + 10] == 1

    def test_sets_pixel_to_zero(self, disp):
        disp.pixels[5 * WIDTH + 10] = 1
        disp.set_pixel(10, 5, 0)
        assert disp.pixels[5 * WIDTH + 10] == 0

    def test_does_nothing_when_x_out_of_bounds(self, disp):
        disp.set_pixel(WIDTH, 0, 1)
        assert all(p == 0 for p in disp.pixels)

    def test_does_nothing_when_y_out_of_bounds(self, disp):
        disp.set_pixel(0, HEIGHT, 1)
        assert all(p == 0 for p in disp.pixels)


class TestTogglePixel:
    def test_toggles_zero_to_one(self, disp):
        result = disp.toggle_pixel(10, 5)
        assert disp.pixels[5 * WIDTH + 10] == 1
        assert result is False

    def test_toggles_one_to_zero(self, disp):
        disp.pixels[5 * WIDTH + 10] = 1
        result = disp.toggle_pixel(10, 5)
        assert disp.pixels[5 * WIDTH + 10] == 0
        assert result is True

    def test_double_toggle_restores_original(self, disp):
        disp.toggle_pixel(10, 5)
        disp.toggle_pixel(10, 5)
        assert disp.pixels[5 * WIDTH + 10] == 0

    def test_returns_false_when_out_of_bounds(self, disp):
        assert disp.toggle_pixel(WIDTH, 0) is False
        assert disp.toggle_pixel(-1, 0) is False
        assert disp.toggle_pixel(0, HEIGHT) is False

    def test_collision_true_when_pixel_was_one(self, disp):
        disp.pixels[5 * WIDTH + 10] = 1
        assert disp.toggle_pixel(10, 5) is True

    def test_collision_false_when_pixel_was_zero(self, disp):
        assert disp.toggle_pixel(10, 5) is False


class TestDraw:
    def test_xor_writes_value(self, disp):
        disp.draw(10, 5, 1)
        assert disp.pixels[5 * WIDTH + 10] == 1

    def test_xor_toggles_back_to_zero(self, disp):
        disp.pixels[5 * WIDTH + 10] = 1
        disp.draw(10, 5, 1)
        assert disp.pixels[5 * WIDTH + 10] == 0

    def test_xor_with_value_greater_than_one(self, disp):
        disp.pixels[5 * WIDTH + 10] = 0b0011
        disp.draw(10, 5, 0b0101)
        assert disp.pixels[5 * WIDTH + 10] == 0b0110

    def test_collision_true_when_both_set(self, disp):
        disp.pixels[5 * WIDTH + 10] = 1
        collision = disp.draw(10, 5, 1)
        assert collision is True

    def test_collision_false_when_pixel_was_zero(self, disp):
        collision = disp.draw(10, 5, 1)
        assert collision is False

    def test_collision_with_multi_bit_value(self, disp):
        disp.pixels[5 * WIDTH + 10] = 0b0001
        collision = disp.draw(10, 5, 0b0001)
        assert collision is True

    def test_collision_multi_bit_no_overlap(self, disp):
        disp.pixels[5 * WIDTH + 10] = 0b0010
        collision = disp.draw(10, 5, 0b0001)
        assert collision is False


class TestCheckEvents:
    def test_returns_true_when_no_quit(self, disp):
        with patch("chip8.display.pygame.event.get", return_value=[]):
            assert disp.check_events() is True

    def test_returns_false_on_quit_event(self, disp):
        quit_event = MagicMock()
        quit_event.type = pygame.QUIT
        with (
            patch("chip8.display.pygame.event.get", return_value=[quit_event]),
            patch("chip8.display.pygame.quit"),
        ):
            assert disp.check_events() is False
