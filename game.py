# -*- coding: utf-8 -*-
#Copyright (c) 2009-14 Walter Bender
#Copyright (c) 2009 Michele Pratusevich
#Copyright (c) 2009 Vincent Le

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import Pango

import os
import glob

from gettext import gettext as _

from math import sqrt

import logging
_logger = logging.getLogger('dimensions-activity')

try:
    from sugar3.graphics.style import GRID_CELL_SIZE, DEFAULT_SPACING
except:
    GRID_CELL_SIZE = 55
    DEFAULT_SPACING = 16

from constants import (HIGH, ROW, COL, CARD_WIDTH, WORD_CARD_INDICIES, LABELH,
                       WORD_CARD_MAP, CARD_HEIGHT, DEAL, DIFFICULTY_LEVEL,
                       DECKSIZE, CUSTOM_CARD_INDICIES, CARDS_IN_A_MATCH)
from grid import Grid
from deck import Deck
from card import Card
from sprites import Sprites, Sprite
from gencards import (generate_match_card, generate_frowny_shape,
                      generate_smiley, generate_frowny_texture,
                      generate_frowny_color, generate_frowny_number,
                      generate_label, generate_background)

CURSOR = '█'


def _distance(pos1, pos2):
    ''' simple distance function '''
    return sqrt((pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) +
                (pos1[1] - pos2[1]) * (pos1[1] - pos2[1]))


def _find_the_number_in_the_name(name):
    ''' Find which element in an array (journal entry title) is a number '''
    parts = name.split('.')
    before = ''
    after = ''
    for i in range(len(parts)):
        ii = len(parts) - i - 1
        try:
            int(parts[ii])
            for j in range(ii):
                before += (parts[j] + '.')
            for j in range(ii + 1, len(parts)):
                after += ('.' + parts[j])
            return before, after, ii
        except ValueError:
            pass
    return '', '', -1


def _construct_a_name(before, i, after):
    ''' Make a numbered filename from parts '''
    return '%s%s%s' % (before, str(i), after)


class Click():
    ''' A simple class to hold a clicked card '''

    def __init__(self):
        self.spr = None
        self.pos = [0, 0]

    def reset(self):
        self.spr = None
        self.pos = [0, 0]

    def hide(self):
        if self.spr is not None:
            self.spr.hide()
            self.reset()


