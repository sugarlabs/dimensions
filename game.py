# -*- coding: utf-8 -*-
#Copyright (c) 2009,10 Walter Bender
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

from gettext import gettext as _

from sugar.graphics.objectchooser import ObjectChooser
from sugar.datastore import datastore
from sugar import mime

import logging
_logger = logging.getLogger('visualmatch-activity')

try:
    from sugar.graphics import style
    GRID_CELL_SIZE = style.GRID_CELL_SIZE
except ImportError:
    GRID_CELL_SIZE = 0

from constants import LOW, MEDIUM, HIGH, SELECTMASK, MATCHMASK, ROW, COL, \
    WORD_CARD_INDICIES, MATCH_POSITION, DEAD_DICTS, DEAD_KEYS, WHITE_SPACE, \
    NOISE_KEYS, WORD_CARD_MAP, KEYMAP, CARD_HEIGHT, CARD_WIDTH, DEAL, \
    DIFFICULTY_LEVEL, BACKGROUNDMASK, DECKSIZE, CUSTOM_CARD_INDICIES

from grid import Grid
from deck import Deck
from card import Card
from sprites import Sprites, Sprite
from gencards import generate_selected_card, generate_match_card, \
    generate_smiley


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


class Game():
    ''' The game play -- called from within Sugar or GNOME '''

    def __init__(self, canvas, path, parent=None):
        ''' Initialize the playing surface '''
        self.path = path
        self.activity = parent

        if parent is None:  # Starting from command line
            self.sugar = False
            self.canvas = canvas
        else:               # Starting from Sugar
            self.sugar = True
            self.canvas = canvas
            parent.show_all()

        self.canvas.set_flags(gtk.CAN_FOCUS)
        self.canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.canvas.connect('expose-event', self._expose_cb)
        self.canvas.connect('button-press-event', self._button_press_cb)
        self.canvas.connect('button-release-event', self._button_release_cb)
        self.canvas.connect('key_press_event', self._keypress_cb)
        self.width = gtk.gdk.screen_width()
        self.height = gtk.gdk.screen_height() - GRID_CELL_SIZE
        self.scale = 0.8 * self.height / (CARD_HEIGHT * 5.5)
        self.card_width = CARD_WIDTH * self.scale
        self.card_height = CARD_HEIGHT * self.scale
        self.custom_paths = [None, None, None, None, None, None, None, None,
                             None]
        self.sprites = Sprites(self.canvas)
        self.selected = []
        self.match_display_area = []
        self.smiley = None
        self.clicked = [None, None, None]
        self.low_score = [-1, -1, -1]
        self.robot = False
        self.numberC = 0
        self.numberO = 0
        self.word_lists = None
        self.editing_word_list = False
        self.editing_custom_cards = False
        self.edit_card = None
        self.dead_key = None

    def new_game(self, saved_state=None, deck_index=0):
        ''' Start a new game '''
        # If we were editing the word list, time to stop
        self.editing_word_list = False
        self.editing_custom_cards = False
        self.edit_card = None

        # If there is already a deck, hide it.
        if hasattr(self, 'deck'):
            self.deck.hide()

        # The first time through, initialize the grid, and overlays.
        if not hasattr(self, 'grid'):
            self.grid = Grid(self.width, self.height, self.card_width,
                             self.card_height)

            for i in range(0, 3):
                self.selected.append(Card(self.sprites,
                                          generate_selected_card(self.scale),
                                          [SELECTMASK, 0, 0, 0]))
                self.match_display_area.append(Card(self.sprites,
                                          generate_match_card(self.scale),
                                          [MATCHMASK, 0, 0, 0]))
                self.grid.display_match(self.match_display_area[i].spr, i)

            self.smiley = Card(self.sprites, generate_smiley(self.scale),
                               [BACKGROUNDMASK, 0, 0, 0])
            self.smiley.spr.move((self.width / 2 - \
                                      self.smiley.spr.rect.width / 2,
                                  self.height / 2 -\
                                      self.smiley.spr.rect.height / 2))
        self._unselect()

        # Restore saved state on resume or share.
        if not hasattr(self, 'card_type'):
            return
        if saved_state is not None:
            _logger.debug('Restoring state: %s' % (str(saved_state)))
            if self.card_type == 'custom':
                self.deck = Deck(self.sprites, self.card_type,
                             [self.numberO, self.numberC], self.custom_paths,
                             self.scale, DIFFICULTY_LEVEL[self.level])
            else:
                self.deck = Deck(self.sprites, self.card_type,
                             [self.numberO, self.numberC], self.word_lists,
                             self.scale, DIFFICULTY_LEVEL[self.level])
            self.deck.hide()
            self.deck.index = deck_index
            _deck_start = ROW * COL + 3
            _deck_stop = _deck_start + self.deck.count()
            self._restore_word_list(saved_state[_deck_stop + \
                                                    3 * self.matches:])
            self.deck.restore(saved_state[_deck_start: _deck_stop])
            self.grid.restore(self.deck, saved_state[0: ROW * COL])
            self._restore_selected(saved_state[ROW * COL: ROW * COL + 3])
            self._restore_matches(saved_state[_deck_stop: _deck_stop + \
                                                  3 * self.matches])
        elif not self.joiner():
            _logger.debug('Starting new game.')
            if self.card_type == 'custom':
                self.deck = Deck(self.sprites, self.card_type,
                                 [self.numberO, self.numberC],
                                 self.custom_paths, self.scale,
                                 DIFFICULTY_LEVEL[self.level])
            else:
                self.deck = Deck(self.sprites, self.card_type,
                                 [self.numberO, self.numberC], self.word_lists,
                                 self.scale, DIFFICULTY_LEVEL[self.level])
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

        self.smiley.hide_card()

    def _sharing(self):
        ''' Are we sharing? '''
        if self.sugar and hasattr(self.activity, 'chattube') and \
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
        self.deck.hide()
        self.card_type = 'custom'
        if len(self.custom_paths) < 3:
            for i in range(len(self.custom_paths), 81):
                self.custom_paths.append(None)
        self.deck = Deck(self.sprites, self.card_type,
                         [self.numberO, self.numberC],
                         self.custom_paths,
                         self.scale, DIFFICULTY_LEVEL.index(HIGH))
        self.deck.hide()
        self._unselect()
        self.matches = 0
        self.robot_matches = 0
        self.match_list = []
        self.total_time = 0
        self.edit_card = None
        self.dead_key = None
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
        self.deck.hide()
        self.card_type = 'word'
        self.deck = Deck(self.sprites, self.card_type,
                         [self.numberO, self.numberC], self.word_lists,
                         self.scale, DIFFICULTY_LEVEL.index(HIGH))
        self.deck.hide()
        self._unselect()
        self.matches = 0
        self.robot_matches = 0
        self.match_list = []
        self.total_time = 0
        self.edit_card = None
        self.dead_key = None
        if hasattr(self, 'timeout_id') and self.timeout_id is not None:
            gobject.source_remove(self.timeout_id)
        # Fill the grid with word cards.
        self.grid.restore(self.deck, WORD_CARD_INDICIES)
        self.set_label('deck', '')
        self.set_label('match', '')
        self.set_label('clock', '')
        self.set_label('status', _('Edit the word cards.'))

    def _button_press_cb(self, win, event):
        ''' Just grab focus on press. '''
        win.grab_focus()
        return True

    def _button_release_cb(self, win, event):
        ''' Select the sprite under the mouse and process the selection. '''
        win.grab_focus()
        x, y = map(int, event.get_coords())
        spr = self.sprites.find_sprite((x, y))
        if spr is None:
            return True
        if self._sharing():
            if self.deck.spr_to_card(spr) is not None:
                self.activity._send_event(
                    'B:' + str(self.deck.spr_to_card(spr).index))
            i = self._selected(spr)
            if i is not -1:
                self.activity._send_event('S:' + str(i))
        return self._process_selection(spr)

    def _selected(self, spr):
        ''' Mark the selected card '''
        for i in range(3):
            if self.selected[i].spr == spr:
                return i
        return -1

    def _process_selection(self, spr):
        ''' Check for matches '''
        # Make sure a card in the matched pile isn't selected.
        x, y = spr.get_xy()
        if x == MATCH_POSITION:
            return True

        # Make sure that the current card isn't already selected.
        i = self._selected(spr)
        if i is not -1:
            # On a second click, unselect it.
            self.clicked[i] = None
            self.selected[i].hide_card()
            return True

        # Otherwise highlight the card with a selection mask.
        for a in self.clicked:
            if a is None:
                i = self.clicked.index(a)
                self.clicked[i] = spr
                x, y = spr.get_xy()
                self.selected[i].spr.move((x, y))
                self.selected[i].show_card()
                break

        _logger.debug('selecting card %d' % (
                self.deck.cards.index(self.deck.spr_to_card(spr))))
        if self.editing_word_list:
            # Only edit one card at a time, so unselect other cards
            for a in self.clicked:
                if a is not None and a is not spr:
                    i = self.clicked.index(a)
                    self.clicked[i] = None
                    self.selected[i].hide_card()
            # Edit card label
            self.edit_card = self.deck.spr_to_card(spr)
        elif self.editing_custom_cards:
            # Only edit one card at a time, so unselect other cards
            for a in self.clicked:
                if a is not None and a is not spr:
                    i = self.clicked.index(a)
                    self.clicked[i] = None
                    self.selected[i].hide_card()
            # Choose an image from the Journal for a card
            self.edit_card = self.deck.spr_to_card(spr)
            self._choose_custom_card()
            # Regenerate the deck with the new card definitions
            self.deck = Deck(self.sprites, self.card_type,
                             [self.numberO, self.numberC],
                             self.custom_paths, self.scale,
                             DIFFICULTY_LEVEL[1])
            self.deck.hide()
            self.grid.restore(self.deck, CUSTOM_CARD_INDICIES)
        elif None not in self.clicked:
            # If we have three cards selected, test for a match.
            self._test_for_a_match()
        return True

    def _game_over(self):
        ''' Game is over when the deck is empty and no more matches. '''
        if self.deck.empty() and not self._find_a_match():
            self.set_label('deck', '')
            self.set_label('clock', '')
            self.set_label('status', '%s (%d:%02d)' %
                (_('Game over'), int(self.total_time / 60),
                 int(self.total_time % 60)))
            self.smiley.show_card()
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
        if self._match_check([self.deck.spr_to_card(self.clicked[0]),
                              self.deck.spr_to_card(self.clicked[1]),
                              self.deck.spr_to_card(self.clicked[2])],
                             self.card_type):

            # Stop the timer.
            if self.timeout_id is not None:
                gobject.source_remove(self.timeout_id)
            self.total_time += gobject.get_current_time() - self.start_time

            # Increment the match counter and add the match to the match list.
            self.matches += 1
            for i in self.clicked:
                self.match_list.append(i)

            # Remove the match and deal three new cards.
            self.grid.remove_and_replace(self.clicked, self.deck)
            self.set_label('deck', '%d %s' %
                           (self.deck.cards_remaining(), _('cards')))

            # Test to see if the game is over.
            if self._game_over():
                gobject.source_remove(self.timeout_id)
                self._unselect()
                if self.low_score[self.level] == -1:
                    self.low_score[self.level] = self.total_time
                elif self.total_time < self.low_score[self.level]:
                    self.low_score[self.level] = self.total_time
                    self.set_label('status', '%s (%d:%02d)' %
                        (_('New record'), int(self.total_time / 60),
                         int(self.total_time % 60)))
                if not self.sugar:
                    self.activity.save_score()
                return True

            # Consolidate the grid.
            self.grid.consolidate()

            # Test to see if we need to deal extra cards.
            if not self._find_a_match():
                self.grid.deal_extra_cards(self.deck)

            # Keep playing.
            self._update_labels()
            self._timer_reset()

        # Whether or not there was a match, unselect all cards.
        self._unselect()

    def _unselect(self):
        ''' Unselect the cards '''
        self.clicked = [None, None, None]
        for a in self.selected:
            a.hide_card()

    def _keypress_cb(self, area, event):
        ''' Keypress: editing word cards or selecting cards to play '''
        k = gtk.gdk.keyval_name(event.keyval)
        u = gtk.gdk.keyval_to_unicode(event.keyval)
        if self.editing_word_list and self.edit_card is not None:
            if k in NOISE_KEYS:
                self.dead_key = None
                return True
            if k[0:5] == 'dead_':
                self.dead_key = k
                return True
            if k == 'BackSpace':
                self.edit_card.spr.labels[0] =\
                self.edit_card.spr.labels[0][
                    :len(self.edit_card.spr.labels[0]) - 1]
            else:
                if self.dead_key is not None:
                    u = DEAD_DICTS[DEAD_KEYS.index(self.dead_key[5:])][k]
                if k in WHITE_SPACE:
                    u = 32
                if unichr(u) is not '\x00':
                    self.edit_card.spr.labels[0] += unichr(u)
            self.edit_card.spr.draw()
            (i, j) = WORD_CARD_MAP[self.edit_card.index]
            self.word_lists[i][j] = self.edit_card.spr.labels[0]
            self.dead_key = None
        else:
            if k in KEYMAP:
                return self._process_selection(
                           self.grid.grid_to_spr(KEYMAP.index(k)))
        return True

    def _expose_cb(self, win, event):
        ''' Callback to handle window expose events '''
        self.do_expose_event(event)
        return True

    # Handle the expose-event by drawing
    def do_expose_event(self, event):

        # Create the cairo context
        cr = self.canvas.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.clip()

        # Refresh sprite list
        self.sprites.redraw_sprites(cr=cr)

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
        if self.sugar:
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
                self.win.set_title('%s: %s' % (_('Visual Match'), s))

    def _restore_selected(self, saved_selected_indices):
        ''' Restore the selected cards upon resume or share. '''
        j = 0
        for i in saved_selected_indices:
            if i is None:
                self.clicked[j] = None
            else:
                self.clicked[j] = self.deck.index_to_card(i).spr
                k = self.grid.spr_to_grid(self.clicked[j])
                self.selected[j].spr.move((self.grid.grid_to_xy(k)[0],
                                           self.grid.grid_to_xy(k)[1]))
                self.selected[j].show_card()
            j += 1

    def _restore_matches(self, saved_match_list_indices):
        ''' Restore the match list upon resume or share. '''
        j = 0
        self.match_list = []
        for i in saved_match_list_indices:
            if i is not None:
                self.match_list.append(self.deck.index_to_card(i).spr)
        if self.matches > 0:
            l = len(self.match_list)
            for j in range(3):
                self.grid.display_match(self.match_list[l - 3 + j], j)

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
            self._find_a_match(True)
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
            self.match_timeout_id = gobject.timeout_add(2000,
                                                        self._show_matches,
                                                        i + 1)

    def _find_a_match(self, robot_match=False):
        ''' Check to see whether there are any matches on the board. '''
        a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        for i in Permutation(a):  # TODO: really should be combination
            cardarray = [self.grid.grid[i[0]],
                         self.grid.grid[i[1]],
                         self.grid.grid[i[2]]]
            if self._match_check(cardarray, self.card_type):
                if robot_match:
                    for j in range(3):
                        self.clicked[j] = self.grid.grid[i[j]].spr
                    self.robot_matches += 1
                    self._test_for_a_match()
                return True
        return False

    def _match_check(self, cardarray, card_type):
        ''' For each attribute, either it is the same or different. '''
        for a in cardarray:
            if a is None:
                return False

        if (cardarray[0].shape + cardarray[1].shape + cardarray[2].shape) % 3\
               != 0:
            return False
        if (cardarray[0].color + cardarray[1].color + cardarray[2].color) % 3\
               != 0:
            return False
        if (cardarray[0].fill + cardarray[1].fill + cardarray[2].fill) % 3\
               != 0:
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
                _logger.debug('%d' % nobjects)
                self.custom_paths = []
                if nobjects > 0:
                    for j in range(DECKSIZE):
                        for i in range(nobjects):
                            if dsobjects[i].metadata['title'] == \
                                    _construct_a_name(basename, j + 1, suffix):
                                _logger.debug('result of find: %s' % \
                                              dsobjects[i].metadata['title'])
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
            grid_index = self.grid.spr_to_grid(self.edit_card.spr)
            _logger.debug('editing card %d' % (grid_index))
            self.custom_paths[grid_index] = jobject
            self.activity.metadata['custom_' + str(grid_index)] = \
                jobject.object_id

        self.card_type = 'custom'
        self.activity.button_custom.set_icon('new-custom-game')
        self.activity.button_custom.set_tooltip(_('New custom game'))
        return


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
