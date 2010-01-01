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
try: # 0.86+ toolbar widgets
    from sugar.bundle.activitybundle import ActivityBundle
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
    from sugar.graphics.toolbarbox import ToolbarBox
    from sugar.graphics.toolbarbox import ToolbarButton
    from namingalert import NamingAlert
except ImportError:
    pass
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem
from sugar.graphics.icon import Icon
from sugar.datastore import datastore

from gettext import gettext as _
import locale
import os.path

from constants import *
from sprites import *
import window

import gencards

SERVICE = 'org.sugarlabs.VisualMatchActivity'
IFACE = SERVICE
PATH = '/org/augarlabs/VisualMatchActivity'

#
# Sugar activity
#
class VisualMatchActivity(activity.Activity):

    def __init__(self, handle):
        super(VisualMatchActivity,self).__init__(handle)

        # Read the high score from the Journal
        try:
            low_score = int(self.metadata['low_score'])
        except:
            low_score = -1

        # Read the robot time from the Journal
        try:
            robot_time = int(self.metadata['robot_time'])
        except:
            robot_time = 60

        try:
            datapath = os.path.join(activity.get_activity_root(), "data")
        except:
            datapath = os.path.join(os.environ['HOME'], SERVICE, "data")

        # Read the number card preferences from the Journal
        try:
            numberO = int(self.metadata['numberO'])
            numberC = int(self.metadata['numberC'])
        except:
            numberO = PRODUCT
            numberC = HASH
        gencards.generator(datapath,numberO,numberC)

        try:
            # Use 0.86 toolbar design
            toolbar_box = ToolbarBox()

            # Buttons added to the Activity toolbar
            activity_button = ActivityToolbarButton(self)

            # Write in the Journal
            journal_button = ToolButton( "journal-write" )
            journal_button.set_tooltip(_('Write in Journal'))
            journal_button.props.accelerator = '<Ctrl>j'
            journal_button.connect('clicked', self._journal_cb, 
                                   activity.get_bundle_path())
            activity_button.props.page.insert(journal_button, -1)
            journal_button.show()

            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.show()

            # New-pattern-game Button
            self.button1 = ToolButton( "new-pattern-game" )
            self.button1.set_tooltip(_('New pattern game'))
            self.button1.props.sensitive = True
            self.button1.connect('clicked', self._select_game_cb, self,
                                 'pattern')
            toolbar_box.toolbar.insert(self.button1, -1)
            self.button1.show()

            # New-number-game Button
            self.button2 = ToolButton( "new-number-game" )
            self.button2.set_tooltip(_('New number game'))
            self.button2.props.sensitive = True
            self.button2.connect('clicked', self._select_game_cb, self,
                                 'number')
            toolbar_box.toolbar.insert(self.button2, -1)
            self.button2.show()

            # New-word-game Button
            self.button3 = ToolButton( "new-word-game" )
            self.button3.set_tooltip(_('New word game'))
            self.button3.props.sensitive = True
            self.button3.connect('clicked', self._select_game_cb, self,
                                 'word')
            toolbar_box.toolbar.insert(self.button3, -1)
            self.button3.show()

            # The tools toolbar
            tools_toolbar = gtk.Toolbar()
            self.robot_button = ToolButton('robot-off')
            self.robot_button.set_tooltip(_("Play with the computer."))
            self.robot_button.connect('clicked', self._robot_cb, self)
            tools_toolbar.insert(self.robot_button,-1)
            self.robot_button.show()

            self._robot_time_spin_adj = gtk.Adjustment(robot_time,
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

            self.product_button = ToolButton('product')
            self.product_button.connect('clicked', self._number_card_O_cb,
                                        self, PRODUCT)
            tools_toolbar.insert(self.product_button,-1)
            self.product_button.show()

            self.roman_button = ToolButton('roman')
            self.roman_button.connect('clicked', self._number_card_O_cb,
                                        self, ROMAN)
            tools_toolbar.insert(self.roman_button,-1)
            self.roman_button.show()

            self.word_button = ToolButton('word')
            self.word_button.connect('clicked', self._number_card_O_cb,
                                        self, WORD)
            tools_toolbar.insert(self.word_button,-1)
            self.word_button.show()

            self.chinese_button = ToolButton('chinese')
            self.chinese_button.connect('clicked', self._number_card_O_cb,
                                        self, CHINESE)
            tools_toolbar.insert(self.chinese_button,-1)
            self.chinese_button.show()

            separator = gtk.SeparatorToolItem()
            separator.props.draw = True
            tools_toolbar.insert(separator, -1)
            separator.show()

            self.hash_button = ToolButton('hash')
            self.hash_button.connect('clicked', self._number_card_C_cb,
                                        self, HASH)
            tools_toolbar.insert(self.hash_button,-1)
            self.hash_button.show()

            self.dots_button = ToolButton('dots')
            self.dots_button.connect('clicked', self._number_card_C_cb,
                                        self, DOTS)
            tools_toolbar.insert(self.dots_button,-1)
            self.dots_button.show()

            self.star_button = ToolButton('star')
            self.star_button.connect('clicked', self._number_card_C_cb,
                                        self, STAR)
            tools_toolbar.insert(self.star_button,-1)
            self.star_button.show()

            self.dice_button = ToolButton('dice')
            self.dice_button.connect('clicked', self._number_card_C_cb,
                                        self, DICE)
            tools_toolbar.insert(self.dice_button,-1)
            self.dice_button.show()

            self.lines_button = ToolButton('lines')
            self.lines_button.connect('clicked', self._number_card_C_cb,
                                        self, LINES)
            tools_toolbar.insert(self.lines_button,-1)
            self.lines_button.show()

            tools_toolbar_button = ToolbarButton(
                    page=tools_toolbar,
                    icon_name='view-source')
            tools_toolbar.show()
            toolbar_box.toolbar.insert(tools_toolbar_button, -1)
            tools_toolbar_button.show()

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # Label for showing deck status
            self.deck_label = gtk.Label("%d %s" % (DECKSIZE-DEAL,
                                        _("cards")))
            self.deck_label.show()
            deck_toolitem = gtk.ToolItem()
            deck_toolitem.add(self.deck_label)
            toolbar_box.toolbar.insert(deck_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # Label for showing match status
            self.match_label = gtk.Label("%d %s" % (0,_("matches")))
            self.match_label.show()
            match_toolitem = gtk.ToolItem()
            match_toolitem.add(self.match_label)
            toolbar_box.toolbar.insert(match_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # Label for showing counter
            self.clock_label = gtk.Label("-")
            self.clock_label.show()
            clock_toolitem = gtk.ToolItem()
            clock_toolitem.add(self.clock_label)
            toolbar_box.toolbar.insert(clock_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # Label for showing play status
            self.status_label = gtk.Label(_("Find a match."))
            self.status_label.show()
            status_toolitem = gtk.ToolItem()
            status_toolitem.add(self.status_label)
            toolbar_box.toolbar.insert(status_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # The ever-present Stop Button
            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>q'
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()

            self.set_toolbar_box(toolbar_box)
            toolbar_box.show()

        except NameError:
            # Use pre-0.86 toolbar design
            self.toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(self.toolbox)

            self.projectToolbar = ProjectToolbar(self)
            self.toolbox.add_toolbar( _('Project'), self.projectToolbar )

            self.toolsToolbar = ToolsToolbar(self)
            self.toolbox.add_toolbar( _('Tools'), self.toolsToolbar )

            self.toolbox.show()

        # Create a canvas
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(),
                                gtk.gdk.screen_height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        # Initialize the canvas
        self.vmw = window.new_window(canvas, datapath, 'pattern', self)
        self.vmw.robot = False
        self.vmw.robot_time = robot_time
        self.vmw.low_score = low_score
        self.vmw.numberO = numberO
        self.vmw.numberC = numberC

    #
    # Write misc. data to the Journal
    #
    def write_file(self, file_path):
        self.metadata['low_score'] = self.vmw.low_score
        self.metadata['robot_time'] = self.vmw.robot_time
        self.metadata['numberO'] = self.vmw.numberO
        self.metadata['numberC'] = self.vmw.numberC

    #
    # Button callbacks
    #
    def _select_game_cb(self, button, activity, cardtype):
        window.new_game(activity.vmw, cardtype)

    def _robot_cb(self, button, activity):
        if activity.vmw.robot is True:
            activity.vmw.robot = False
            self.robot_button.set_tooltip(_("Play with the computer."))
            self.robot_button.set_icon('robot-off')
        else:
            activity.vmw.robot = True
            self.robot_button.set_tooltip(
                _("Stop playing with the computer."))
            self.robot_button.set_icon('robot-on')

    def _number_card_O_cb(self, button, activity, numberO):
        activity.vmw.numberO = numberO
        gencards.generate_number_cards(activity.vmw.path,
                                       activity.vmw.numberO,
                                       activity.vmw.numberC)
        activity.vmw.cardtype = ''
        window.new_game(activity.vmw, 'number')

    def _number_card_C_cb(self, button, activity, numberC):
        activity.vmw.numberC = numberC
        gencards.generate_number_cards(activity.vmw.path,
                                       activity.vmw.numberO,
                                       activity.vmw.numberC)
        activity.vmw.cardtype = ''
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
# Toolbars for pre-0.86 toolbars
#
class ToolsToolbar(gtk.Toolbar):

    def __init__(self, activity):
        gtk.Toolbar.__init__(self)
        self.activity = activity

        # Robot
        self.activity.robot_button = ToolButton( "robot-off" )
        self.activity.robot_button.set_tooltip(_('Play with the computer.'))
        self.activity.robot_button.props.sensitive = True
        self.activity.robot_button.connect('clicked', self.activity._robot_cb, 
                                           self.activity)
        self.insert(self.activity.robot_button, -1)
        self.activity.robot_button.show()

        self.activity._robot_time_spin_adj = gtk.Adjustment(60,15,180,5,15,0)
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

        # New-pattern-game Button
        self.activity.button1 = ToolButton( "new-pattern-game" )
        self.activity.button1.set_tooltip(_('New pattern game'))
        self.activity.button1.props.sensitive = True
        self.activity.button1.connect('clicked', self.activity._select_game_cb, 
                                      self.activity, 'pattern')
        self.insert(self.activity.button1, -1)
        self.activity.button1.show()

        # New-number-game Button
        self.activity.button2 = ToolButton( "new-number-game" )
        self.activity.button2.set_tooltip(_('New number game'))
        self.activity.button2.props.sensitive = True
        self.activity.button2.connect('clicked', self.activity._select_game_cb, 
                                      self.activity, 'number')
        self.insert(self.activity.button2, -1)
        self.activity.button2.show()

        # New-word-game Button
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

        # Label for showing deck status
        self.activity.deck_label = gtk.Label("%d %s" % (DECKSIZE-DEAL,
                                              _("cards")))
        self.activity.deck_label.show()
        self.activity.deck_toolitem = gtk.ToolItem()
        self.activity.deck_toolitem.add(self.activity.deck_label)
        self.insert(self.activity.deck_toolitem, -1)
        self.activity.deck_toolitem.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        # Label for showing match status
        self.activity.match_label = gtk.Label("%d %s" % (0,_("matches")))
        self.activity.match_label.show()
        self.activity.match_toolitem = gtk.ToolItem()
        self.activity.match_toolitem.add(self.activity.match_label)
        self.insert(self.activity.match_toolitem, -1)
        self.activity.match_toolitem.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        # Label for showing counter
        self.activity.clock_label = gtk.Label("-")
        self.activity.clock_label.show()
        self.activity.clock_toolitem = gtk.ToolItem()
        self.activity.clock_toolitem.add(self.activity.clock_label)
        self.insert(self.activity.clock_toolitem, -1)
        self.activity.clock_toolitem.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        # Label for showing play status
        self.activity.status_label = gtk.Label(_("Find a match."))
        self.activity.status_label.show()
        self.activity.status_toolitem = gtk.ToolItem()
        self.activity.status_toolitem.add(self.activity.status_label)
        self.insert(self.activity.status_toolitem, -1)
        self.activity.status_toolitem.show()

