from unittest.mock import MagicMock, patch

import pygame
import pytest

from chip8.keyboard import KEYMAP, keyboard


@pytest.fixture
def kb():
    return keyboard()


class TestIsPressed:
    def test_returns_false_for_invalid_key(self, kb):
        with patch("chip8.keyboard.pygame.key.get_pressed", return_value=[]):
            assert kb.is_pressed(0xFF) is False

    @pytest.mark.parametrize("chip_key, pygame_key", list(KEYMAP.items()))
    def test_returns_true_when_pressed(self, kb, chip_key, pygame_key):
        keys = [0] * 512
        keys[pygame_key] = 1
        with patch("chip8.keyboard.pygame.key.get_pressed", return_value=keys):
            assert kb.is_pressed(chip_key) is True

    @pytest.mark.parametrize("chip_key, pygame_key", list(KEYMAP.items()))
    def test_returns_false_when_not_pressed(self, kb, chip_key, pygame_key):
        keys = [0] * 512
        with patch("chip8.keyboard.pygame.key.get_pressed", return_value=keys):
            assert kb.is_pressed(chip_key) is False

    def test_mapping_contains_all_16_entries(self):
        assert len(KEYMAP) == 16

    def test_all_chip8_keys_are_mapped(self):
        for i in range(16):
            assert i in KEYMAP


class TestWaitForKey:
    def test_returns_none_on_quit(self, kb):
        quit_event = MagicMock()
        quit_event.type = pygame.QUIT
        with (
            patch("chip8.keyboard.pygame.event.get", return_value=[quit_event]),
            patch("chip8.keyboard.pygame.quit"),
            patch("chip8.keyboard.pygame.time.delay"),
        ):
            result = kb.wait_for_key()
            assert result is None

    def test_returns_correct_key_on_keydown(self, kb):
        key_event = MagicMock()
        key_event.type = pygame.KEYDOWN
        key_event.key = KEYMAP[0xA]
        with (
            patch("chip8.keyboard.pygame.event.get", side_effect=[[], [key_event]]),
            patch("chip8.keyboard.pygame.time.delay"),
        ):
            assert kb.wait_for_key() == 0xA
