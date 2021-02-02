# Copyright (c) 2009-14 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301  USA

import os

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('TelepathyGLib', '0.12')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib

from sugar3.activity import activity
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics.menuitem import MenuItem
from sugar3.graphics.alert import NotifyAlert, Alert
from sugar3.graphics import style
from sugar3.graphics.icon import Icon
from sugar3.graphics.xocolor import XoColor
from sugar3.datastore import datastore
from sugar3 import profile

from gi.repository import TelepathyGLib
CHANNEL_TYPE_TUBES = TelepathyGLib.IFACE_CHANNEL_TYPE_TUBES
CHANNEL_INTERFACE_GROUP = TelepathyGLib.IFACE_CHANNEL_INTERFACE_GROUP
TUBE_TYPE_DBUS = TelepathyGLib.IFACE_CHANNEL_TYPE_DBUS_TUBE
LOCAL_PENDING = TelepathyGLib.TubeState.LOCAL_PENDING


from dbus.service import signal
from dbus.gi_service import ExportedGObject
from sugar3.presence import presenceservice
from sugar3.presence.tubeconn import TubeConnection

from gettext import gettext as _
import logging
_logger = logging.getLogger('dimensions-activity')

from json import dump as jdump
from json import dumps as jdumps
from json import loads as jloads

from io import StringIO

from toolbar_utils import (radio_factory, button_factory, separator_factory)

from constants import (DECKSIZE, PRODUCT, HASH, ROMAN, WORD, CHINESE, MAYAN,
                       INCAN, DOTS, STAR, DICE, LINES)

from game import Game
from collabwrapper import CollabWrapper

MODE = 'pattern'

help_palettes = {}

BEGINNER = 0
INTERMEDIATE = 1
EXPERT = 2
LEVEL_LABELS = [_('beginner'), _('intermediate'), _('expert')]
LEVEL_DECKSIZE = [DECKSIZE / 3, DECKSIZE, DECKSIZE / 9]

NUMBER_O_BUTTONS = {}
NUMBER_C_BUTTONS = {}
LEVEL_BUTTONS = {}

SERVICE = 'org.sugarlabs.Dimensions'
IFACE = SERVICE
PATH = '/org/augarlabs/Dimensions'

PROMPT_DICT = {'pattern': _('New pattern game'),
               'number': _('New number game'),
               'word': _('New word game'),
               'custom': _('Import custom cards')}

ROBOT_TIMER_VALUES = [15, 30, 60, 120, 300]
ROBOT_TIMER_LABELS = {15: _('15 seconds'), 30: _('30 seconds'),
                      60: _('1 minute'), 120: _('2 minutes'),
                      300: _('5 minutes')}
ROBOT_TIMER_DEFAULT = 15


