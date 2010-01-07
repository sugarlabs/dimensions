#Copyright (c) 2009, Walter Bender

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sugar
from sugar.activity import activity
try:
    from sugar.bundle.activitybundle import ActivityBundle
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
    from sugar.graphics.toolbarbox import ToolbarBox
    from sugar.graphics.toolbarbox import ToolbarButton
    from namingalert import NamingAlert
    sugar86 = True
except ImportError:
    sugar86 = False
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem
from sugar.graphics.icon import Icon
from sugar.datastore import datastore

from gettext import gettext as _
import locale
import os.path
import logging
_logger = logging.getLogger('visualmatch-activity')
import json
from StringIO import StringIO

from constants import *
from sprites import *
import window
import gencards
import grid
import deck
import card

level_icons = ['level1','level2']


SERVICE = 'org.sugarlabs.VisualMatchActivity'
IFACE = SERVICE
PATH = '/org/augarlabs/VisualMatchActivity'

#
# Sugar activity
#
class VisualMatchActivity(activity.Activity):

    def __init__(self, handle):
        super(VisualMatchActivity,self).__init__(handle)

        # Turn sharing off
        # self.share(private=True)

        # Read settings from the Journal
        try:
            self._play_level = int(self.metadata['play_level'])
            self._robot_time = int(self.metadata['robot_time'])
            self._cardtype = self.metadata['cardtype']
            _numberO = int(self.metadata['numberO'])
            _numberC = int(self.metadata['numberC'])
            _matches = int(self.metadata['matches'])
            _robot_matches = int(self.metadata['robot_matches'])
            _total_time = int(self.metadata['total_time'])
            _deck_index = int(self.metadata['deck_index'])
            _low_score = [int(self.metadata['low_score_beginner']),\
                          int(self.metadata['low_score_expert'])]
        except:
            self._play_level = 0
            self._robot_time = 60
            self._cardtype = 'pattern'
            _numberO = PRODUCT
            _numberC = HASH
            _matches = 0
            _robot_matches = 0
            _total_time = 0
            _deck_index = 0
            _low_score = [-1,-1]

        # Find a path to write card files
        try:
            datapath = os.path.join(activity.get_activity_root(), 'data')
        except:
            datapath = os.path.join(os.environ['HOME'], SERVICE, 'data')
        gencards.generator(datapath, _numberO, _numberC)

        # Create the toolbars
        if sugar86 is True:
            toolbar_box = ToolbarBox()

            # Activity toolbar
            activity_button = ActivityToolbarButton(self)
            journal_button = ToolButton( "journal-write" )
            journal_button.set_tooltip(_('Write in Journal'))
            journal_button.props.accelerator = '<Ctrl>j'
            journal_button.connect('clicked', self._journal_cb, 
                                   activity.get_bundle_path())
            activity_button.props.page.insert(journal_button, -1)
            journal_button.show()
            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.show()

            # New games toolbar
            games_toolbar = gtk.Toolbar()
            self.button1 = ToolButton( "new-pattern-game" )
            self.button1.set_tooltip(_('New pattern game'))
            self.button1.props.sensitive = True
            self.button1.connect('clicked', self._select_game_cb, self,
                                 'pattern')
            games_toolbar.insert(self.button1, -1)
            self.button1.show()
            self.button2 = ToolButton( "new-number-game" )
            self.button2.set_tooltip(_('New number game'))
            self.button2.props.sensitive = True
            self.button2.connect('clicked', self._select_game_cb, self,
                                 'number')
            games_toolbar.insert(self.button2, -1)
            self.button2.show()
            self.button3 = ToolButton( "new-word-game" )
            self.button3.set_tooltip(_('New word game'))
            self.button3.props.sensitive = True
            self.button3.connect('clicked', self._select_game_cb, self,
                                 'word')
            games_toolbar.insert(self.button3, -1)
            self.button3.show()
            games_toolbar_button = ToolbarButton(
                    page=games_toolbar,
                    icon_name='new-game')
            games_toolbar.show()
            toolbar_box.toolbar.insert(games_toolbar_button, -1)
            games_toolbar_button.show()

            # The tools toolbar
            tools_toolbar = gtk.Toolbar()
            self.level_button = ToolButton(level_icons[self._play_level])
            self.level_button.set_tooltip(_('Set difficulty level.'))
            self.level_button.connect('clicked', self._level_cb, self)
            tools_toolbar.insert(self.level_button,-1)
            self.level_button.show()
            if self._play_level == 0:
                self.level_label = gtk.Label(_('beginner'))
            else:
                self.level_label = gtk.Label(_('expert'))
            self.level_label.show()
            level_toolitem = gtk.ToolItem()
            level_toolitem.add(self.level_label)
            tools_toolbar.insert(level_toolitem,-1)
            level_toolitem.show()

            separator = gtk.SeparatorToolItem()
            separator.props.draw = True
            tools_toolbar.insert(separator, -1)
            separator.show()

            self.robot_button = ToolButton('robot-off')
            self.robot_button.set_tooltip(_('Play with the computer.'))
            self.robot_button.connect('clicked', self._robot_cb, self)
            tools_toolbar.insert(self.robot_button,-1)
            self.robot_button.show()

            self._robot_time_spin_adj = gtk.Adjustment(self._robot_time,
                                                       15, 180, 5, 15, 0)
            self._robot_time_spin = gtk.SpinButton(self._robot_time_spin_adj,
                                                   0, 0)
            self._robot_time_spin_id = self._robot_time_spin.connect(
                'value-changed', self._robot_time_spin_cb)
            self._robot_time_spin.set_numeric(True)
            self._robot_time_spin.show()
            self.tool_item_robot_time = gtk.ToolItem()
            self.tool_item_robot_time.add(self._robot_time_spin)
            tools_toolbar.insert(self.tool_item_robot_time, -1)
            self.tool_item_robot_time.show()

            tools_toolbar_button = ToolbarButton(
                    page=tools_toolbar,
                    icon_name='view-source')
            tools_toolbar.show()
            toolbar_box.toolbar.insert(tools_toolbar_button, -1)
            tools_toolbar_button.show()

            # Number games toolbar
            numbers_toolbar = gtk.Toolbar()
            self.product_button = ToolButton('product')
            self.product_button.connect('clicked', self._number_card_O_cb,
                                        self, PRODUCT)
            self.product_button.set_tooltip(_('product'))
            numbers_toolbar.insert(self.product_button,-1)
            self.product_button.show()
            self.roman_button = ToolButton('roman')
            self.roman_button.connect('clicked', self._number_card_O_cb,
                                        self, ROMAN)
            self.roman_button.set_tooltip(_('Roman numerals'))
            numbers_toolbar.insert(self.roman_button,-1)
            self.roman_button.show()
            self.word_button = ToolButton('word')
            self.word_button.connect('clicked', self._number_card_O_cb,
                                        self, WORD)
            self.word_button.set_tooltip(_('word'))
            numbers_toolbar.insert(self.word_button,-1)
            self.word_button.show()
            self.chinese_button = ToolButton('chinese')
            self.chinese_button.connect('clicked', self._number_card_O_cb,
                                        self, CHINESE)
            self.chinese_button.set_tooltip(_('Chinese'))
            numbers_toolbar.insert(self.chinese_button,-1)
            self.chinese_button.show()

            separator = gtk.SeparatorToolItem()
            separator.props.draw = True
            numbers_toolbar.insert(separator, -1)
            separator.show()

            self.hash_button = ToolButton('hash')
            self.hash_button.connect('clicked', self._number_card_C_cb,
                                        self, HASH)
            self.hash_button.set_tooltip(_('hash marks'))
            numbers_toolbar.insert(self.hash_button,-1)
            self.hash_button.show()
            self.dots_button = ToolButton('dots')
            self.dots_button.connect('clicked', self._number_card_C_cb,
                                        self, DOTS)
            self.dots_button.set_tooltip(_('dots in a circle'))
            numbers_toolbar.insert(self.dots_button,-1)
            self.dots_button.show()
            self.star_button = ToolButton('star')
            self.star_button.connect('clicked', self._number_card_C_cb,
                                        self, STAR)
            self.star_button.set_tooltip(_('points on a star'))
            numbers_toolbar.insert(self.star_button,-1)
            self.star_button.show()
            self.dice_button = ToolButton('dice')
            self.dice_button.connect('clicked', self._number_card_C_cb,
                                        self, DICE)
            self.dice_button.set_tooltip(_('dice'))
            numbers_toolbar.insert(self.dice_button,-1)
            self.dice_button.show()
            self.lines_button = ToolButton('lines')
            self.lines_button.connect('clicked', self._number_card_C_cb,
                                        self, LINES)
            self.lines_button.set_tooltip(_('dots in a line'))
            numbers_toolbar.insert(self.lines_button,-1)
            self.lines_button.show()

            numbers_toolbar_button = ToolbarButton(
                    page=numbers_toolbar,
                    icon_name='number-tools')
            numbers_toolbar.show()
            toolbar_box.toolbar.insert(numbers_toolbar_button, -1)
            numbers_toolbar_button.show()

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            if self._play_level == 1:
                self.deck_label = gtk.Label("%d %s" % (DECKSIZE-DEAL,
                                            _('cards')))
            else:
                self.deck_label = gtk.Label("%d %s" % ((DECKSIZE-DEAL)/3,
                                            _('cards')))
            self.deck_label.show()
            deck_toolitem = gtk.ToolItem()
            deck_toolitem.add(self.deck_label)
            toolbar_box.toolbar.insert(deck_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            self.match_label = gtk.Label("%d %s" % (0,_('matches')))
            self.match_label.show()
            match_toolitem = gtk.ToolItem()
            match_toolitem.add(self.match_label)
            toolbar_box.toolbar.insert(match_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            self.clock_label = gtk.Label('-')
            self.clock_label.show()
            clock_toolitem = gtk.ToolItem()
            clock_toolitem.add(self.clock_label)
            toolbar_box.toolbar.insert(clock_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            self.status_label = gtk.Label(_('Find a match.'))
            self.status_label.show()
            status_toolitem = gtk.ToolItem()
            status_toolitem.add(self.status_label)
            toolbar_box.toolbar.insert(status_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>q'
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()

            self.set_toolbar_box(toolbar_box)
            toolbar_box.show()

        else:
            self.toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(self.toolbox)
            self.projectToolbar = ProjectToolbar(self)
            self.toolbox.add_toolbar( _('Game'), self.projectToolbar )
            self.toolsToolbar = ToolsToolbar(self)
            self.toolbox.add_toolbar( _('Tools'), self.toolsToolbar )
            self.numbersToolbar = NumbersToolbar(self)
            self.toolbox.add_toolbar( _('Numbers'), self.numbersToolbar )
            self.toolbox.show()
            self.toolbox.set_current_toolbar(1)

        # Create a canvas
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(),
                                gtk.gdk.screen_height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        # Initialize the canvas, game state, et al.
        self.vmw = window.new_window(canvas, datapath, self)
        self.vmw.level = self._play_level
        self.vmw.cardtype = self._cardtype
        self.vmw.robot = False
        self.vmw.robot_time = self._robot_time
        self.vmw.low_score = _low_score
        self.vmw.numberO = _numberO
        self.vmw.numberC = _numberC
        self.vmw.matches = _matches
        self.vmw.robot_matches = _robot_matches
        self.vmw.total_time = _total_time
        if not hasattr(self,'_saved_state'):
            self._saved_state = None

        # Start playing the game
        window.new_game(self.vmw, self.vmw.cardtype, 
                        self._saved_state, _deck_index)

    #
    # Write data to the Journal
    #
    def write_file(self, file_path):
        _logger.debug("Saving to: %s" % file_path)
        if hasattr(self, 'vmw'):
            self.metadata['play_level'] = self.vmw.level
            self.metadata['low_score_beginner'] = int(self.vmw.low_score[0])
            self.metadata['low_score_expert'] = int(self.vmw.low_score[1])
            self.metadata['robot_time'] = self.vmw.robot_time
            self.metadata['numberO'] = self.vmw.numberO
            self.metadata['numberC'] = self.vmw.numberC
            self.metadata['cardtype'] = self.vmw.cardtype
            self.metadata['matches'] = self.vmw.matches
            self.metadata['robot_matches'] = self.vmw.robot_matches
            self.metadata['total_time'] = int(self.vmw.total_time)
            self.metadata['deck_index'] = self.vmw.deck.index
            self.metadata['mime_type'] = 'application/x-visualmatch'
            f = file(file_path, 'w')
            data = []
            for i in self.vmw.grid.grid:
                if i is None:
                    data.append(None)
                else:
                    data.append(i.index)
            for i in self.vmw.clicked:
                if i is None:
                    data.append(None)
                else:
                    data.append(self.vmw.deck.spr_to_card(i).index)
            for i in self.vmw.deck.cards:
                data.append(i.index)
            for i in self.vmw.match_list:
                data.append(self.vmw.deck.spr_to_card(i).index)
            io = StringIO()
            json.dump(data,io)
            f.write(io.getvalue())
            f.close()
        else:
            _logger.debug("Deferring saving to %s" % file_path)

    #
    # Read data from the Journal
    #
    def read_file(self, file_path):
        _logger.debug("Resuming from: %s" %  file_path)
        f = open(file_path, 'r')
        io = StringIO(f.read())
        saved_state = json.load(io)
        if len(saved_state) > 0:
            self._saved_state = saved_state
        f.close()

    #
    # Button callbacks
    #
    def _select_game_cb(self, button, activity, cardtype):
        window.new_game(activity.vmw, cardtype)

    def _robot_cb(self, button, activity):
        if activity.vmw.robot is True:
            activity.vmw.robot = False
            self.robot_button.set_tooltip(_('Play with the computer.'))
            self.robot_button.set_icon('robot-off')
        else:
            activity.vmw.robot = True
            self.robot_button.set_tooltip(
                _('Stop playing with the computer.'))
            self.robot_button.set_icon('robot-on')

    def _level_cb(self, button, activity):
        activity.vmw.level = 1-activity.vmw.level
        if activity.vmw.level == 0:
            self.level_label.set_text(_('beginner'))
        else:
            self.level_label.set_text(_('expert'))
        self.level_button.set_icon(level_icons[activity.vmw.level])
        cardtype = activity.vmw.cardtype
        activity.vmw.cardtype = '' # force generation of new deck 
        window.new_game(activity.vmw, cardtype)

    def _number_card_O_cb(self, button, activity, numberO):
        activity.vmw.numberO = numberO
        gencards.generate_number_cards(activity.vmw.path,
                                       activity.vmw.numberO,
                                       activity.vmw.numberC)
        activity.vmw.cardtype = '' # force generation of new deck 
        window.new_game(activity.vmw, 'number')

    def _number_card_C_cb(self, button, activity, numberC):
        activity.vmw.numberC = numberC
        gencards.generate_number_cards(activity.vmw.path,
                                       activity.vmw.numberO,
                                       activity.vmw.numberC)
        activity.vmw.cardtype = '' # force generation of new deck 
        window.new_game(activity.vmw, 'number')

    def _robot_time_spin_cb(self, button):
        self.vmw.robot_time = self._robot_time_spin.get_value_as_int()
        return

    def _journal_cb(self, button, path):
        title_alert = NamingAlert(self, path)
        title_alert.set_transient_for(self.get_toplevel())
        title_alert.show()
        self.reveal()
        return True

#
# Toolbars for pre-0.86 Sugar
#
class ToolsToolbar(gtk.Toolbar):

    def __init__(self, activity):
        gtk.Toolbar.__init__(self)
        self.activity = activity

        self.activity.level_button = ToolButton(
            level_icons[self.activity._play_level])
        self.activity.level_button.set_tooltip(_('Set difficulty level.'))
        self.activity.level_button.props.sensitive = True
        self.activity.level_button.connect('clicked', self.activity._level_cb, 
                                           self.activity)
        self.insert(self.activity.level_button, -1)
        self.activity.level_button.show()
        if self.activity._play_level == 0:
            self.activity.level_label = gtk.Label(_('beginner'))
        else:
            self.activity.level_label = gtk.Label(_('expert'))
        self.activity.level_label.show()
        self.activity.level_toolitem = gtk.ToolItem()
        self.activity.level_toolitem.add(self.activity.level_label)
        self.insert(self.activity.level_toolitem,-1)
        self.activity.level_toolitem.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        self.activity.robot_button = ToolButton( "robot-off" )
        self.activity.robot_button.set_tooltip(_('Play with the computer.'))
        self.activity.robot_button.props.sensitive = True
        self.activity.robot_button.connect('clicked', self.activity._robot_cb, 
                                           self.activity)
        self.insert(self.activity.robot_button, -1)
        self.activity.robot_button.show()
        self.activity._robot_time_spin_adj = gtk.Adjustment(
            self.activity._robot_time,15,180,5,15,0)
        self.activity._robot_time_spin = gtk.SpinButton(
            self.activity._robot_time_spin_adj, 0, 0)
        self.activity._robot_time_spin_id = \
            self.activity._robot_time_spin.connect('value-changed', 
                self.activity._robot_time_spin_cb)
        self.activity._robot_time_spin.set_numeric(True)
        self.activity._robot_time_spin.show()
        self.activity.tool_item_robot_time = gtk.ToolItem()
        self.activity.tool_item_robot_time.add(self.activity._robot_time_spin)
        self.insert(self.activity.tool_item_robot_time, -1)
        self.activity.tool_item_robot_time.show()

class NumbersToolbar(gtk.Toolbar):

    def __init__(self, activity):
        gtk.Toolbar.__init__(self)
        self.activity = activity

        self.activity.product_button = ToolButton( "product" )
        self.activity.product_button.props.sensitive = True
        self.activity.product_button.connect('clicked', 
            self.activity._number_card_O_cb, self.activity, PRODUCT)
        self.insert(self.activity.product_button, -1)
        self.activity.product_button.show()
        self.activity.roman_button = ToolButton( "roman" )
        self.activity.roman_button.props.sensitive = True
        self.activity.roman_button.connect('clicked', 
            self.activity._number_card_O_cb, self.activity, ROMAN)
        self.insert(self.activity.roman_button, -1)
        self.activity.roman_button.show()
        self.activity.word_button = ToolButton( "word" )
        self.activity.word_button.props.sensitive = True
        self.activity.word_button.connect('clicked', 
            self.activity._number_card_O_cb, self.activity, WORD)
        self.insert(self.activity.word_button, -1)
        self.activity.word_button.show()
        self.activity.chinese_button = ToolButton( "chinese" )
        self.activity.chinese_button.props.sensitive = True
        self.activity.chinese_button.connect('clicked', 
            self.activity._number_card_O_cb, self.activity, CHINESE)
        self.insert(self.activity.chinese_button, -1)
        self.activity.chinese_button.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        self.activity.hash_button = ToolButton( "hash" )
        self.activity.hash_button.props.sensitive = True
        self.activity.hash_button.connect('clicked', 
            self.activity._number_card_C_cb, self.activity, HASH)
        self.insert(self.activity.hash_button, -1)
        self.activity.hash_button.show()
        self.activity.dots_button = ToolButton( "dots" )
        self.activity.dots_button.props.sensitive = True
        self.activity.dots_button.connect('clicked', 
            self.activity._number_card_C_cb, self.activity, DOTS)
        self.insert(self.activity.dots_button, -1)
        self.activity.dots_button.show()
        self.activity.star_button = ToolButton( "star" )
        self.activity.star_button.props.sensitive = True
        self.activity.star_button.connect('clicked', 
            self.activity._number_card_C_cb, self.activity, STAR)
        self.insert(self.activity.star_button, -1)
        self.activity.star_button.show()
        self.activity.dice_button = ToolButton( "dice" )
        self.activity.dice_button.props.sensitive = True
        self.activity.dice_button.connect('clicked', 
            self.activity._number_card_C_cb, self.activity, DICE)
        self.insert(self.activity.dice_button, -1)
        self.activity.dice_button.show()
        self.activity.lines_button = ToolButton( "lines" )
        self.activity.lines_button.props.sensitive = True
        self.activity.lines_button.connect('clicked', 
            self.activity._number_card_C_cb, self.activity, LINES)
        self.insert(self.activity.lines_button, -1)
        self.activity.lines_button.show()

class ProjectToolbar(gtk.Toolbar):

    def __init__(self, activity):
        gtk.Toolbar.__init__(self)
        self.activity = activity
        self.activity.button1 = ToolButton( "new-pattern-game" )
        self.activity.button1.set_tooltip(_('New pattern game'))
        self.activity.button1.props.sensitive = True
        self.activity.button1.connect('clicked', self.activity._select_game_cb, 
                                      self.activity, 'pattern')
        self.insert(self.activity.button1, -1)
        self.activity.button1.show()
        self.activity.button2 = ToolButton( "new-number-game" )
        self.activity.button2.set_tooltip(_('New number game'))
        self.activity.button2.props.sensitive = True
        self.activity.button2.connect('clicked', self.activity._select_game_cb, 
                                      self.activity, 'number')
        self.insert(self.activity.button2, -1)
        self.activity.button2.show()
        self.activity.button3 = ToolButton( "new-word-game" )
        self.activity.button3.set_tooltip(_('New word game'))
        self.activity.button3.props.sensitive = True
        self.activity.button3.connect('clicked', self.activity._select_game_cb, 
                                      self.activity, 'word')
        self.insert(self.activity.button3, -1)
        self.activity.button3.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        self.activity.deck_label = gtk.Label("%d %s" % (DECKSIZE-DEAL,
                                              _('cards')))
        self.activity.deck_label.show()
        self.activity.deck_toolitem = gtk.ToolItem()
        self.activity.deck_toolitem.add(self.activity.deck_label)
        self.insert(self.activity.deck_toolitem, -1)
        self.activity.deck_toolitem.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        self.activity.match_label = gtk.Label("%d %s" % (0,_('matches')))
        self.activity.match_label.show()
        self.activity.match_toolitem = gtk.ToolItem()
        self.activity.match_toolitem.add(self.activity.match_label)
        self.insert(self.activity.match_toolitem, -1)
        self.activity.match_toolitem.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        self.activity.clock_label = gtk.Label('-')
        self.activity.clock_label.show()
        self.activity.clock_toolitem = gtk.ToolItem()
        self.activity.clock_toolitem.add(self.activity.clock_label)
        self.insert(self.activity.clock_toolitem, -1)
        self.activity.clock_toolitem.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        self.activity.status_label = gtk.Label(_('Find a match.'))
        self.activity.status_label.show()
        self.activity.status_toolitem = gtk.ToolItem()
        self.activity.status_toolitem.add(self.activity.status_label)
        self.insert(self.activity.status_toolitem, -1)
        self.activity.status_toolitem.show()

