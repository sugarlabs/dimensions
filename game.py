# -*- coding: utf-8 -*-
#Copyright (c) 2009,12 Walter Bender
#Copyright (c) 2009 Michele Pratusevich
#Copyright (c) 2009 Vincent Le

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA


import pygtk
pygtk.require('2.0')
import gtk
import gobject

import os

from gettext import gettext as _

from math import sqrt

from sugar.graphics.objectchooser import ObjectChooser
from sugar.datastore import datastore
from sugar import mime
from sugar.activity import activity

import logging
_logger = logging.getLogger('visualmatch-activity')

try:
    from sugar.graphics import style
    GRID_CELL_SIZE = style.GRID_CELL_SIZE
except ImportError:
    GRID_CELL_SIZE = 0

from constants import LOW, MEDIUM, HIGH, MATCHMASK, ROW, COL, \
    WORD_CARD_INDICIES, DEAD_DICTS, DEAD_KEYS, WHITE_SPACE, \
    NOISE_KEYS, WORD_CARD_MAP, KEYMAP, CARD_HEIGHT, CARD_WIDTH, DEAL, \
    DIFFICULTY_LEVEL, BACKGROUNDMASK, DECKSIZE, CUSTOM_CARD_INDICIES

from grid import Grid
from deck import Deck
from card import Card
from sprites import Sprites, Sprite
from gencards import generate_match_card, \
    generate_smiley, generate_frowny_texture,  generate_frowny_shape, \
    generate_frowny_color, generate_frowny_number

CURSOR = '█'