class Game():
    ''' The game play -- called from within Sugar or GNOME '''

    def __init__(self, canvas, parent=None, card_type='pattern'):
        ''' Initialize the playing surface '''
        self.activity = parent

        if parent is None:  # Starting from command line
            self._sugar = False
            self._canvas = canvas
        else:  # Starting from Sugar
            self._sugar = True
            self._canvas = canvas
            parent.show_all()

        self._canvas.set_can_focus(True)

        self._canvas.add_events(Gdk.EventMask.TOUCH_MASK)
        self._canvas.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self._canvas.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self._canvas.add_events(Gdk.EventMask.BUTTON_MOTION_MASK)

        self._canvas.connect('event', self.__event_cb)
        self._canvas.connect('draw', self.__draw_cb)

        self._width = Gdk.Screen.width()
        self._height = Gdk.Screen.height()
        if self._width < self._height:
            self.portrait = True
            self._scale = 0.67 * self._width / (CARD_HEIGHT * 5.5)
        else:
            self.portrait = False
            self._scale = 0.67 * self._height / (CARD_HEIGHT * 5.5)

        self._card_width = CARD_WIDTH * self._scale
        self._card_height = CARD_HEIGHT * self._scale
        self.custom_paths = [None, None, None, None, None, None, None, None,
                             None]
        self._sprites = Sprites(self._canvas)
        self._sprites.set_delay(True)
        self._press = None
        self.matches = 0
        self.robot_matches = 0
        self._match_area = []
        self._matches_on_display = False
        self._smiley = []
        self._frowny = []
        self._help = []
        self._help_timeout_id = None
        self._stop_help = True
        self._failure = None
        self.clicked = []
        self.last_click = None
        self._drag_pos = [0, 0]
        self._start_pos = [0, 0]
        self.low_score = [-1, -1, -1]
        self.all_scores = []
        self.robot = False
        self.robot_time = 0
        self.total_time = 0
        self.numberC = 0
        self.numberO = 0
        self.word_lists = None
        self.editing_word_list = False
        self.editing_custom_cards = False
        self._edit_card = None
        self._dead_key = None
        self._found_a_match = False
        self.level = 0
        self.card_type = card_type
        self.buddies = []
        self._dealing = False
        self._the_game_is_over = False
        self._played_animation = False

        self.grid = Grid(self._width, self._height, self._card_width,
                         self._card_height)

        self.backgrounds = []
        if self.portrait:
            width = Gdk.Screen.height()
            height = Gdk.Screen.width()
        else:
            width = Gdk.Screen.width()
            height = Gdk.Screen.height()
        # generate landscape background
        string = generate_background(width, height)
        self.backgrounds.append(Sprite(
            self._sprites, 0, 0, svg_str_to_pixbuf(string, width, height)))
        if self.portrait:
            width = Gdk.Screen.width()
            height = Gdk.Screen.height()
        else:
            width = Gdk.Screen.height()
            height = Gdk.Screen.width()
        # generate portrait background
        string = generate_background(width, height)
        self.backgrounds.append(Sprite(
            self._sprites, 0, 0, svg_str_to_pixbuf(string, width, height)))

        if self.portrait:
            self.backgrounds[0].hide()
        else:
            self.backgrounds[1].hide()

        if self._sugar:
            self._old_cursor = self.activity.get_window().get_cursor()
            self.activity.get_window().set_cursor(Gdk.Cursor.new(
                Gdk.CursorType.WATCH))
        GObject.idle_add(self._complete_loading)

    def _complete_loading(self):
        self._cards = []
        for i in range(DECKSIZE):
            self._cards.append(Card(scale=self._scale))

        self.deck = Deck(self._cards, scale=self._scale)

        for i in range(CARDS_IN_A_MATCH):
            self.clicked.append(Click())
            self._match_area.append(Card(scale=self._scale))
            self._match_area[-1].create(
                generate_match_card(self._scale), sprites=self._sprites)
            self._match_area[-1].spr.move(self.grid.match_to_xy(i))

        for i in range(30):
            scale = self._scale * (i / 2 + 2)
            self._smiley.append(Card(scale=scale))
            self._smiley[-1].create(
                generate_smiley(scale), sprites=self._sprites)
            x = self._smiley_xy()[0] - i / 2 * int(self._card_width / 2)
            y = self._smiley_xy()[1] - i / 2 * int(self._card_height / 2)
            self._smiley[-1].spr.move((int(x), int(y)))
            if i == 0:
                self._smiley[-1].spr.set_layer(10000)
            else:
                self._smiley[-1].spr.set_layer(20000)
            self._smiley[-1].spr.hide()

        # A different frowny face for each type of error
        self._frowny.append(Card(self._scale * 2))
        self._frowny[-1].create(
            generate_frowny_shape(self._scale * 2), sprites=self._sprites)
        self._frowny[-1].spr.move(self._smiley_xy())
        self._frowny.append(Card(self._scale))
        self._frowny[-1].create(
            generate_frowny_color(self._scale * 2), sprites=self._sprites)
        self._frowny[-1].spr.move(self._smiley_xy())
        self._frowny.append(Card(self._scale))
        self._frowny[-1].create(
            generate_frowny_texture(self._scale * 2), sprites=self._sprites)
        self._frowny[-1].spr.move(self._smiley_xy())
        self._frowny.append(Card(self._scale))
        self._frowny[-1].create(
            generate_frowny_number(self._scale * 2), sprites=self._sprites)
        self._frowny[-1].spr.move(self._smiley_xy())
        self._hide_frowny()

        size = min(self._width, self._height)
        self._label = Card()
        self._label.create(generate_label(size, LABELH * 4),
                           sprites=self._sprites)
        self._label.spr.move((LABELH, LABELH))
        self._label.spr.set_label_attributes(24, horiz_align="left")

        self._label_time = Card()
        self._label_time.create(generate_label(size, LABELH * 4),
                                sprites=self._sprites)
        self._label_time.spr.move((Gdk.Screen.width() - size - LABELH, LABELH))
        self._label_time.spr.set_label_attributes(24, horiz_align="right")

        self._labels = {'deck': '', 'match': '', 'clock': '', 'status': ''}

        Gdk.Screen.get_default().connect('size-changed', self._configure_cb)
        if self._sugar:
            self.activity.get_window().set_cursor(self._old_cursor)

    def _smiley_xy(self):
        x = int(Gdk.Screen.width() / 2) - self._card_width + DEFAULT_SPACING
        y = int(Gdk.Screen.height() / 2) - self._card_height + DEFAULT_SPACING
        return ((x, y))

    def _configure_cb(self, event):
        self.grid.stop_animation = True

        self._width = Gdk.Screen.width()
        self._height = Gdk.Screen.height()

        if self._width < self._height:
            self.portrait = True
            self.backgrounds[0].hide()
            self.backgrounds[1].set_layer(0)
        else:
            self.portrait = False
            self.backgrounds[1].hide()
            self.backgrounds[0].set_layer(0)

        size = min(self._width, self._height)
        self._label_time.spr.move((Gdk.Screen.width() - size - LABELH, LABELH))

        self.grid.rotate(self._width, self._height)

        for i in range(CARDS_IN_A_MATCH):
            self._match_area[i].spr.move(self.grid.match_to_xy(i))
        for i in range(30):
            x = self._smiley_xy()[0] - i * int(self._card_width / 2)
            y = self._smiley_xy()[1] - i * int(self._card_height / 2)
            self._smiley[i].spr.move((x, y))
        for c in self._frowny:
            c.spr.move(self._smiley_xy())

        for i, c in enumerate(self.clicked):
            if c.spr is not None:
                c.spr.move(self.grid.match_to_xy(i))

    def new_game(self, saved_state=None, deck_index=0):
        ''' Start a new game '''
        # If we were editing the word list, time to stop
        self.grid.stop_animation = True
        self.editing_word_list = False
        self.editing_custom_cards = False
        self._edit_card = None
        self._saved_state = saved_state
        self._deck_index = deck_index
        if self._sugar:
            self.activity.get_window().set_cursor(Gdk.Cursor.new(
                Gdk.CursorType.WATCH))
        GObject.timeout_add(200, self._prepare_new_game)

    def _prepare_new_game(self):
        # If there is already a deck, hide it.
        if hasattr(self, 'deck'):
            self.deck.hide()

        self._dealing = False

        self._hide_clicked()

        self._matches_on_display = False
        self._failure = None

        self._hide_frowny()

        for card in self._smiley:
            card.spr.hide()

        if self._saved_state is not None:
            _logger.debug('Restoring state: %s' % (str(self._saved_state)))
            if self.card_type == 'custom':
                self.deck.create(self._sprites, self.card_type,
                                 [self.numberO, self.numberC],
                                 self.custom_paths,
                                 DIFFICULTY_LEVEL[self.level])
            else:
                self.deck.create(self._sprites, self.card_type,
                                 [self.numberO, self.numberC], self.word_lists,
                                 DIFFICULTY_LEVEL[self.level])
            self.deck.hide()
            self.deck.index = self._deck_index
            deck_start = ROW * COL + 3
            deck_stop = deck_start + self.deck.count()
            self._restore_word_list(self._saved_state[deck_stop +
                                                      3 * self.matches:])
            if self._saved_state[deck_start] is not None:
                self.deck.restore(self._saved_state[deck_start: deck_stop])
                self.grid.restore(self.deck, self._saved_state[0: ROW * COL])
                self._restore_matches(
                    self._saved_state[deck_stop: deck_stop + 3 * self.matches])
                self._restore_clicked(
                    self._saved_state[ROW * COL: ROW * COL + 3])
            else:
                self.deck.hide()
                self.deck.shuffle()
                self.grid.deal(self.deck)
                if not self._find_a_match():
                    self.grid.deal_extra_cards(self.deck)
                self.matches = 0
                self.robot_matches = 0
                self.match_list = []
                self.total_time = 0

        elif not self.joiner():
            _logger.debug('Starting new game.')
            if self.card_type == 'custom':
                self.deck.create(self._sprites, self.card_type,
                                 [self.numberO, self.numberC],
                                 self.custom_paths,
                                 DIFFICULTY_LEVEL[self.level])
            else:
                self.deck.create(self._sprites, self.card_type,
                                 [self.numberO, self.numberC], self.word_lists,
                                 DIFFICULTY_LEVEL[self.level])
            self.deck.hide()
            self.deck.shuffle()
            self.grid.deal(self.deck)
            if not self._find_a_match():
                self.grid.deal_extra_cards(self.deck)
            self.matches = 0
            self.robot_matches = 0
            self.match_list = []
            self.total_time = 0

        # When sharer starts a new game, joiners should be notified.
        if self.sharer():
            self.activity._send_event('J')

        self._update_labels()

        self._the_game_is_over = False

        if self._game_over():
            if hasattr(self, 'timeout_id') and self.timeout_id is not None:
                GObject.source_remove(self.timeout_id)
        else:
            if hasattr(self, 'match_timeout_id') and \
                    self.match_timeout_id is not None:
                GObject.source_remove(self.match_timeout_id)
            if hasattr(self, 'animation_timeout_id') and \
                    self.animation_timeout_id is not None:
                GObject.source_remove(self.animation_timeout_id)
            self._timer_reset()

        self._hide_smiley()
        self._hide_frowny()

        self._sprites.draw_all()

        if self._sugar:
            self.activity.get_window().set_cursor(self._old_cursor)

        if self._saved_state == None and not self._played_animation:
            # Launch animated help
            if self._sugar:
                self.help_animation()
        self._played_animation = True

    def _sharing(self):
        ''' Are we sharing? '''
        if self._sugar and hasattr(self.activity, 'chattube') and \
                self.activity.chattube is not None:
            return True
        return False

    def joiner(self):
        ''' Are you the one joining? '''
        if self._sharing() and not self.activity.initiating:
            return True
        return False

    def sharer(self):
        ''' Are you the one sharing? '''
        if self._sharing() and self.activity.initiating:
            return True
        return False

    def edit_custom_card(self):
        ''' Update the custom cards from the Journal '''
        if not self.editing_custom_cards:
            return

        if self._sugar:
            self.activity.get_window().set_cursor(Gdk.Cursor.new(
                Gdk.CursorType.WATCH))
        GObject.idle_add(self._edit_custom_card_action)

    def _edit_custom_card_action(self):
        # Set the card type to custom, and generate a new deck.
        self._hide_clicked()

        self.deck.hide()
        self.card_type = 'custom'
        if len(self.custom_paths) < 3:
            for i in range(len(self.custom_paths), 81):
                self.custom_paths.append(None)
        self.deck.create(self._sprites, self.card_type,
                         [self.numberO, self.numberC], self.custom_paths,
                         DIFFICULTY_LEVEL.index(HIGH))
        self.deck.hide()
        self.matches = 0
        self.robot_matches = 0
        self.match_list = []
        self.total_time = 0
        self._edit_card = None
        self._dead_key = None
        if hasattr(self, 'timeout_id') and self.timeout_id is not None:
            GObject.source_remove(self.timeout_id)

        # Fill the grid with custom cards.
        self.grid.restore(self.deck, CUSTOM_CARD_INDICIES)
        self.set_label('deck', '')
        self.set_label('match', '')
        self.set_label('clock', '')
        self.set_label('status', _('Edit the custom cards.'))

        if self._sugar:
            self.activity.get_window().set_cursor(self._old_cursor)

    def edit_word_list(self):
        ''' Update the word cards '''
        if not self.editing_word_list:
            if hasattr(self, 'text_entry'):
                self.text_entry.hide()
                self.text_entry.disconnect(self.text_event_id)
            return

        # Set the card type to words, and generate a new deck.
        self._hide_clicked()
        self.deck.hide()
        self.card_type = 'word'
        self.deck.create(self._sprites, self.card_type,
                         [self.numberO, self.numberC], self.word_lists,
                         DIFFICULTY_LEVEL.index(HIGH))
        self.deck.hide()
        self.matches = 0
        self.robot_matches = 0
        self.match_list = []
        self.total_time = 0
        self._edit_card = None
        self._dead_key = None
        if hasattr(self, 'timeout_id') and self.timeout_id is not None:
            GObject.source_remove(self.timeout_id)
        # Fill the grid with word cards.
        self.grid.restore(self.deck, WORD_CARD_INDICIES)
        self.set_label('deck', '')
        self.set_label('match', '')
        self.set_label('clock', '')
        self.set_label('status', _('Edit the word cards.'))

        if not hasattr(self, 'text_entry'):
            self.text_entry = Gtk.TextView()
            self.text_entry.set_wrap_mode(Gtk.WrapMode.WORD)
            self.text_entry.set_pixels_above_lines(0)
            self.text_entry.set_size_request(self._card_width,
                                             self._card_height)
            '''
            rgba = Gdk.RGBA()
            rgba.red, rgba.green, rgba.blue = rgb(self._colors[1])
            rgba.alpha = 1.
            self.text_entry.override_background_color(
            Gtk.StateFlags.NORMAL, rgba)
            '''
            font_text = Pango.font_description_from_string('24')
            self.text_entry.modify_font(font_text)
            self.activity.fixed.put(self.text_entry, 0, 0)

    def _text_focus_out_cb(self, widget=None, event=None):
        if self._edit_card is None:
            self.text_entry.hide()
            self.text_entry.disconnect(self.text_event_id)
        self._update_word_card()
        self.text_entry.hide()

    def _update_word_card(self):
        bounds = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(bounds[0], bounds[1], True)
        self._edit_card.spr.set_label(text)
        (i, j) = WORD_CARD_MAP[self._edit_card.index]
        self.word_lists[i][j] = text
        self._edit_card = None

    def __event_cb(self, widget, event):
        ''' Handle touch events '''
        if event.type in (Gdk.EventType.TOUCH_BEGIN,
                          Gdk.EventType.TOUCH_END,
                          Gdk.EventType.TOUCH_UPDATE,
                          Gdk.EventType.BUTTON_PRESS,
                          Gdk.EventType.BUTTON_RELEASE,
                          Gdk.EventType.MOTION_NOTIFY):
            x = event.get_coords()[1]
            y = event.get_coords()[2]
            if event.type == Gdk.EventType.TOUCH_BEGIN or \
                    event.type == Gdk.EventType.BUTTON_PRESS:
                self._button_press(x, y)
            elif event.type == Gdk.EventType.TOUCH_UPDATE or \
                    event.type == Gdk.EventType.MOTION_NOTIFY:
                self._drag_event(x, y)
            elif event.type == Gdk.EventType.TOUCH_END or \
                    event.type == Gdk.EventType.BUTTON_RELEASE:
                self._button_release(x, y)

    def _button_press_cb(self, win, event):
        ''' Look for a card under the button press and save its position. '''
        win.grab_focus()

        x, y = map(int, event.get_coords())
        self._button_press(x, y)

    def _button_press(self, x, y):
        # Turn off help animation
        if not self._stop_help:
            self._stop_help = True
            return True

        # Don't do anything if the game is over
        if self._the_game_is_over:
            return True

        # Don't do anything during a deal
        if self._dealing:
            return True

        # Find the sprite under the mouse.
        spr = self._sprites.find_sprite((x, y))

        # Hide a frowny
        for card in self._frowny:
            if spr == card.spr:
                spr.hide()
                return True

        # Hide a smiley
        if spr == self._smiley[0].spr:
            spr.hide()
            return True

        # If there is a match showing, hide it.
        if self._matches_on_display:
            self.clean_up_match(share=True)

        # Nothing else to do.
        if spr is None:
            return True

        # Don't grab cards in the match pile.
        if spr in self.match_list:
            return True

        # Don't grab a card being animated.
        if True in self.grid.animation_lock:
            return True

        # Don't do anything if a card is already in motion
        if self._in_motion(spr):
            return True

        # Keep track of starting drag position.
        self._drag_pos = [x, y]
        self._start_pos = [x, y]

        # If the match area is full, we need to move a card back to the grid
        if self._failure is not None:
            if not self.grid.xy_in_match(spr.get_xy()):
                return True

        # We are only interested in cards in the deck.
        if self.deck.spr_to_card(spr) is not None:
            self._press = spr
            # Save its starting position so we can restore it if necessary
            if self._where_in_clicked(spr) is None:
                i = self._none_in_clicked()
                if i is None:
                    self._press = None
                else:
                    self.clicked[i].spr = spr
                    self.clicked[i].pos = spr.get_xy()
                    self.last_click = i
        else:
            self._press = None
        return True

    def clean_up_match(self, share=False):
        ''' Unselect clicked cards that are now in the match pile '''
        self._matches_on_display = False
        self._hide_clicked()
        self._smiley[0].spr.hide()
        if share and self._sharing():
            self.activity._send_event('r:')

    def clean_up_no_match(self, spr, share=False):
        ''' Return last card played to grid '''
        if self.clicked[2].spr is not None and self.clicked[2].spr != spr:
            self.return_card_to_grid(2)
            self.last_click = 2
            if share and self._sharing():
                self.activity._send_event('R:2')
        self._hide_frowny()
        self._failure = None

    def _mouse_move_cb(self, win, event):
        ''' Drag the card with the mouse. '''
        win.grab_focus()
        x, y = map(int, event.get_coords())
        self._drag_event(x, y)

    def _drag_event(self, x, y):
        if self._press is None or self.editing_word_list or \
                self.editing_custom_cards:
            self._drag_pos = [0, 0]
            return True
        dx = x - self._drag_pos[0]
        dy = y - self._drag_pos[1]
        self._press.set_layer(5000)
        self._press.move_relative((dx, dy))
        self._drag_pos = [x, y]

    def _button_release_cb(self, win, event):
        ''' Lots of possibilities here between clicks and drags '''
        win.grab_focus()
        x, y = map(int, event.get_coords())
        self._button_release(x, y)

    def _button_release(self, x, y):
        # Maybe there is nothing to do.
        if self._press is None:
            if self.editing_word_list:
                self._text_focus_out_cb()
            self._drag_pos = [0, 0]
            return True

        self._press.set_layer(2000)

        # Determine if it was a click, a drag, or an aborted drag
        d = _distance((x, y), (self._start_pos[0], self._start_pos[1]))
        if self.editing_custom_cards or d < self._card_width / 10:  # click
            move = 'click'
        elif d < self._card_width / 2:  # aborted drag
            move = 'abort'
        else:
            move = 'drag'

        if move == 'click':
            if self.editing_word_list:
                # Only edit one card at a time, so unselect other cards
                for i, c in enumerate(self.clicked):
                    if c.spr is not None and c.spr != self._press:
                        c.spr.set_label(
                            c.spr.labels[0].replace(CURSOR, ''))
                        c.spr = None  # Unselect
            elif self.editing_custom_cards:
                pass
            else:
                self.process_click(self._press)
        elif move == 'abort':
            i = self._where_in_clicked(self._press)
            self._press.move(self.clicked[i].pos)
        else:  # move == 'drag'
            move = self._process_drag(self._press, x, y)

        if move == 'abort':
            self._press = None
            return

        if self._sharing():
            if self.deck.spr_to_card(self._press) is not None:
                # Tell everyone about the card we just clicked
                self.activity._send_event(
                    'B:%d' % (self.deck.spr_to_card(self._press).index))
            i = self._where_in_clicked(self._press)
            if i is not None:
                self.activity._send_event('S:%d' % (i))
            elif self.last_click is not None:
                self.activity._send_event('S:%d' % (self.last_click))
            else:
                _logger.error('WARNING: Cannot find last click')
            self.last_click = None

        self.process_selection(self._press)
        self._press = None
        return

    def process_click(self, spr):
        ''' Either move the card to the match area or back to the grid.'''
        if self.grid.spr_to_grid(spr) is None:  # Return card to grid
            i = self._where_in_clicked(spr)
            if i is not None:
                self.return_card_to_grid(i)
                self.last_click = i
            self._hide_frowny()
            self._failure = None
        else:
            i = self._where_in_clicked(spr)
            if i is None:
                spr.move((self._start_pos))
            else:
                spr.set_layer(5000)
                self.grid.grid[self.grid.spr_to_grid(spr)] = None
                self.grid.display_match(spr, i)

    def _process_drag(self, spr, x, y):
        ''' Either drag to the match area, back to the grid, or to a
        new slot. '''
        move = 'drag'
        if self.grid.spr_to_grid(spr) is None:
            # Returning a card to the grid
            '''
            if (self.portrait and y < self.grid.bottom) or \
                    (not self.portrait and x > self.grid.left):
            '''
            if y < self.grid.bottom:
                i = self.grid.xy_to_grid((x, y))
                if self.grid.grid[i] is not None:
                    i = self.grid.find_an_empty_slot()
                spr.move(self.grid.grid_to_xy(i))
                self.grid.grid[i] = self.deck.spr_to_card(spr)
                i = self._where_in_clicked(spr)
                self.last_click = i
                self.clicked[i].reset()
                self._hide_frowny()
                self._failure = None
            # Move a click to a different match slot
            else:
                i = self._where_in_clicked(spr)
                j = self.grid.xy_to_match((x, y))
                if i == j:
                    spr.move(self.clicked[i].pos)
                else:
                    temp_spr = self.clicked[i].spr
                    self.clicked[i].spr = self.clicked[j].spr
                    self.clicked[j].spr = temp_spr
                    if self.clicked[i].spr is not None:
                        self.clicked[i].spr.move(self.grid.match_to_xy(i))
                    if self.clicked[j].spr is not None:
                        self.clicked[j].spr.move(self.grid.match_to_xy(j))
                move = 'abort'
        else:
            i = self._where_in_clicked(spr)
            if i is None:
                move = 'abort'
               # Moving a card to the match area
               # elif (self.portrait and y > self.grid.bottom) or \
               #        (not self.portrait and x < self.grid.left):
            elif y > self.grid.bottom:
                self.grid.grid[self.grid.spr_to_grid(spr)] = None
                spr.move(self._match_area[i].spr.get_xy())
            else:  # Shuffle positions in match area
                j = self.grid.xy_to_grid((x, y))
                k = self.grid.xy_to_grid(self.clicked[i].pos)
                if j < 0 or k < 0 or j > 15 or k > 15 or j == k:
                    spr.move(self.clicked[i].pos)
                else:
                    tmp_card = self.grid.grid[k]
                    if self.grid.grid[j] is not None:
                        self.grid.grid[j].spr.move(self.grid.grid_to_xy(k))
                        spr.move(self.grid.grid_to_xy(j))
                        self.grid.grid[k] = self.grid.grid[j]
                        self.grid.grid[j] = tmp_card
                    else:
                        spr.move(self.grid.grid_to_xy(j))
                        self.grid.grid[j] = self.grid.grid[k]
                        self.grid.grid[k] = None
                move = 'abort'
                self.clicked[i].reset()

        self._consistency_check()
        return move

    def _consistency_check(self):
        ''' Make sure that the cards in the grid are really in the grid '''
        # Root cause: a race condition?
        for i in range(3):
            spr = self.clicked[i].spr
            if spr is not None:
                if not self.grid.xy_in_match(spr.get_xy()):
                    _logger.debug('card in both the grid and '
                                  'match area (%d)' % (i))
                    spr.move(self.grid.match_to_xy(i))

    def process_selection(self, spr):
        ''' After a card has been selected... '''
        if self.editing_word_list:  # Edit label of selected card
            x, y = spr.get_xy()
            if self._edit_card is not None:
                self._update_word_card()
            self._edit_card = self.deck.spr_to_card(spr)
            self.text_buffer = self.text_entry.get_buffer()
            self.text_entry.show()
            self.text_buffer.set_text(self._edit_card.spr.labels[0])
            self.activity.fixed.move(self.text_entry, x, y)
            self.text_event_id = self.text_entry.connect(
                'focus-out-event', self._text_focus_out_cb)
            self.text_entry.grab_focus()
        elif self.editing_custom_cards:
            # Only edit one card at a time, so unselect other cards
            for i, c in enumerate(self.clicked):
                if c.spr is not None and c.spr != spr:
                    c.spr = None
            # Choose an image from the Journal for a card
            self._edit_card = self.deck.spr_to_card(spr)
            self._choose_custom_card()
        elif self._none_in_clicked() is None:
            # If we have three cards selected, test for a match.
            self._test_for_a_match()
            if self._matches_on_display:
                self._smiley[0].spr.set_layer(10000)
            elif not self._the_game_is_over and self._failure is not None:
                self._frowny[self._failure].spr.set_layer(10000)
        return

    def _none_in_clicked(self):
        ''' Look for room on the click list '''
        for i, c in enumerate(self.clicked):
            if c.spr is None:
                return i
        return None

    def _where_in_clicked(self, spr):
        ''' Is the card already selected? '''
        for i, c in enumerate(self.clicked):
            if c.spr == spr:
                return i
        return None

    def add_to_clicked(self, spr, pos=[0, 0]):
        ''' Add a card to the selected list '''
        i = self._where_in_clicked(spr)
        if i is not None:
            self.last_click = i
        else:
            i = self._none_in_clicked()
            if i is None:
                _logger.error('WARNING: No room in clicked')
                self.last_click = None
                return
            self.clicked[i].spr = spr
            self.clicked[i].pos = pos
            self.last_click = i

    def _hide_clicked(self):
        ''' Hide the clicked cards '''
        if self.editing_custom_cards:
            return
        for c in self.clicked:
            if c is not None:
                c.hide()

    def _hide_smiley(self):
        for card in self._smiley:
            card.spr.hide()

    def _hide_frowny(self):
        ''' Hide the frowny cards '''
        for card in self._frowny:
            card.spr.hide()

    def return_card_to_grid(self, i):
        ''' "Unclick" '''
        j = self.grid.find_an_empty_slot()
        if j is not None:
            self.grid.return_to_grid(self.clicked[i].spr, j, i)
            self.grid.grid[j] = self.deck.spr_to_card(self.clicked[i].spr)
            self.clicked[i].reset()

    def _game_over(self):
        ''' Game is over when the deck is empty and no more matches. '''
        if self.deck.empty() and not self._find_a_match():
            self._hide_frowny()
            self._update_labels()
            self.set_label('deck', '')
            self.set_label('clock', '')
            self.set_label('status', '%s\n(%d:%02d)' %
                           (_('Game over'), int(self.total_time / 60),
                            int(self.total_time % 60)))
            self._smiley[0].show_card()
            self.animation_timeout_id = GObject.timeout_add(
                200, self._show_animation, 0)
            self._the_game_is_over = True
        elif self.grid.cards_in_grid() == DEAL + 3 \
                and not self._find_a_match():
            self._hide_frowny()
            self._update_labels()
            self.set_label('deck', '')
            self.set_label('clock', '')
            self.set_label('status', _('unsolvable'))
            self._the_game_is_over = True
        return self._the_game_is_over

    def _test_for_a_match(self):
        ''' If we have a match, then we have work to do. '''
        if self._match_check([self.deck.spr_to_card(self.clicked[0].spr),
                              self.deck.spr_to_card(self.clicked[1].spr),
                              self.deck.spr_to_card(self.clicked[2].spr)],
                             self.card_type):
            # Stop the timer.
            if hasattr(self, 'timeout_id'):
                if self.timeout_id is not None:
                    GObject.source_remove(self.timeout_id)
                self.total_time += GObject.get_current_time() - self.start_time

            # Increment the match counter and add the match to the match list.
            self.matches += 1
            for c in self.clicked:
                self.match_list.append(c.spr)
            self._matches_on_display = True

            # Test to see if the game is over.
            if self._game_over():
                if hasattr(self, 'timeout_id'):
                    GObject.source_remove(self.timeout_id)
                if self.low_score[self.level] == -1:
                    self.low_score[self.level] = self.total_time
                elif self.total_time < self.low_score[self.level]:
                    self.low_score[self.level] = self.total_time
                    self.set_label('status', '%s (%d:%02d)' %
                                   (_('New record'), int(self.total_time / 60),
                                    int(self.total_time % 60)))
                # Round to nearest second
                self.all_scores.append(int(self.total_time + 0.5))
                if not self._sugar:
                    self.activity.save_score()
                else:
                    self._auto_increase_difficulty()
                return True
            else:
                if self.deck.cards_remaining() > 0:
                    self._dealing = True
                    # Wait a few seconds before dealing new cards.
                    GObject.timeout_add(2000, self._deal_new_cards)

            # Keep playing.
            self._update_labels()
            self._timer_reset()

        else:
            self._matches_on_display = False

    def _auto_increase_difficulty(self):
        ''' Auto advance levels '''
        return  # was found to be confusing

        '''
        if self.level == 2 and len(self.all_scores) > 3:
            sum = 0
            for i in range(3):
                sum += self.all_scores[-i - 1]
            if sum < 120:
                self.level = 0
                self.activity.intermediate_button.set_active(True)
        elif self.level == 0 and len(self.all_scores) > 8:
            sum = 0
            for i in range(3):
                sum += self.all_scores[-i - 1]
            if sum < 240:
                self.level = 1
                self.activity.expert_button.set_active(True)
        '''

    def _deal_new_cards(self):
        ''' Deal three new cards. '''
        self.grid.replace(self.deck)
        self.set_label('deck', '%d %s' %
                       (self.deck.cards_remaining(), _('cards')))
        # Consolidate the grid.
        self.grid.consolidate()
        # Test to see if we need to deal extra cards.
        if not self._find_a_match():
            self.grid.deal_extra_cards(self.deck)
            self._failure = None
        self._dealing = False

    def __draw_cb(self, canvas, cr):
        self._sprites.redraw_sprites(cr=cr)

    def _expose_cb(self, win, event):
        ''' Callback to handle window expose events '''
        self.do_expose_event(event)
        return True

    # Handle the expose-event by drawing
    def do_expose_event(self, event):

        # Create the cairo context
        cr = self._canvas.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                     event.area.width, event.area.height)
        cr.clip()

        # Refresh sprite list
        if cr is not None:
            self._sprites.redraw_sprites(cr=cr)

    def _destroy_cb(self, win, event):
        ''' This is the end '''
        Gtk.main_quit()

    def _update_labels(self):
        ''' Write strings to a label in the toolbar. '''
        self.set_label('deck', '%d %s' %
                       (self.deck.cards_remaining(), _('cards')))
        self.set_label('status', '')
        if self.matches - self.robot_matches == 1:
            if self.robot_matches > 0:
                self.set_label('match', '%d %s\n(%d %s)' % (
                    self.matches - self.robot_matches,
                    _('match'),
                    self.robot_matches,
                    _('robot')))
            else:
                self.set_label('match', '%d %s' % (self.matches, _('match')))
        else:
            if self.robot_matches > 0:
                self.set_label('match', '%d %s\n(%d %s)' % (
                    self.matches - self.robot_matches,
                    _('matches'),
                    self.robot_matches,
                    _('robot')))
            else:
                self.set_label('match', '%d %s' % (self.matches, _('matches')))

    def set_label(self, label, s):
        ''' Update the toolbar labels '''
        if label in self._labels:
            self._labels[label] = s

        msg = "%s\n%s" % (self._labels['deck'], self._labels['match'])
        self._label.spr.set_label(msg)

        msg = "%s\n%s" % (self._labels['clock'], self._labels['status'])
        self._label_time.spr.set_label(msg)

    def _restore_clicked(self, saved_selected_indices):
        ''' Restore the selected cards upon resume or share. '''
        j = 0
        for i in saved_selected_indices:
            if i is None or self.deck.index_to_card(i) is None:
                self.clicked[j].reset()
            else:
                self.clicked[j].spr = self.deck.index_to_card(i).spr
                self.clicked[j].spr.move(self.grid.match_to_xy(j))
                self.clicked[j].pos = self.grid.match_to_xy(j)
                self.clicked[j].spr.set_layer(2000)
            j += 1
        self.process_selection(None)

    def _restore_matches(self, saved_match_list_indices):
        ''' Restore the match list upon resume or share. '''
        self.match_list = []
        for i in saved_match_list_indices:
            if i is not None:
                try:
                    self.match_list.append(self.deck.index_to_card(i).spr)
                except AttributeError:
                    _logger.debug('index %s was not found in deck' % (str(i)))

    def _restore_word_list(self, saved_word_list):
        ''' Restore the word list upon resume or share. '''
        if len(saved_word_list) == 9:
            for i in range(3):
                for j in range(3):
                    self.word_lists[i][j] = saved_word_list[i * 3 + j]

    def _counter(self):
        ''' Display of seconds since start_time. '''
        seconds = int(GObject.get_current_time() - self.start_time)
        self.set_label('clock', str(seconds))
        if self.robot and self.robot_time < seconds:
            self._find_a_match(robot_match=True)
        else:
            self.timeout_id = GObject.timeout_add(1000, self._counter)

    def _timer_reset(self):
        ''' Reset the timer for the robot '''
        self.start_time = GObject.get_current_time()
        self.timeout_id = None
        if not self._the_game_is_over:
            self._counter()

    def _show_animation(self, i):
        ''' Show smiley animation '''
        if i < len(self._smiley) - 1:
            self._smiley[i].show_card(layer=20000)
            self.animation_timeout_id = GObject.timeout_add(
                100, self._show_animation, i + 1)
        else:
            for card in self._smiley:
                card.spr.hide()
            self.match_timeout_id = GObject.timeout_add(
                1000, self._show_matches, 0)

    def _show_matches(self, i):
        ''' Show all the matches as a simple animation. '''
        if i < self.matches and \
                i * CARDS_IN_A_MATCH < len(self.match_list):
            for j in range(CARDS_IN_A_MATCH):
                self.grid.display_match(
                    self.match_list[i * CARDS_IN_A_MATCH + j], j)
            self.match_timeout_id = GObject.timeout_add(
                2000, self._show_matches, i + 1)

    def _find_a_match(self, robot_match=False):
        ''' Check to see whether there are any matches on the board. '''
        # Before finding a match, return any cards from the match area
        if self._matches_on_display:
            if not self.deck.empty():
                self._matches_on_display = False
                GObject.timeout_add(1000, self.clean_up_match)
        else:
            for c in self.clicked:
                if c.spr is not None:
                    i = self.grid.find_an_empty_slot()
                    if i is not None:
                        c.spr.move(self.grid.grid_to_xy(i))
                        self.grid.grid[i] = self.deck.spr_to_card(c.spr)
                        c.reset()

        a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        for i in Permutation(a):  # TODO: really should be combination
            cardarray = [self.grid.grid[i[0]],
                         self.grid.grid[i[1]],
                         self.grid.grid[i[2]]]
            if self._match_check(cardarray, self.card_type):
                if robot_match:
                    # Stop animations before moving robot match
                    self.grid.stop_animation = True
                    self._robot_match(i)
                return True
        return False

    def _robot_match(self, i):
        ''' Robot finds a match '''
        for j in range(CARDS_IN_A_MATCH):
            # WARNING: Sometimes there is a race condition between the
            # robot delay and shoing a robot match.
            if self.grid.grid[i[j]] is not None:
                self.clicked[j].spr = self.grid.grid[i[j]].spr
                self.grid.grid[i[j]].spr.move(self.grid.match_to_xy(j))
            else:
                _logger.error('in robot match, grid[%d] is None' % (i[j]))
            self.grid.grid[i[j]] = None
        self.robot_matches += 1
        self._test_for_a_match()
        self._smiley[0].spr.set_layer(100)
        self._matches_on_display = True

    def _match_check(self, cardarray, card_type):
        ''' For each attribute, either it is the same or different. '''
        for a in cardarray:
            if a is None:
                return False

        if (cardarray[0].shape + cardarray[1].shape +
            cardarray[2].shape) % 3 != 0:
            self._failure = 0
            return False
        if (cardarray[0].color + cardarray[1].color +
            cardarray[2].color) % 3 != 0:
            self._failure = 1
            return False
        if (cardarray[0].fill + cardarray[1].fill +
            cardarray[2].fill) % 3 != 0:
            self._failure = 2
            return False
        # Special case: only check number when shapes are the same
        if card_type == 'word':
            if cardarray[0].shape == cardarray[1].shape and \
               cardarray[0].shape == cardarray[2].shape and \
               (cardarray[0].num + cardarray[1].num + cardarray[2].num) % 3 \
               != 0:
                return False
        else:
            if (cardarray[0].num + cardarray[1].num +
                cardarray[2].num) % 3 != 0:
                self._failure = 3
                return False
        self._failure = None
        return True

    def _choose_custom_card(self):
        ''' Select a custom card from the Journal '''
        self.activity.get_window().set_cursor(Gdk.Cursor.new(
            Gdk.CursorType.WATCH))
        GObject.idle_add(self._choose_custom_card_action)

    def _choose_custom_card_action(self):
        from sugar3.graphics.objectchooser import ObjectChooser
        try:
            from sugar3.graphics.objectchooser import FILTER_TYPE_GENERIC_MIME
        except:
            FILTER_TYPE_GENERIC_MIME = 'generic_mime'
        from sugar3 import mime

        chooser = None
        name = None

        if hasattr(mime, 'GENERIC_TYPE_IMAGE'):
            # See #2398
            if 'image/svg+xml' not in \
                    mime.get_generic_type(mime.GENERIC_TYPE_IMAGE).mime_types:
                mime.get_generic_type(
                    mime.GENERIC_TYPE_IMAGE).mime_types.append('image/svg+xml')
            try:
                chooser = ObjectChooser(parent=self.activity,
                                        what_filter=mime.GENERIC_TYPE_IMAGE,
                                        filter_type=FILTER_TYPE_GENERIC_MIME,
                                        show_preview=True)
            except:
                chooser = ObjectChooser(parent=self.activity,
                                        what_filter=mime.GENERIC_TYPE_IMAGE)
        else:
            try:
                chooser = ObjectChooser(parent=self, what_filter=None)
            except TypeError:
                chooser = ObjectChooser(
                    None, self.activity,
                    Gtk.DialogFlags.MODAL |
                    Gtk.DialogFlags.DESTROY_WITH_PARENT)

        if chooser is not None:
            try:
                result = chooser.run()
                if result == Gtk.ResponseType.ACCEPT:
                    jobject = chooser.get_selected_object()
                    if jobject and jobject.file_path:
                        name = jobject.metadata['title']
                        mime_type = jobject.metadata['mime_type']
                        _logger.debug('result of choose: %s (%s)' %
                                      (name, str(mime_type)))
            finally:
                chooser.destroy()
                del chooser

            if name is not None:
                self._find_custom_paths(jobject)

            # Regenerate the deck with the new card definitions
            self.deck.create(self._sprites, self.card_type,
                             [self.numberO, self.numberC],
                             self.custom_paths, DIFFICULTY_LEVEL[2])
            self.deck.hide()
            self.grid.restore(self.deck, CUSTOM_CARD_INDICIES)

        self.activity.get_window().set_cursor(self._old_cursor)

    def _find_custom_paths(self, jobject):
        ''' Associate a Journal object with a card '''
        from sugar3.datastore import datastore

        found_a_sequence = False
        if self.custom_paths[0] is None:
            basename, suffix, i = _find_the_number_in_the_name(
                jobject.metadata['title'])
            ''' If this is the first card, try to find paths for other custom
            cards based on the name; else just load the card. '''
            if i >= 0:
                dsobjects, nobjects = datastore.find(
                    {'mime_type': [str(jobject.metadata['mime_type'])]})
                self.custom_paths = []
                if nobjects > 0:
                    for j in range(DECKSIZE):
                        for i in range(nobjects):
                            if dsobjects[i].metadata['title'] == \
                                    _construct_a_name(basename, j + 1, suffix):
                                self.custom_paths.append(dsobjects[i])
                                break

                if len(self.custom_paths) < 9:
                    for i in range(3, 81):
                        self.custom_paths.append(
                            self.custom_paths[int(i / 27)])
                elif len(self.custom_paths) < 27:
                    for i in range(9, 81):
                        self.custom_paths.append(
                            self.custom_paths[int(i / 9)])
                elif len(self.custom_paths) < 81:
                    for i in range(9, 81):
                        self.custom_paths.append(
                            self.custom_paths[int(i / 3)])
                found_a_sequence = True
                self.activity.metadata['custom_object'] = jobject.object_id
                self.activity.metadata['custom_mime_type'] = \
                    jobject.metadata['mime_type']

        if not found_a_sequence:
            grid_index = self.grid.spr_to_grid(self._edit_card.spr)
            self.custom_paths[grid_index] = jobject
            self.activity.metadata['custom_' + str(grid_index)] = \
                jobject.object_id

        self.card_type = 'custom'
        self.activity.button_custom.set_sensitive(True)
        return

    def _in_motion(self, spr):
        ''' Is the sprite in a grid or match position or in motion? '''
        x, y = spr.get_xy()
        if self.grid.xy_in_match((x, y)):
            return False
        if self.grid.xy_in_grid((x, y)):
            return False
        return True

    def _get_help_files(self):
        from sugar3.activity import activity

        help_target = os.path.join(activity.get_bundle_path(),
                                   'images', 'help-*.png')
        help_files = glob.glob(help_target)
        return sorted(help_files)

    def help_animation(self):
        ''' Simple explanatory animation at start of play '''
        if not self._sugar:
            return

        # from sugar3.activity import activity

        self._played_animation = True
        for help_file in self._get_help_files():
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                help_file, 550, 650)
            self._help.append(Sprite(self._sprites,
                                     int((self._width - 550) / 2),
                                     int((self._height - 650) / 2),
                                     pixbuf))
            self._help[-1].hide()

        self._help_index = 0
        self._stop_help = False
        self._help[self._help_index].set_layer(5000)
        self._help_timeout_id = GObject.timeout_add(2000, self._help_next)

    def _help_next(self):
        ''' Load the next frame in the animation '''
        self._help[self._help_index].hide()
        if self._stop_help:
            self._help = []
            return
        self._help_index += 1
        self._help_index %= len(self._help)
        self._help[self._help_index].set_layer(5000)
        if self._help_index in [0, 13, 25, 30]:
            pause = 2500
        else:
            pause = 750
        self._help_timeout_id = GObject.timeout_add(pause, self._help_next)


class Permutation:
    '''Permutaion class for checking for all possible matches on the grid '''

    def __init__(self, elist):
        self._data = elist[:]
        self._sofar = []

    def __iter__(self):
        return self.next()

    def next(self):
        for e in self._data:
            if e not in self._sofar:
                self._sofar.append(e)
                if len(self._sofar) == 3:
                    yield self._sofar[:]
                else:
                    for v in self.next():
                        yield v
                self._sofar.pop()


def svg_str_to_pixbuf(svg_string, w, h):
    """ Load pixbuf from SVG string """
    pl = GdkPixbuf.PixbufLoader.new_with_type('svg')
    pl.set_size(w, h)
    pl.write(svg_string)
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf


def svg_from_file(pathname):
    """ Read SVG string from a file """
    f = file(pathname, 'r')
    svg = f.read()
    f.close()
    return(svg)