class Dimensions(activity.Activity):

    ''' Dimension matching game '''

    def __init__(self, handle):
        ''' Initialize the Sugar activity '''
        super(Dimensions, self).__init__(handle)
        self.ready_to_play = False
        self.initiating = False
        self._prompt = ''
        self._read_journal_data()
        self._sep = []
        self._setup_toolbars()
        self._setup_canvas()
        self.connect('shared', self._shared_cb)

        if not hasattr(self, '_saved_state'):
            self._saved_state = None
            self.vmw.new_game(show_selector=True)
        else:
            self.vmw.new_game(saved_state=self._saved_state,
                              deck_index=self._deck_index)
        self.ready_to_play = True

        if self._editing_word_list:
            self.vmw.editing_word_list = True
            self.vmw.edit_word_list()
        elif self._editing_custom_cards:
            self.vmw.editing_custom_cards = True
            self.vmw.edit_custom_card()

        Gdk.Screen.get_default().connect('size-changed', self._configure_cb)
        self._configure_cb(None)

        self._collab = CollabWrapper(self)
        self._collab.buddy_joined.connect(self._buddy_joined_cb)
        self._collab.buddy_left.connect(self._buddy_left_cb)
        self._collab.joined.connect(self._joined_cb)
        self._collab.message.connect(self._message_cb)
        self._collab.setup()

    def get_data(self):
        return None

    def set_data(self, data):
        pass

    def _select_game_cb(self, button, card_type):
        ''' Choose which game we are playing. '''
        if self.vmw.joiner():  # joiner cannot change level
            return
        self._prompt = PROMPT_DICT[card_type]
        self._load_new_game(card_type)

    def _load_new_game(self, card_type=None, show_selector=True):
        if not self.ready_to_play:
            return

        # self._notify_new_game(self._prompt)
        GLib.idle_add(self._new_game, card_type, show_selector)

    def _new_game(self, card_type, show_selector=True):
        if card_type == 'custom' and self.vmw.custom_paths[0] is None:
            self.image_import_cb()
        else:
            self.tools_toolbar_button.set_expanded(False)
            self.vmw.new_game(show_selector=show_selector)

    def _robot_cb(self, button=None):
        ''' Toggle robot assist on/off '''
        if self.vmw.robot:
            self.vmw.robot = False
            self.robot_button.set_tooltip(_('Play with the computer.'))
            self.robot_button.set_icon_name('robot-off')
        elif not self.vmw.editing_word_list:
            self.vmw.robot = True
            self.robot_button.set_tooltip(
                _('Stop playing with the computer.'))
            self.robot_button.set_icon_name('robot-on')

    def _level_cb(self, button, level):
        ''' Cycle between levels '''
        if self.vmw.joiner():  # joiner cannot change level
            return
        self.vmw.level = level
        # self.level_label.set_text(self.calc_level_label(self.vmw.low_score,
        #                                                 self.vmw.level))
        self._load_new_game(show_selector=False)

    def calc_level_label(self, low_score, play_level):
        ''' Show the score. '''
        if low_score[play_level] == -1:
            return LEVEL_LABELS[play_level]
        else:
            return '%s (%d:%02d)' % \
                (LEVEL_LABELS[play_level],
                 int(low_score[play_level] / 60),
                 int(low_score[play_level] % 60))

    def image_import_cb(self, button=None):
        ''' Import custom cards from the Journal '''
        self.vmw.editing_custom_cards = True
        self.vmw.editing_word_list = False
        self.vmw.edit_custom_card()
        if self.vmw.robot:
            self._robot_cb(button)

    def _number_card_O_cb(self, button, numberO):
        ''' Choose between O-card list for numbers game. '''
        if self.vmw.joiner():  # joiner cannot change decks
            return
        self.vmw.numberO = numberO
        self.vmw.card_type = 'number'
        self._load_new_game()

    def _number_card_C_cb(self, button, numberC):
        ''' Choose between C-card list for numbers game. '''
        if self.vmw.joiner():  # joiner cannot change decks
            return
        self.vmw.numberC = numberC
        self.vmw.card_type = 'number'
        self._load_new_game()

    def _edit_words_cb(self, button):
        ''' Edit the word list. '''
        self.vmw.editing_word_list = True
        self.vmw.editing_custom_cards = False
        self.vmw.edit_word_list()
        if self.vmw.robot:
            self._robot_cb(button)

    def _read_metadata(self, keyword, default_value, json=False):
        ''' If the keyword is found, return stored value '''
        if keyword in self.metadata:
            data = self.metadata[keyword]
        else:
            data = default_value

        if json:
            try:
                return jloads(data)
            except:
                pass

        return data

    def _read_journal_data(self):
        ''' There may be data from a previous instance. '''
        self._play_level = int(self._read_metadata('play_level', 0))
        self._robot_time = int(self._read_metadata('robot_time',
                                                   ROBOT_TIMER_DEFAULT))
        self._card_type = self._read_metadata('cardtype', MODE)
        self._low_score = [int(self._read_metadata('low_score_beginner', -1)),
                           int(self._read_metadata('low_score_intermediate',
                                                   -1)),
                           int(self._read_metadata('low_score_expert', -1))]

        self._all_scores = self._read_metadata(
            'all_scores',
            '{"pattern": [], "word": [], "number": [], "custom": []}',
            True)
        self._numberO = int(self._read_metadata('numberO', PRODUCT))
        self._numberC = int(self._read_metadata('numberC', HASH))
        self._matches = int(self._read_metadata('matches', 0))
        self._robot_matches = int(self._read_metadata('robot_matches', 0))
        self._total_time = int(self._read_metadata('total_time', 0))
        self._deck_index = int(self._read_metadata('deck_index', 0))
        self._word_lists = [[self._read_metadata('mouse', _('mouse')),
                             self._read_metadata('cat', _('cat')),
                             self._read_metadata('dog', _('dog'))],
                            [self._read_metadata('cheese', _('cheese')),
                             self._read_metadata('apple', _('apple')),
                             self._read_metadata('bread', _('bread'))],
                            [self._read_metadata('moon', _('moon')),
                             self._read_metadata('sun', _('sun')),
                             self._read_metadata('earth', _('earth'))]]
        self._editing_word_list = bool(int(self._read_metadata(
            'editing_word_list', 0)))
        self._editing_custom_cards = bool(int(self._read_metadata(
            'editing_custom_cards', 0)))
        if self._card_type == 'custom':
            self._custom_object = self._read_metadata('custom_object', None)
            if self._custom_object is None:
                self._card_type = MODE
        self._custom_jobject = []
        for i in range(9):
            self._custom_jobject.append(self._read_metadata(
                'custom_' + str(i), None))

    def _write_scores_to_clipboard(self, button=None):
        ''' SimpleGraph will plot the cululative results '''
        jscores = ''
        c = 0
        for key in list(self.vmw.all_scores.keys()):
            for data in self.vmw.all_scores[key]:
                jscores += '%s: %s\n' % (str(c + 1), data[1])
                c += 1
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(jscores, -1)

    def _setup_toolbars(self):
        ''' Setup the toolbars.. '''

        tools_toolbar = Gtk.Toolbar()
        numbers_toolbar = Gtk.Toolbar()
        toolbox = ToolbarBox()

        self.activity_toolbar_button = ActivityToolbarButton(self)

        toolbox.toolbar.insert(self.activity_toolbar_button, 0)
        self.activity_toolbar_button.show()

        self.numbers_toolbar_button = ToolbarButton(
            page=numbers_toolbar,
            icon_name='number-tools')
        if MODE == 'number':
            numbers_toolbar.show()
            toolbox.toolbar.insert(self.numbers_toolbar_button, -1)
            self.numbers_toolbar_button.show()

        self.tools_toolbar_button = ToolbarButton(
            page=tools_toolbar,
            icon_name='view-source')

        self.button_pattern = button_factory(
            'new-pattern-game', toolbox.toolbar, self._select_game_cb,
            cb_arg='pattern', tooltip=_('New game'))

        self._set_extras(toolbox.toolbar)

        self._sep.append(separator_factory(toolbox.toolbar, True, False))

        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>q'
        toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()

        button_factory('score-copy', self.activity_toolbar_button,
                       self._write_scores_to_clipboard,
                       tooltip=_('Export scores to clipboard'))

        self.set_toolbar_box(toolbox)
        toolbox.show()

        if MODE == 'word':
            self.words_tool_button = button_factory(
                'word-tools', tools_toolbar, self._edit_words_cb,
                tooltip=_('Edit word lists.'))

        self.import_button = button_factory(
            'image-tools', tools_toolbar, self.image_import_cb,
            tooltip=_('Import custom cards'))

        self.button_custom = button_factory(
            'new-custom-game', tools_toolbar, self._select_game_cb,
            cb_arg='custom', tooltip=_('New custom game'))
        self.button_custom.set_sensitive(False)

        if MODE == 'number':
            self._setup_number_buttons(numbers_toolbar)

    def _setup_number_buttons(self, numbers_toolbar):
        self.product_button = radio_factory(
            'product',
            numbers_toolbar,
            self._number_card_O_cb,
            cb_arg=PRODUCT,
            tooltip=_('product'),
            group=None)
        NUMBER_O_BUTTONS[PRODUCT] = self.product_button
        self.roman_button = radio_factory(
            'roman',
            numbers_toolbar,
            self._number_card_O_cb,
            cb_arg=ROMAN,
            tooltip=_('Roman numerals'),
            group=self.product_button)
        NUMBER_O_BUTTONS[ROMAN] = self.roman_button
        self.word_button = radio_factory(
            'word',
            numbers_toolbar,
            self._number_card_O_cb,
            cb_arg=WORD,
            tooltip=_('word'),
            group=self.product_button)
        NUMBER_O_BUTTONS[WORD] = self.word_button
        self.chinese_button = radio_factory(
            'chinese',
            numbers_toolbar,
            self._number_card_O_cb,
            cb_arg=CHINESE,
            tooltip=_('Chinese'),
            group=self.product_button)
        NUMBER_O_BUTTONS[CHINESE] = self.chinese_button
        self.mayan_button = radio_factory(
            'mayan',
            numbers_toolbar,
            self._number_card_O_cb,
            cb_arg=MAYAN,
            tooltip=_('Mayan'),
            group=self.product_button)
        NUMBER_O_BUTTONS[MAYAN] = self.mayan_button
        self.incan_button = radio_factory(
            'incan',
            numbers_toolbar,
            self._number_card_O_cb,
            cb_arg=INCAN,
            tooltip=_('Quipu'),
            group=self.product_button)
        NUMBER_O_BUTTONS[INCAN] = self.incan_button

        separator_factory(numbers_toolbar, False, True)

        self.hash_button = radio_factory(
            'hash',
            numbers_toolbar,
            self._number_card_C_cb,
            cb_arg=HASH,
            tooltip=_('hash marks'),
            group=None)
        NUMBER_C_BUTTONS[HASH] = self.hash_button
        self.dots_button = radio_factory(
            'dots',
            numbers_toolbar,
            self._number_card_C_cb,
            cb_arg=DOTS,
            tooltip=_('dots in a circle'),
            group=self.hash_button)
        NUMBER_C_BUTTONS[DOTS] = self.dots_button
        self.star_button = radio_factory(
            'star',
            numbers_toolbar,
            self._number_card_C_cb,
            cb_arg=STAR,
            tooltip=_('points on a star'),
            group=self.hash_button)
        NUMBER_C_BUTTONS[STAR] = self.star_button
        self.dice_button = radio_factory(
            'dice',
            numbers_toolbar,
            self._number_card_C_cb,
            cb_arg=DICE,
            tooltip=_('dice'),
            group=self.hash_button)
        NUMBER_C_BUTTONS[DICE] = self.dice_button
        self.lines_button = radio_factory(
            'lines',
            numbers_toolbar,
            self._number_card_C_cb,
            cb_arg=LINES,
            tooltip=_('dots in a line'),
            group=self.hash_button)
        NUMBER_C_BUTTONS[LINES] = self.lines_button

    def _configure_cb(self, event):
        self._vbox.set_size_request(Gdk.Screen.width(), Gdk.Screen.height())
        self._vbox.show()

        if Gdk.Screen.width() < Gdk.Screen.height():
            for sep in self._sep:
                sep.hide()
        else:
            for sep in self._sep:
                sep.show()

    def _robot_selection_cb(self, widget):
        if self._robot_palette:
            if not self._robot_palette.is_up():
                self._robot_palette.popup(immediate=True)
            else:
                self._robot_palette.popdown(immediate=True)
            return

    def _setup_robot_palette(self):
        self._robot_palette = self._robot_time_button.get_palette()

        self._robot_timer_menu = {}
        for seconds in ROBOT_TIMER_VALUES:
            self._robot_timer_menu[seconds] = {
                'menu_item': MenuItem(),
                'label': ROBOT_TIMER_LABELS[seconds],
                'icon': image_from_svg_file(
                    'timer-%d.svg' % (seconds)),
                'icon-selected': image_from_svg_file(
                    'timer-%d-selected.svg' % (seconds))
            }

            self._robot_timer_menu[seconds]['menu_item'].set_label(
                self._robot_timer_menu[seconds]['label'])
            if seconds == ROBOT_TIMER_DEFAULT:
                self._robot_timer_menu[seconds]['menu_item'].set_image(
                    self._robot_timer_menu[seconds]['icon-selected'])
            else:
                self._robot_timer_menu[seconds]['menu_item'].set_image(
                    self._robot_timer_menu[seconds]['icon'])
            self._robot_timer_menu[seconds]['menu_item'].connect(
                'activate', self._robot_selected_cb, seconds)
            self._robot_palette.menu.append(
                self._robot_timer_menu[seconds]['menu_item'])
            self._robot_timer_menu[seconds]['menu_item'].show()

    def _robot_selected_cb(self, button, seconds):
        self.vmw.robot_time = seconds
        if hasattr(self, '_robot_time_button') and \
                seconds in ROBOT_TIMER_VALUES:
            self._robot_time_button.set_icon_name('timer-%d' % seconds)

        for time in ROBOT_TIMER_VALUES:
            if time == seconds:
                self._robot_timer_menu[time]['menu_item'].set_image(
                    self._robot_timer_menu[time]['icon-selected'])
            else:
                self._robot_timer_menu[time]['menu_item'].set_image(
                    self._robot_timer_menu[time]['icon'])

    def _set_extras(self, toolbar):
        self.robot_button = button_factory(
            'robot-off', toolbar, self._robot_cb,
            tooltip=_('Play with the computer'))

        self._robot_time_button = button_factory(
            'timer-15',
            toolbar,
            self._robot_selection_cb,
            tooltip=_('robot pause time'))
        self._setup_robot_palette()

        self._sep.append(separator_factory(toolbar, False, True))

        self.beginner_button = radio_factory(
            'beginner',
            toolbar,
            self._level_cb,
            cb_arg=BEGINNER,
            tooltip=_('beginner'),
            group=None)
        LEVEL_BUTTONS[BEGINNER] = self.beginner_button
        self.intermediate_button = radio_factory(
            'intermediate',
            toolbar,
            self._level_cb,
            cb_arg=INTERMEDIATE,
            tooltip=_('intermediate'),
            group=self.beginner_button)
        LEVEL_BUTTONS[INTERMEDIATE] = self.intermediate_button
        self.expert_button = radio_factory(
            'expert',
            toolbar,
            self._level_cb,
            cb_arg=EXPERT,
            tooltip=_('expert'),
            group=self.beginner_button)
        LEVEL_BUTTONS[EXPERT] = self.expert_button

    def _fixed_resize_cb(self, widget=None, rect=None):
        ''' If a toolbar opens or closes, we need to resize the vbox
        holding out scrolling window. '''
        self._vbox.set_size_request(rect.width, rect.height)

    def _setup_canvas(self):
        ''' Create a canvas in a Gtk.Fixed '''
        self.fixed = Gtk.Fixed()
        self.fixed.connect('size-allocate', self._fixed_resize_cb)
        self.fixed.show()
        self.set_canvas(self.fixed)

        self._vbox = Gtk.VBox(False, 0)
        self._vbox.set_size_request(Gdk.Screen.width(), Gdk.Screen.height())
        self.fixed.put(self._vbox, 0, 0)
        self._vbox.show()

        self._canvas = Gtk.DrawingArea()
        self._canvas.set_size_request(int(Gdk.Screen.width()),
                                      int(Gdk.Screen.height()))
        self._canvas.show()
        self.show_all()
        self._vbox.pack_end(self._canvas, True, True, 0)
        self._vbox.show()

        self.show_all()

        self.vmw = Game(self._canvas, parent=self, card_type=MODE)
        self.vmw.level = self._play_level
        LEVEL_BUTTONS[self._play_level].set_active(True)
        self.vmw.card_type = self._card_type
        self.vmw.robot = False
        self.vmw.robot_time = self._robot_time
        self.vmw.low_score = self._low_score
        self.vmw.all_scores = self._all_scores
        self.vmw.numberO = self._numberO
        self.vmw.numberC = self._numberC
        self.vmw.matches = self._matches
        self.vmw.robot_matches = self._robot_matches
        self.vmw.total_time = self._total_time
        self.vmw.buddies = []
        self.vmw.word_lists = self._word_lists
        self.vmw.editing_word_list = self._editing_word_list
        if hasattr(self, '_custom_object') and self._custom_object is not None:
            self.vmw._find_custom_paths(datastore.get(self._custom_object))
        for i in range(9):
            if hasattr(self, '_custom_jobject') and \
               self._custom_jobject[i] is not None:
                self.vmw.custom_paths[i] = datastore.get(
                    self._custom_jobject[i])
                self.button_custom.set_sensitive(True)
        return self._canvas

    def write_file(self, file_path):
        ''' Write data to the Journal. '''
        if hasattr(self, 'vmw'):
            self.metadata['play_level'] = self.vmw.level
            self.metadata['low_score_beginner'] = int(self.vmw.low_score[0])
            self.metadata['low_score_intermediate'] = int(
                self.vmw.low_score[1])
            self.metadata['low_score_expert'] = int(self.vmw.low_score[2])
            self.metadata['all_scores'] = jdumps(self.vmw.all_scores)
            _logger.debug("{}".format(jdumps(self.vmw.all_scores)))
            self.metadata['robot_time'] = self.vmw.robot_time
            self.metadata['numberO'] = self.vmw.numberO
            self.metadata['numberC'] = self.vmw.numberC
            self.metadata['cardtype'] = self.vmw.card_type
            self.metadata['matches'] = self.vmw.matches
            self.metadata['robot_matches'] = self.vmw.robot_matches
            self.metadata['total_time'] = int(self.vmw.total_time)
            self.metadata['deck_index'] = self.vmw.deck.index
            self.metadata['mouse'] = self.vmw.word_lists[0][0]
            self.metadata['cat'] = self.vmw.word_lists[0][1]
            self.metadata['dog'] = self.vmw.word_lists[0][2]
            self.metadata['cheese'] = self.vmw.word_lists[1][0]
            self.metadata['apple'] = self.vmw.word_lists[1][1]
            self.metadata['bread'] = self.vmw.word_lists[1][2]
            self.metadata['moon'] = self.vmw.word_lists[2][0]
            self.metadata['sun'] = self.vmw.word_lists[2][1]
            self.metadata['earth'] = self.vmw.word_lists[2][2]
            self.metadata['editing_word_list'] = self.vmw.editing_word_list
            self.metadata['mime_type'] = 'application/x-visualmatch'
            f = open(file_path, 'w')
            f.write(self._dump())
            f.close()
        else:
            _logger.debug('Deferring saving to %s' % file_path)

    def _dump(self):
        ''' Dump game data to the journal.'''
        data = []
        for i in self.vmw.grid.grid:
            if i is None or self.vmw.editing_word_list:
                data.append(None)
            else:
                data.append(i.index)
        for i in self.vmw.clicked:
            if i.spr is None or self.vmw.deck.spr_to_card(i.spr) is None or \
               self.vmw.editing_word_list:
                data.append(None)
            else:
                data.append(self.vmw.deck.spr_to_card(i.spr).index)
        for i in self.vmw.deck.cards:
            if i is None or self.vmw.editing_word_list:
                data.append(None)
            else:
                data.append(i.index)
        for i in self.vmw.match_list:
            if self.vmw.deck.spr_to_card(i) is not None:
                data.append(self.vmw.deck.spr_to_card(i).index)
        for i in self.vmw.word_lists:
            for j in i:
                data.append(j)
        return self._data_dumper(data)

    def _data_dumper(self, data):
        io = StringIO()
        jdump(data, io)
        return io.getvalue()

    def read_file(self, file_path):
        ''' Read data from the Journal. '''
        f = open(file_path, 'r')
        self._load(f.read())
        f.close()

    def _load(self, data):
        ''' Load game data from the journal. '''
        saved_state = self._data_loader(data)
        if len(saved_state) > 0:
            self._saved_state = saved_state

    def _data_loader(self, data):
        json_data = jloads(data)
        return json_data

    def _notify_new_game(self, prompt):
        ''' Called from New Game button since loading a new game can
        be slooow!! '''
        alert = NotifyAlert(3)
        alert.props.title = prompt
        alert.props.msg = _('A new game is loading.')

        def _notification_alert_response_cb(alert, response_id, self):
            self.remove_alert(alert)

        alert.connect('response', _notification_alert_response_cb, self)
        self.add_alert(alert)
        alert.show()

    def _new_help_box(self, name, button=None):
        help_box = Gtk.VBox()
        help_box.set_homogeneous(False)
        help_palettes[name] = help_box
        if button is not None:
            help_buttons[name] = button
        help_windows[name] = Gtk.ScrolledWindow()
        help_windows[name].set_size_request(
            int(Gdk.Screen.width() / 3),
            Gdk.Screen.height() - style.GRID_CELL_SIZE * 3)
        help_windows[name].set_policy(Gtk.PolicyType.NEVER,
                                      Gtk.PolicyType.AUTOMATIC)
        help_windows[name].add_with_viewport(help_palettes[name])
        help_palettes[name].show()
        return help_box

    def _setup_toolbar_help(self):
        ''' Set up a help palette for the main toolbars '''
        help_box = self._new_help_box('main-toolbar')
        add_section(help_box, _('Dimensions'), icon='activity-dimensions')
        add_paragraph(help_box, _('Tools'), icon='view-source')
        if MODE == 'pattern':
            add_paragraph(help_box, _('Game'), icon='new-pattern-game')
        elif MODE == 'number':
            add_paragraph(help_box, PROMPT_DICT['number'],
                          icon='new-number-game')
            add_paragraph(help_box, _('Numbers'), icon='number-tools')
        elif MODE == 'word':
            add_paragraph(help_box, PROMPT_DICT['word'], icon='new-word-game')
        add_paragraph(help_box, _('Play with the computer'), icon='robot-off')
        add_paragraph(help_box, _('robot pause time'), icon='timer-60')
        add_paragraph(help_box, _('beginner'), icon='beginner')
        add_paragraph(help_box, _('intermediate'), icon='intermediate')
        add_paragraph(help_box, _('expert'), icon='expert')

        add_section(help_box, _('Dimensions'), icon='activity-dimensions')
        add_paragraph(help_box, _('Export scores to clipboard'),
                      icon='score-copy')

        add_section(help_box, _('Tools'), icon='view-source')
        add_section(help_box, _('Import image cards'), icon='image-tools')
        add_paragraph(help_box, PROMPT_DICT['custom'], icon='new-custom-game')
        if MODE == 'word':
            add_section(help_box, _('Edit word lists.'), icon='word-tools')

        if MODE == 'number':
            add_section(help_box, _('Numbers'), icon='number-tools')
            add_paragraph(help_box, _('product'), icon='product')
            add_paragraph(help_box, _('Roman numerals'), icon='roman')
            add_paragraph(help_box, _('word'), icon='word')
            add_paragraph(help_box, _('Chinese'), icon='chinese')
            add_paragraph(help_box, _('Mayan'), icon='mayan')
            add_paragraph(help_box, _('Quipu'), icon='incan')
            add_paragraph(help_box, _('hash marks'), icon='hash')
            add_paragraph(help_box, _('dots in a circle'), icon='dots')
            add_paragraph(help_box, _('points on a star'), icon='star')
            add_paragraph(help_box, _('dice'), icon='dice')
            add_paragraph(help_box, _('dots in a line'), icon='lines')

    def _buddy_joined_cb(self, collab, buddy):
        if buddy.nick in self.vmw.buddies:
            return
        self.vmw.buddies.append(buddy.nick)

    def _buddy_left_cb(self, collab, buddy):
        if buddy.nick not in self.vmw.buddies:
            return
        del self.vmw.buddies[self.vmw.buddies.index(buddy.nick)]

    def _shared_cb(self, owner):
        if self.shared_activity is None:
            _logger.error('Failed to share or join activity...\
                shared_activity is null in _shared_cb()')
            return
        _logger.debug('Sharing...')
        self.initiating = True
        self.waiting_for_deck = False

    def _joined_cb(self, sender):
        if self._collab.leader:
            return

        self.waiting_for_deck = True

        self.button_pattern.set_sensitive(False)
        self.robot_button.set_sensitive(False)
        self._robot_time_button.set_sensitive(False)
        self.beginner_button.set_sensitive(False)
        self.intermediate_button.set_sensitive(False)
        self.expert_button.set_sensitive(False)
        self._collab.post(dict(action='joined'))

    def _message_cb(self, collab, buddy, message):
        ''' Data is passed as dict(action='action') '''
        action = message.get('action')

        if action == 'clicked_card':
            card_index = message.get('clicked_card')
            self.vmw.add_to_clicked(
                self.vmw.deck.index_to_card(int(card_index)).spr)
        elif action == 'unselect_cards':
            self.vmw.clean_up_match()
        elif action == 'return_card':
            self.vmw.clean_up_no_match(None)
        elif action == 'select_card':
            card = message.get('select_card')
            self.vmw.process_click(self.vmw.clicked[card].spr)
            self.vmw.process_selection(self.vmw.clicked[card].spr)
        elif action == 'joined':
            if self.initiating:  # Only the sharer 'shares'.
                self._collab.post(dict(action='level',
                    level=self.vmw.level))
                self._collab.post(dict(action='index',
                    index=self.vmw.deck.index))
                self._collab.post(dict(action='matches',
                    matches=self.vmw.matches))
                self._collab.post(dict(action='card_type',
                    card_type=self.vmw.card_type))
                self._collab.post(dict(action='data',
                    data=self._dump()))
        elif action == 'req_state':  # Force a request for current state.
            self._collab.post(dict(action='joined'))
            self.waiting_for_deck = True
        elif action == 'card_type':
            card_type = message.get('card_type')
            self.vmw.card_type = card_type
        elif action == 'numberO':
            numberO = message.get('numberO')
            self.vmw.numberO = numberO
        elif action == 'numberC':
            numberC = message.get('numberC')
            self.vmw.numberC = numberC
        elif action == 'level':
            level = message.get('level')
            self.vmw.level = level
            # self.level_label.set_text(self.calc_level_label(
            #     self.vmw.low_score, self.vmw.level))
            LEVEL_BUTTONS[self.vmw.level].set_active(True)
        elif action == 'index':
            index = message.get('index')
            self.vmw.deck.index = index
        elif action == 'matches':
            matches = message.get('matches')
            self.vmw.matches = matches
        elif action == 'data':
            if self.waiting_for_deck:
                data = message.get('data')
                self._load(data)
                self.waiting_for_deck = False
            self.vmw.new_game(self._saved_state, self.vmw.deck.index)



def image_from_svg_file(filename):
    path = os.path.join(activity.get_bundle_path(), 'icons', filename)
    fd = open(path)
    svg = fd.read()
    fd.close()
    pl = GdkPixbuf.PixbufLoader.new_with_type('svg')
    pl.write(svg.encode('utf-8'))
    pl.close()
    pixbuf = pl.get_pixbuf()
    image = Gtk.Image()
    image.set_from_pixbuf(pixbuf)
    return image
