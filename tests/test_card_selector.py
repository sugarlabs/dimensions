"""Keep the initial card selector unchanged after leaving help."""
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402

from constants import CARD_STYLES  # noqa: E402
from game import Game  # noqa: E402


class CardSelectorTest(unittest.TestCase):
    def setUp(self):
        bundle_path = str(Path(__file__).resolve().parents[1])
        environment = {'SUGAR_BUNDLE_PATH': bundle_path}
        self.bundle = patch.dict(os.environ, environment)
        self.bundle.start()
        self.canvas = Gtk.DrawingArea()
        self.game = Game(self.canvas, parent=Mock())
        self.game.word_lists = [['mouse', 'cat', 'dog'],
                                ['cheese', 'apple', 'bread'],
                                ['moon', 'sun', 'earth']]

    def tearDown(self):
        self.canvas.destroy()
        self.bundle.stop()

    def visible_choices(self):
        return [spr for spr in self.game._card_type_buttons
                if spr in self.game._sprites.list]

    def test_leaving_help_does_not_select_default_game(self):
        self.game.choose_card_type()
        before = self.visible_choices()
        self.assertTrue(self.game._first_time)
        for _ in range(3):
            self.game.choose_card_type()
            self.assertTrue(self.game._first_time)
            self.assertEqual(self.visible_choices(), before)
        self.assertEqual(
            before, self.game._card_type_buttons[:len(CARD_STYLES)])

    def test_user_choice_is_highlighted_when_returning(self):
        self.game.choose_card_type()
        choice = self.game._card_type_buttons[0]
        x, y = choice.get_xy()
        width, height = choice.get_dimensions()
        with patch('game.GLib.timeout_add'):
            self.game._button_press(x + width // 2, y + height // 2)
        self.assertFalse(self.game._first_time)
        self.game.choose_card_type()
        self.assertIn(self.game._card_type_buttons[len(CARD_STYLES)],
                      self.visible_choices())
        self.assertNotIn(choice, self.visible_choices())

    def test_programmatic_game_start_marks_selection(self):
        self.game.card_type = 'word'
        self.game._saved_state = None
        with patch.object(self.game, '_sharing', return_value=False):
            self.game._prepare_new_game()
        self.assertFalse(self.game._first_time)
        self.game.choose_card_type()
        index = CARD_STYLES.index('word')
        self.assertIn(self.game._card_type_buttons[len(CARD_STYLES) + index],
                      self.visible_choices())

    def test_editor_choices_mark_selection(self):
        self.game._edit_custom_card_action()
        self.assertFalse(self.game._first_time)
        self.game._first_time = True
        self.game.editing_word_list = True
        self.game.edit_word_list()
        self.assertFalse(self.game._first_time)

    def test_restored_selection_is_highlighted(self):
        self.game._first_time = False
        self.game.card_type = 'word'
        self.game.choose_card_type()
        index = CARD_STYLES.index('word')
        self.assertIn(self.game._card_type_buttons[len(CARD_STYLES) + index],
                      self.visible_choices())
        self.assertNotIn(self.game._card_type_buttons[index],
                         self.visible_choices())


if __name__ == '__main__':
    unittest.main()