def _distance(pos1, pos2):
    ''' simple distance function '''
    return sqrt((pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) + \
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
            self.spr = None
        self.pos = [0, 0]


class Game():
    ''' The game play -- called from within Sugar or GNOME '''

    def __init__(self, canvas, parent=None):
        ''' Initialize the playing surface '''
        self.activity = parent

        if parent is None:  # Starting from command line
            self._sugar = False
            self._canvas = canvas
        else:  # Starting from Sugar
            self._sugar = True
            self._canvas = canvas
            parent.show_all()

        self._canvas.set_flags(gtk.CAN_FOCUS)
        self._canvas.connect('expose-event', self._expose_cb)
        self._canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self._canvas.connect('button-press-event', self._button_press_cb)
        self._canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self._canvas.connect('button-release-event', self._button_release_cb)
        self._canvas.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self._canvas.connect("motion-notify-event", self._mouse_move_cb)
        self._canvas.connect('key_press_event', self._keypress_cb)
        self._width = gtk.gdk.screen_width()
        self._height = gtk.gdk.screen_height() - GRID_CELL_SIZE
        self._scale = 0.8 * self._height / (CARD_HEIGHT * 5.5)
        self._card_width = CARD_WIDTH * self._scale
        self._card_height = CARD_HEIGHT * self._scale
        self.custom_paths = [None, None, None, None, None, None, None, None,
                             None]
        self._sprites = Sprites(self._canvas)
        self._press = None
        self.matches = 0
        self.robot_matches = 0
        self._match_display_area = []
        self._matches_on_display = False
        self._smiley = []
        self._frowny = []
        self._help = []
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
        self.card_type = 'pattern'
        self.buddies = []

    def new_game(self, saved_state=None, deck_index=0):
        ''' Start a new game '''
        # If we were editing the word list, time to stop
        self.editing_word_list = False
        self.editing_custom_cards = False
        self._edit_card = None

        # If there is already a deck, hide it.
        if hasattr(self, 'deck'):
            self.deck.hide()

        # The first time through, initialize the grid, and overlays.
        if not hasattr(self, 'grid'):
            self.grid = Grid(self._width, self._height, self._card_width,
                             self._card_height)

            for i in range(3):
                self.clicked.append(Click())

            for i in range(3):
                self._match_display_area.append(Card(self._sprites,
                                          generate_match_card(self._scale),
                                          [MATCHMASK, 0, 0, 0]))
                self._match_display_area[-1].spr.move(self.grid.match_to_xy(i))

            for i in range((ROW - 1) * COL):
                self._smiley.append(
                    Card(self._sprites, generate_smiley(self._scale),
                         [BACKGROUNDMASK, 0, 0, 0]))
                self._smiley[-1].spr.move(self.grid.grid_to_xy(i))
            self._smiley.append(Card(self._sprites,
                                     generate_smiley(self._scale),
                                    [BACKGROUNDMASK, 0, 0, 0]))
            self._smiley[-1].spr.move(self.grid.match_to_xy(3))
            self._smiley[-1].spr.hide()

            # A different frowny face for each type of error
            self._frowny.append(
                Card(self._sprites, generate_frowny_shape(self._scale),
                         [BACKGROUNDMASK, 0, 0, 0]))
            self._frowny[-1].spr.move(self.grid.match_to_xy(3))
            self._frowny.append(
                Card(self._sprites, generate_frowny_color(self._scale),
                         [BACKGROUNDMASK, 0, 0, 0]))
            self._frowny[-1].spr.move(self.grid.match_to_xy(3))
            self._frowny.append(
                Card(self._sprites, generate_frowny_texture(self._scale),
                         [BACKGROUNDMASK, 0, 0, 0]))
            self._frowny[-1].spr.move(self.grid.match_to_xy(3))
            self._frowny.append(
                Card(self._sprites, generate_frowny_number(self._scale),
                         [BACKGROUNDMASK, 0, 0, 0]))
            self._frowny[-1].spr.move(self.grid.match_to_xy(3))

        if self._sugar:
            for i in range(22):
                path = os.path.join(activity.get_bundle_path(),
                                    'images', 'help-%d.svg' % i)
                svg_str = svg_from_file(path)
                pixbuf = svg_str_to_pixbuf(svg_str, int(self._width),
                                           int(self._height))
                self._help.append(Sprite(self._sprites, 0, 0, pixbuf))
                self._help[-1].hide()

        for c in self.clicked:
            c.hide()

        self._matches_on_display = False
        for c in self._frowny:
            c.spr.hide()
        self._smiley[-1].spr.hide()

        if saved_state is not None:
            _logger.debug('Restoring state: %s' % (str(saved_state)))
            if self.card_type == 'custom':
                self.deck = Deck(self._sprites, self.card_type,
                             [self.numberO, self.numberC], self.custom_paths,
                             self._scale, DIFFICULTY_LEVEL[self.level])
            else:
                self.deck = Deck(self._sprites, self.card_type,
                             [self.numberO, self.numberC], self.word_lists,
                             self._scale, DIFFICULTY_LEVEL[self.level])
            self.deck.hide()
            self.deck.index = deck_index
            deck_start = ROW * COL + 3
            deck_stop = deck_start + self.deck.count()
            self._restore_word_list(saved_state[deck_stop + \
                                                    3 * self.matches:])
            self.deck.restore(saved_state[deck_start: deck_stop])
            self.grid.restore(self.deck, saved_state[0: ROW * COL])
            self._restore_matches(saved_state[deck_stop: deck_stop + \
                                                  3 * self.matches])
            self._restore_clicked(saved_state[ROW * COL: ROW * COL + 3])

        elif not self.joiner():
            _logger.debug('Starting new game.')
            if self.card_type == 'custom':
                self.deck = Deck(self._sprites, self.card_type,
                                 [self.numberO, self.numberC],
                                 self.custom_paths, self._scale,
                                 DIFFICULTY_LEVEL[self.level])
            else:
                self.deck = Deck(self._sprites, self.card_type,
                                 [self.numberO, self.numberC], self.word_lists,
                                 self._scale, DIFFICULTY_LEVEL[self.level])
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
        if self._game_over():
            if hasattr(self, 'timeout_id') and self.timeout_id is not None:
                gobject.source_remove(self.timeout_id)
        else:
            if hasattr(self, 'match_timeout_id') and \
               self.match_timeout_id is not None:
                gobject.source_remove(self.match_timeout_id)
            self._timer_reset()

        for i in range((ROW - 1) * COL):
            self._smiley[i].hide_card()

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

        # Set the card type to custom, and generate a new deck.
        for c in self.clicked:
            c.hide()

        self.deck.hide()
        self.card_type = 'custom'
        if len(self.custom_paths) < 3:
            for i in range(len(self.custom_paths), 81):
                self.custom_paths.append(None)
        self.deck = Deck(self._sprites, self.card_type,
                         [self.numberO, self.numberC],
                         self.custom_paths,
                         self._scale, DIFFICULTY_LEVEL.index(HIGH))
        self.deck.hide()
        self.matches = 0
        self.robot_matches = 0
        self.match_list = []
        self.total_time = 0
        self._edit_card = None
        self._dead_key = None
        if hasattr(self, 'timeout_id') and self.timeout_id is not None:
            gobject.source_remove(self.timeout_id)

        # Fill the grid with custom cards.
        self.grid.restore(self.deck, CUSTOM_CARD_INDICIES)
        self.set_label('deck', '')
        self.set_label('match', '')
        self.set_label('clock', '')
        self.set_label('status', _('Edit the custom cards.'))

    def edit_word_list(self):
        ''' Update the word cards '''
        if not self.editing_word_list:
            return

        # Set the card type to words, and generate a new deck.
        for c in self.clicked:
            if c.spr is not None:
                c.hide()
        self.deck.hide()
        self.card_type = 'word'
        self.deck = Deck(self._sprites, self.card_type,
                         [self.numberO, self.numberC], self.word_lists,
                         self._scale, DIFFICULTY_LEVEL.index(HIGH))
        self.deck.hide()
        self.matches = 0
        self.robot_matches = 0
        self.match_list = []
        self.total_time = 0
        self._edit_card = None
        self._dead_key = None
        if hasattr(self, 'timeout_id') and self.timeout_id is not None:
            gobject.source_remove(self.timeout_id)
        # Fill the grid with word cards.
        self.grid.restore(self.deck, WORD_CARD_INDICIES)
        self.set_label('deck', '')
        self.set_label('match', '')
        self.set_label('clock', '')
        self.set_label('status', _('Edit the word cards.'))

    def _button_press_cb(self, win, event):
        ''' Look for a card under the button press and save its position. '''
        win.grab_focus()

        # Turn off help animation
        self._stop_help = True

        # Keep track of starting drag position.
        x, y = map(int, event.get_coords())
        self._drag_pos = [x, y]
        self._start_pos = [x, y]

        # Find the sprite under the mouse.
        spr = self._sprites.find_sprite((x, y))

        # If there is a match showing, hide it.
        if self._matches_on_display:
            self.clean_up_match(share=True)
        elif self._failure is not None:  # Return last card clicked to grid
            self.clean_up_no_match(spr, share=True)

        # Nothing else to do.
        if spr is None:
            return True

        # Don't grab cards in the match pile.
        if spr in self.match_list:
            return True

        # Don't grab a card being animated.
        if True in self.grid.animation_lock:
            _logger.debug('waiting on animation lock')
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
        for c in self.clicked:
            c.hide()
        self._smiley[-1].spr.hide()
        self._matches_on_display = False
        if share and self._sharing():
            self.activity._send_event('r:')

    def clean_up_no_match(self, spr, share=False):
        ''' Return last card played to grid '''
        if self.clicked[2].spr is not None and self.clicked[2].spr != spr:
            self.return_card_to_grid(2)
            self.last_click = 2
            if share and self._sharing():
                self.activity._send_event('R:2')
        for c in self._frowny:
            c.spr.hide()
        self._failure = None

    def _mouse_move_cb(self, win, event):
        ''' Drag the card with the mouse. '''
        if self._press is None or \
           self.editing_word_list or \
           self.editing_custom_cards:
            self._drag_pos = [0, 0]
            return True
        win.grab_focus()
        x, y = map(int, event.get_coords())
        dx = x - self._drag_pos[0]
        dy = y - self._drag_pos[1]
        self._press.set_layer(5000)
        self._press.move_relative((dx, dy))
        self._drag_pos = [x, y]

    def _button_release_cb(self, win, event):
        ''' Lots of possibilities here between clicks and drags '''
        win.grab_focus()

        # Maybe there is nothing to do.
        if self._press is None:
            self._drag_pos = [0, 0]
            return True

        self._press.set_layer(2000)

        # Determine if it was a click, a drag, or an aborted drag
        x, y = map(int, event.get_coords())
        d = _distance((x, y), (self._start_pos[0], self._start_pos[1]))
        if d < self._card_width / 10:  # click
            move = 'click'
        elif d < self._card_width / 2:  # aborted drag
            move = 'abort'
        else:
            move = 'drag'

        # Determine status of card
        status = self.grid.spr_to_grid(self._press)

        if move == 'click':
            if self.editing_word_list:
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
                _logger.debug('WARNING: Cannot find last click')
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
            for c in self._frowny:
                c.spr.hide()
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
            if x > self.grid.left:  # Returning a card to the grid
                i = self.grid.xy_to_grid((x, y))
                if self.grid.grid[i] is not None:
                    i = self.grid.find_an_empty_slot()
                spr.move(self.grid.grid_to_xy(i))
                self.grid.grid[i] = self.deck.spr_to_card(spr)
                i = self._where_in_clicked(spr)
                self.last_click = i
                self.clicked[i].reset()
                for c in self._frowny:
                    c.spr.hide()
            else:  # Move a click to a different match slot
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
            if x < self.grid.left:  # Moving a card to the match area
                self.grid.grid[self.grid.spr_to_grid(spr)] = None
                spr.move(self._match_display_area[i].spr.get_xy())
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
        return move

    def process_selection(self, spr):
        ''' After a card has been selected... '''
        if self.editing_word_list:  # Edit label of selected card
            self._edit_card = self.deck.spr_to_card(spr)
            spr.set_label(spr.labels[0] + CURSOR)
        elif self.editing_custom_cards:
            # Only edit one card at a time, so unselect other cards
            for i, c in enumerate(self.clicked):
                if c.spr is not None and c.spr != spr:
                    c.spr = None
            # Choose an image from the Journal for a card
            self._edit_card = self.deck.spr_to_card(spr)
            self._choose_custom_card()
            # Regenerate the deck with the new card definitions
            self.deck = Deck(self._sprites, self.card_type,
                             [self.numberO, self.numberC],
                             self.custom_paths, self._scale,
                             DIFFICULTY_LEVEL[1])
            self.deck.hide()
            self.grid.restore(self.deck, CUSTOM_CARD_INDICIES)
        elif self._none_in_clicked() == None:
            # If we have three cards selected, test for a match.
            self._test_for_a_match()
            if self._matches_on_display:
                self._smiley[-1].spr.set_layer(100)
                _logger.debug('Found a match')
            elif self._failure is not None:
                self._frowny[self._failure].spr.set_layer(100)
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
                _logger.debug('WARNING: No room in clicked')
                self.last_click = None
                return
            self.clicked[i].spr = spr
            self.clicked[i].pos = pos
            self.last_click = i

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
            self.set_label('deck', '')
            self.set_label('clock', '')
            self.set_label('status', '%s (%d:%02d)' %
                (_('Game over'), int(self.total_time / 60),
                 int(self.total_time % 60)))
            for i in range((ROW - 1) * COL):
                if self.grid.grid[i] == None:
                    self._smiley[i].show_card()
            self.match_timeout_id = gobject.timeout_add(
                2000, self._show_matches, 0)
            return True
        elif self.grid.cards_in_grid() == DEAL + 3 \
                and not self._find_a_match():
            self.set_label('deck', '')
            self.set_label('clock', '')
            self.set_label('status', _('unsolvable'))
            return True
        return False

    def _test_for_a_match(self):
        ''' If we have a match, then we have work to do. '''
        if self._match_check([self.deck.spr_to_card(self.clicked[0].spr),
                              self.deck.spr_to_card(self.clicked[1].spr),
                              self.deck.spr_to_card(self.clicked[2].spr)],
                             self.card_type):

            # Stop the timer.
            if hasattr(self, 'timeout_id'):
                if self.timeout_id is not None:
                    gobject.source_remove(self.timeout_id)
                self.total_time += gobject.get_current_time() - self.start_time

            # Increment the match counter and add the match to the match list.
            self.matches += 1
            for c in self.clicked:
                self.match_list.append(c.spr)
            self._matches_on_display = True

            # Test to see if the game is over.
            if self._game_over():
                if hasattr(self, 'timeout_id'):
                    gobject.source_remove(self.timeout_id)
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
                # Wait a few seconds before dealing new cards.
                gobject.timeout_add(2000, self._deal_new_cards)

            # Keep playing.
            self._update_labels()
            self._timer_reset()

        else:
            self._matches_on_display = False

    def _auto_increase_difficulty(self):
        ''' Auto advance levels '''
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

    def _deal_new_cards(self):
        ''' Deal three new cards. '''
        self.grid.replace(self.clicked, self.deck)
        self.set_label('deck', '%d %s' %
                       (self.deck.cards_remaining(), _('cards')))
        # Consolidate the grid.
        self.grid.consolidate()
        # Test to see if we need to deal extra cards.
        if not self._find_a_match():
            self.grid.deal_extra_cards(self.deck)

    def _keypress_cb(self, area, event):
        ''' Keypress: editing word cards or selecting cards to play '''
        k = gtk.gdk.keyval_name(event.keyval)
        u = gtk.gdk.keyval_to_unicode(event.keyval)
        if self.editing_word_list and self._edit_card is not None:
            if k in NOISE_KEYS:
                self._dead_key = None
                return True
            if k[0:5] == 'dead_':
                self._dead_key = k
                return True
            label = self._edit_card.spr.labels[0]
            if len(label) > 0:
                c = label.count(CURSOR)
                if c == 0:
                    oldleft = label
                    oldright = ''
                elif len(label) == 1:  # Only CURSOR
                    oldleft = ''
                    oldright = ''
                else:
                    try:  # Why are getting a ValueError on occasion?
                        oldleft, oldright = label.split(CURSOR)
                    except ValueError:
                        oldleft = label
                        oldright = ''
            else:
                oldleft = ''
                oldright = ''
            newleft = oldleft
            if k == 'BackSpace':
                if len(oldleft) > 1:
                    newleft = oldleft[:len(oldleft) - 1]
                else:
                    newleft = ''
            elif k == 'Delete':
                if len(oldright) > 0:
                    oldright = oldright[1:]
            elif k == 'Home':
                oldright = oldleft + oldright
                newleft = ''
            elif k == 'Left':
                if len(oldleft) > 0:
                    oldright = oldleft[len(oldleft) - 1:] + oldright
                    newleft = oldleft[:len(oldleft) - 1]
            elif k == 'Right':
                if len(oldright) > 0:
                    newleft = oldleft + oldright[0]
                    oldright = oldright[1:]
            elif k == 'End':
                newleft = oldleft + oldright
                oldright = ''
            elif k == 'Return':
                newleft = oldleft + RETURN
            else:
                if self._dead_key is not None:
                    u = DEAD_DICTS[DEAD_KEYS.index(self._dead_key[5:])][k]
                if k in WHITE_SPACE:
                    u = 32
                if unichr(u) != '\x00':
                    newleft = oldleft + unichr(u)
                else:
                    newleft = oldleft + k
            label = newleft + CURSOR + oldright
            self._edit_card.spr.set_label(label)
            (i, j) = WORD_CARD_MAP[self._edit_card.index]
            self.word_lists[i][j] = label.replace(CURSOR, '')
            self._dead_key = None
        else:
            if k in KEYMAP:
                self.process_selection(self.grid.grid_to_spr(KEYMAP.index(k)))
        return True

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
        gtk.main_quit()

    def _update_labels(self):
        ''' Write strings to a label in the toolbar. '''
        self.set_label('deck', '%d %s' %
            (self.deck.cards_remaining(), _('cards')))
        self.set_label('status', '')
        if self.matches == 1:
            if self.robot_matches > 0:
                self.set_label('match', '%d (%d) %s' % (
                    self.matches - self.robot_matches, self.robot_matches,
                    _('match')))
            else:
                self.set_label('match', '%d %s' % (self.matches, _('match')))
        else:
            if self.robot_matches > 0:
                self.set_label('match', '%d (%d) %s' % (
                    self.matches - self.robot_matches, self.robot_matches,
                    _('matches')))
            else:
                self.set_label('match', '%d %s' % (self.matches, _('matches')))

    def set_label(self, label, s):
        ''' Update the toolbar labels '''
        if self._sugar:
            if label == 'deck':
                self.activity.deck_label.set_text(s)
            elif label == 'status':
                self.activity.status_label.set_text(s)
            elif label == 'clock':
                self.activity.clock_label.set_text(s)
            elif label == 'match':
                self.activity.match_label.set_text(s)
        else:
            if hasattr(self, 'win') and label is not 'clock':
                #TRANS: Please translate Visual Match as Dimensions
                self.win.set_title('%s: %s' % (_('Visual Match'), s))

    def _restore_clicked(self, saved_selected_indices):
        ''' Restore the selected cards upon resume or share. '''
        j = 0
        for i in saved_selected_indices:
            if i is None:
                self.clicked[j].reset()
            else:
                self.clicked[j].spr = self.deck.index_to_card(i).spr
                k = self.grid.spr_to_grid(self.clicked[j].spr)
                self.clicked[j].spr.move(self.grid.match_to_xy(j))
                self.clicked[j].pos = self.grid.match_to_xy(j)
                self.clicked[j].spr.set_layer(2000)
            j += 1
        self.process_selection(None)

    def _restore_matches(self, saved_match_list_indices):
        ''' Restore the match list upon resume or share. '''
        j = 0
        self.match_list = []
        for i in saved_match_list_indices:
            if i is not None:
                self.match_list.append(self.deck.index_to_card(i).spr)
        '''
        if self.matches > 0:
            l = len(self.match_list)
            for j in range(3):
                self.grid.display_match(self.match_list[l - 3 + j], j)
            self._matches_on_display = True
        '''

    def _restore_word_list(self, saved_word_list):
        ''' Restore the word list upon resume or share. '''
        if len(saved_word_list) == 9:
            for i in range(3):
                for j in range(3):
                    self.word_lists[i][j] = saved_word_list[i * 3 + j]

    def _counter(self):
        ''' Display of seconds since start_time. '''
        seconds = int(gobject.get_current_time() - self.start_time)
        self.set_label('clock', str(seconds))
        if self.robot and self.robot_time < seconds:
            self._find_a_match(robot_match=True)
        else:
            self.timeout_id = gobject.timeout_add(1000, self._counter)

    def _timer_reset(self):
        ''' Reset the timer for the robot '''
        self.start_time = gobject.get_current_time()
        self.timeout_id = None
        self._counter()

    def _show_matches(self, i):
        ''' Show all the matches as a simple animation. '''
        if i < self.matches:
            for j in range(3):
                self.grid.display_match(self.match_list[i * 3 + j], j)
            self.match_timeout_id = gobject.timeout_add(
                2000, self._show_matches, i + 1)

    def _find_a_match(self, robot_match=False):
        ''' Check to see whether there are any matches on the board. '''
        if robot_match:
            # Before robot finds a match: restore any cards in match area
            if self._matches_on_display:
                # And unselect clicked cards
                for c in self.clicked:
                    c.hide()
                self._smiley[-1].spr.hide()
                self._matches_on_display = False
            else:
                for j in range(3):
                    if self.clicked[j].spr is not None:
                        k = self.grid.xy_to_grid(self.clicked[j].pos)
                        self.clicked[j].spr.move(self.clicked[j].pos)
                        self.grid.grid[k] = self.deck.spr_to_card(
                            self.clicked[j].spr)
                        self.clicked[j].reset()

        a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        for i in Permutation(a):  # TODO: really should be combination
            cardarray = [self.grid.grid[i[0]],
                         self.grid.grid[i[1]],
                         self.grid.grid[i[2]]]
            if self._match_check(cardarray, self.card_type):
                if robot_match:
                    # Turn off any current animations
                    self.grid.stop_animation = True
                    # Wait to move robot match to match area
                    timeout = gobject.timeout_add(200, self._robot_match, i)
                return True
        return False

    def _robot_match(self, i):
        ''' Robot finds a match '''
        for j in range(3):
            self.clicked[j].spr = self.grid.grid[i[j]].spr
            self.grid.grid[i[j]].spr.move(
                self.grid.match_to_xy(j))
            self.grid.grid[i[j]] = None
        self.robot_matches += 1
        self._test_for_a_match()
        self._matches_on_display = True

    def _match_check(self, cardarray, card_type):
        ''' For each attribute, either it is the same or different. '''
        for a in cardarray:
            if a is None:
                return False

        if (cardarray[0].shape + cardarray[1].shape + cardarray[2].shape) % 3\
               != 0:
            self._failure = 0
            return False
        if (cardarray[0].color + cardarray[1].color + cardarray[2].color) % 3\
               != 0:
            self._failure = 1
            return False
        if (cardarray[0].fill + cardarray[1].fill + cardarray[2].fill) % 3\
               != 0:
            self._failure = 2
            return False
        # Special case: only check number when shapes are the same
        if card_type == 'word':
            if cardarray[0].shape == cardarray[1].shape and \
                  cardarray[0].shape == cardarray[2].shape and \
                  (cardarray[0].num + cardarray[1].num + cardarray[2].num) % 3\
                  != 0:
                return False
        else:
            if (cardarray[0].num + cardarray[1].num + cardarray[2].num) % 3\
                   != 0:
                self._failure = 3
                return False
        return True

    def _choose_custom_card(self):
        ''' Select a custom card from the Journal '''
        chooser = None
        name = None
        if hasattr(mime, 'GENERIC_TYPE_IMAGE'):
            # See #2398
            if 'image/svg+xml' not in \
                    mime.get_generic_type(mime.GENERIC_TYPE_IMAGE).mime_types:
                mime.get_generic_type(
                    mime.GENERIC_TYPE_IMAGE).mime_types.append('image/svg+xml')
            chooser = ObjectChooser(parent=self.activity,
                                    what_filter=mime.GENERIC_TYPE_IMAGE)
        else:
            try:
                chooser = ObjectChooser(parent=self, what_filter=None)
            except TypeError:
                chooser = ObjectChooser(None, self.activity,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)

        if chooser is not None:
            try:
                result = chooser.run()
                if result == gtk.RESPONSE_ACCEPT:
                    jobject = chooser.get_selected_object()
                    if jobject and jobject.file_path:
                        name = jobject.metadata['title']
                        mime_type = jobject.metadata['mime_type']
                        _logger.debug('result of choose: %s (%s)' % \
                                          (name, str(mime_type)))
            finally:
                chooser.destroy()
                del chooser

            if name is not None:
                self._find_custom_paths(jobject)

    def _find_custom_paths(self, jobject):
        ''' Associate a Journal object with a card '''
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
        self.activity.button_custom.set_icon('new-custom-game')
        self.activity.button_custom.set_tooltip(_('New custom game'))
        return

    def help_animation(self):
        ''' Simple explanatory animation at start of play '''
        self._help_index = 0
        self._stop_help = False
        self._help[self._help_index].set_layer(5000)
        self._help_timeout_id = gobject.timeout_add(2000, self._help_next)

    def _help_next(self):
        ''' Load the next frame in the animation '''
        self._help[self._help_index].hide()
        if self._stop_help:
            return
        self._help_index += 1
        self._help_index %= len(self._help)
        self._help[self._help_index].set_layer(5000)
        if self._help_index in [0, 9, 10, 20, 21]:
            self._help_timeout_id = gobject.timeout_add(2000, self._help_next)
        else:
            self._help_timeout_id = gobject.timeout_add(1000, self._help_next)


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
    pl = gtk.gdk.PixbufLoader('svg')
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
