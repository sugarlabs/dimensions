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

import telepathy
from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject
from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection
from sugar import profile

from gettext import gettext as _
import locale
import os.path
import logging
_logger = logging.getLogger('visualmatch-activity')
try:
    _old_sugar_system = False
    import json
    json.dumps
    from json import load as jload
    from json import dump as jdump
except (ImportError, AttributeError):
    try:
        import simplejson as json
        from simplejson import load as jload
        from simplejson import dump as jdump
    except:
        _old_sugar_system = True

from StringIO import StringIO

from constants import *
from sprites import *
import window
import gencards
import grid
import deck
import card

level_icons = ['level1','level2']
level_labels = [_('beginner'),_('expert')]
level_decksize = [DECKSIZE/3, DECKSIZE]

SERVICE = 'org.sugarlabs.VisualMatchActivity'
IFACE = SERVICE
PATH = '/org/augarlabs/VisualMatchActivity'

#
# Sugar activity
#
class VisualMatchActivity(activity.Activity):

    def __init__(self, handle):
        super(VisualMatchActivity,self).__init__(handle)

        # Set things up.
        self._read_journal_data()
        datapath = self._find_datapath(_old_sugar_system)
        gencards.generator(datapath, self._numberO, self._numberC)
        self._setup_toolbars(sugar86)
        canvas = self._setup_canvas(datapath)
        self._setup_presence_service()

        # Then start playing the game.
        if not hasattr(self,'_saved_state'):
            self._saved_state = None
        self.vmw.new_game(self._saved_state, self._deck_index)

    #
    # Button callbacks
    #
    def _select_game_cb(self, button, activity, cardtype):
        if self.vmw.joiner(): # joiner cannot change level
            return
        activity.vmw.cardtype = cardtype
        activity.vmw.new_game()

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
        if activity.vmw.joiner(): # joiner cannot change level
            return
        activity.vmw.level = 1-activity.vmw.level
        self.level_label.set_text(self.calc_level_label(activity.vmw.low_score,
                                                        activity.vmw.level))
        self.level_button.set_icon(level_icons[activity.vmw.level])
        activity.vmw.new_game()

    def calc_level_label(self, low_score, play_level):
        if low_score[play_level] == -1:
            return level_labels[play_level]
        else:
            return "%s (%d:%02d)" % \
                    (level_labels[play_level],
                     int(low_score[play_level]/60),
                     int(low_score[play_level]%60))

    def _number_card_O_cb(self, button, activity, numberO):
        if activity.vmw.joiner(): # joiner cannot change decks
            return
        activity.vmw.numberO = numberO
        gencards.generate_number_cards(activity.vmw.path,
                                       activity.vmw.numberO,
                                       activity.vmw.numberC)
        activity.vmw.cardtype = 'number'
        activity.vmw.new_game()

    def _number_card_C_cb(self, button, activity, numberC):
        if activity.vmw.joiner(): # joiner cannot change decks
            return
        activity.vmw.numberC = numberC
        gencards.generate_number_cards(activity.vmw.path,
                                       activity.vmw.numberO,
                                       activity.vmw.numberC)
        activity.vmw.cardtype = 'number'
        activity.vmw.new_game()

    def _robot_time_spin_cb(self, button):
        self.vmw.robot_time = self._robot_time_spin.get_value_as_int()
        return

    '''
    def _journal_cb(self, button, path):
        title_alert = NamingAlert(self, path)
        title_alert.set_transient_for(self.get_toplevel())
        title_alert.show()
        self.reveal()
        return True
    '''

    #
    # There may be data from a previous instance.
    #
    def _read_journal_data(self):
        try: # Try reading restored settings from the Journal.
            self._play_level = int(self.metadata['play_level'])
            self._robot_time = int(self.metadata['robot_time'])
            self._cardtype = self.metadata['cardtype']
            self._low_score = [int(self.metadata['low_score_beginner']),\
                               int(self.metadata['low_score_expert'])]
            self._numberO = int(self.metadata['numberO'])
            self._numberC = int(self.metadata['numberC'])
            self._matches = int(self.metadata['matches'])
            self._robot_matches = int(self.metadata['robot_matches'])
            self._total_time = int(self.metadata['total_time'])
            self._deck_index = int(self.metadata['deck_index'])
        except: # Otherwise, use default values.
            self._play_level = 0
            self._robot_time = 60
            self._cardtype = 'pattern'
            self._low_score = [-1,-1]
            self._numberO = PRODUCT
            self._numberC = HASH
            self._matches = 0
            self._robot_matches = 0
            self._total_time = 0
            self._deck_index = 0

    #
    # Find the datapath for saving card files
    #
    def _find_datapath(self, _old_sugar_system):
        # Create the card files.
        self._old_sugar_system = _old_sugar_system
        if self._old_sugar_system:
            return os.path.join(os.environ['HOME'], ".sugar", "default", 
                                SERVICE, 'data')
        else:
            return os.path.join(activity.get_activity_root(), 'data')

    #
    # Setup the toolbars.
    #
    def _setup_toolbars(self, sugar86):
        # Create the toolbars.
        if sugar86 is True:
            toolbar_box = ToolbarBox()

            # Activity toolbar
            activity_button = ActivityToolbarButton(self)

            '''
            journal_button = ToolButton( "journal-write" )
            journal_button.set_tooltip(_('Write in Journal'))
            journal_button.props.accelerator = '<Ctrl>j'
            journal_button.connect('clicked', self._journal_cb, 
                                   activity.get_bundle_path())
            activity_button.props.page.insert(journal_button, -1)
            journal_button.show()
            '''

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

            separator = gtk.SeparatorToolItem()
            separator.props.draw = True
            tools_toolbar.insert(separator, -1)
            separator.show()

            self.level_button = ToolButton(level_icons[self._play_level])
            self.level_button.set_tooltip(_('Set difficulty level.'))
            self.level_button.connect('clicked', self._level_cb, self)
            tools_toolbar.insert(self.level_button,-1)
            self.level_button.show()
            self.level_label = gtk.Label(self.calc_level_label(self._low_score,
                                                              self._play_level))
            self.level_label.show()
            level_toolitem = gtk.ToolItem()
            level_toolitem.add(self.level_label)
            tools_toolbar.insert(level_toolitem,-1)
            level_toolitem.show()

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

            self.deck_label = gtk.Label("%d %s" % \
                (level_decksize[self._play_level]-DEAL, _('cards')))
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

    #
    # Create a canvas.
    #
    def _setup_canvas(self, datapath):
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(),
                                gtk.gdk.screen_height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        self.vmw = window.VisualMatchWindow(canvas, datapath, self)
        self.vmw.level = self._play_level
        self.vmw.cardtype = self._cardtype
        self.vmw.robot = False
        self.vmw.robot_time = self._robot_time
        self.vmw.low_score = self._low_score
        self.vmw.numberO = self._numberO
        self.vmw.numberC = self._numberC
        self.vmw.matches = self._matches
        self.vmw.robot_matches = self._robot_matches
        self.vmw.total_time = self._total_time
        self.vmw.buddies = []
        return canvas

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
            f.write(self._dump())
            f.close()
        else:
            _logger.debug("Deferring saving to %s" % file_path)

    def _dump(self):
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

        if self._old_sugar_system is True:
            return json.write(data)
        else:
            io = StringIO()
            jdump(data, io)
            return io.getvalue()

    #
    # Read data from the Journal
    #
    def read_file(self, file_path):
        _logger.debug("Resuming from: %s" %  file_path)
        f = open(file_path, 'r')
        self._load(f.read())
        f.close()

    def _load(self, data):
        if self._old_sugar_system is True:
            saved_state = json.read(data)
        else:
            io = StringIO(data)
            saved_state = jload(io)
        if len(saved_state) > 0:
            self._saved_state = saved_state

    #
    # Setup the Presence Service
    #
    def _setup_presence_service(self):
        self.pservice = presenceservice.get_instance()
        self.initiating = None # sharing (True) or joining (False)

        # Add my buddy object to the list
        owner = self.pservice.get_owner()
        self.owner = owner
        self.vmw.buddies.append(self.owner)
        self._share = ""
        self.connect('shared', self._shared_cb)
        self.connect('joined', self._joined_cb)

    #
    # Sharing-related callbacks
    #

    # Either set up initial share...
    def _shared_cb(self, activity):
        if self._shared_activity is None:
            _logger.error("Failed to share or join activity ... \
                _shared_activity is null in _shared_cb()")
            return

        self.initiating = True
        self.waiting_for_deck = False
        _logger.debug('I am sharing...')

        self.conn = self._shared_activity.telepathy_conn
        self.tubes_chan = self._shared_activity.telepathy_tubes_chan
        self.text_chan = self._shared_activity.telepathy_text_chan
        
        # call back for "NewTube" signal
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal \
            ('NewTube', self._new_tube_cb)

        _logger.debug('This is my activity: making a tube...')
        id = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            SERVICE, {})

    # ...or join an exisiting share.
    def _joined_cb(self, activity):
        if self._shared_activity is None:
            _logger.error("Failed to share or join activity ... \
                _shared_activity is null in _shared_cb()")
            return

        self.initiating = False
        _logger.debug('I joined a shared activity.')

        self.conn = self._shared_activity.telepathy_conn
        self.tubes_chan = self._shared_activity.telepathy_tubes_chan
        self.text_chan = self._shared_activity.telepathy_text_chan
        
        # call back for "NewTube" signal
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal( \
            'NewTube', self._new_tube_cb)

        _logger.debug('I am joining an activity: waiting for a tube...')
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb, 
            error_handler=self._list_tubes_error_cb)

        self.waiting_for_deck = True

    def _list_tubes_reply_cb(self, tubes):
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        _logger.error('ListTubes() failed: %s', e)

    def _new_tube_cb(self, id, initiator, type, service, params, state):
        _logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
                     'params=%r state=%d', id, initiator, type, service, 
                     params, state)

        if (type == telepathy.TUBE_TYPE_DBUS and service == SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[ \
                              telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)

            tube_conn = TubeConnection(self.conn, 
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES], id, \
                group_iface=self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP])

            # We'll use a chattube to send serialized data back and forth.
            self.chattube = ChatTube(tube_conn, self.initiating, \
                self.event_received_cb)

            # Now that we have the tube, we can ask for the deck of cards.
            if self.waiting_for_deck is True:
                self._send_event("j")

    # Data is passed as tuples: cmd:text
    def event_received_cb(self, text):
        if text[0] == 'B':
            e,card_index = text.split(':')
            _logger.debug("receiving card index: " + card_index)
            self.vmw._process_selection(
                self.vmw.deck.index_to_card(int(card_index)).spr)
        elif text[0] == 'S':
            e,card_index = text.split(':')
            _logger.debug("receiving selection index: " + card_index)
            self.vmw._process_selection(
                self.vmw.selected[int(card_index)].spr)
        elif text[0] == 'j':
            if self.initiating is True:  # Only the sharer "shares".
                _logger.debug("serialize the project and send to joiner")
                self._send_event("P:" + str(self.vmw.level))
                self._send_event("X:" + str(self.vmw.deck.index))
                self._send_event("M:" + str(self.vmw.matches))
                self._send_event("C:" + self.vmw.cardtype)
                self._send_event("D:" + str(self._dump()))
        elif text[0] == 'J': # Force a request for current state.
            self._send_event("j")
            self.waiting_for_deck = True
        elif text[0] == 'C':
            e,text = text.split(':')
            _logger.debug("receiving cardtype from sharer " + text)
            self.vmw.cardtype = text
        elif text[0] == 'P':
            e,text = text.split(':')
            _logger.debug("receiving play level from sharer " + text)
            self.vmw.level = int(text)
            self.level_label.set_text(self.calc_level_label(
                self.vmw.low_score, self.vmw.level))
            self.level_button.set_icon(level_icons[self.vmw.level])
        elif text[0] == 'X':
            e,text = text.split(':')
            _logger.debug("receiving deck index from sharer " + text)
            self.vmw.deck.index = int(text)
        elif text[0] == 'M':
            e,text = text.split(':')
            _logger.debug("receiving matches from sharer " + text)
            self.vmw.matches = int(text)
        elif text[0] == 'D':
            if self.waiting_for_deck:
                e,text = text.split(':')
                _logger.debug("receiving deck data from sharer")
                self._load(text)
                self.waiting_for_deck = False
            self.vmw.new_game(self._saved_state, self.vmw.deck.index)

    # Send event through the tube
    def _send_event(self, entry):
        if hasattr(self, 'chattube') and self.chattube is not None:
            self.chattube.SendText(entry)

#
# Class for setting up tube for sharing
#
class ChatTube(ExportedGObject):
 
    def __init__(self, tube, is_initiator, stack_received_cb):
        super(ChatTube, self).__init__(tube, PATH)
        self.tube = tube
        self.is_initiator = is_initiator # Are we sharing or joining activity?
        self.stack_received_cb = stack_received_cb
        self.stack = ''

        self.tube.add_signal_receiver(self.send_stack_cb, 'SendText', IFACE,
                                      path=PATH, sender_keyword='sender')

    def send_stack_cb(self, text, sender=None):
        if sender == self.tube.get_unique_name():
            return
        # _logger.debug("This connection has no unique name yet.")
        self.stack = text
        self.stack_received_cb(text)

    @signal(dbus_interface=IFACE, signature='s')
    def SendText(self, text):
        self.stack = text

#
# Toolbars for pre-0.86 Sugar
#
class ToolsToolbar(gtk.Toolbar):

    def __init__(self, activity):
        gtk.Toolbar.__init__(self)
        self.activity = activity

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

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        self.activity.level_button = ToolButton(
            level_icons[self.activity._play_level])
        self.activity.level_button.set_tooltip(_('Set difficulty level.'))
        self.activity.level_button.props.sensitive = True
        self.activity.level_button.connect('clicked', self.activity._level_cb, 
                                           self.activity)
        self.insert(self.activity.level_button, -1)
        self.activity.level_button.show()
        self.activity.level_label = gtk.Label(self.activity.calc_level_label(
                                         self.activity._low_score,
                                         self.activity._play_level))
        self.activity.level_label.show()
        self.activity.level_toolitem = gtk.ToolItem()
        self.activity.level_toolitem.add(self.activity.level_label)
        self.insert(self.activity.level_toolitem,-1)
        self.activity.level_toolitem.show()

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

        self.activity.deck_label = gtk.Label("%d %s" % \
            (level_decksize[self.activity._play_level]-DEAL, _('cards')))
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

