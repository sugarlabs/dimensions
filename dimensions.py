#!/usr/bin/env python

#Copyright (c) 2009-12 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import gi
from gi.repository import Gtk
from gi.repository import Gdk

from gettext import gettext as _
import os

from game import Game
from constants import PRODUCT, HASH, ROMAN, WORD, CHINESE, MAYAN, DICE, DOTS, \
                      STAR, LINES, INCAN


class DimensionsMain:

    def __init__(self):
        # create a new window
        self.win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.win.maximize()
        self.win.set_title("%s: %s" % (_("Dimensions"),
                           _("Click on cards to create sets of three.")))
        self.win.connect("delete_event", lambda w, e: Gtk.main_quit())

        menu0 = Gtk.Menu()
        menu_items = Gtk.MenuItem(_("beginner"))
        menu0.append(menu_items)
        menu_items.connect("activate", self._level_cb, 0)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("intermediate"))
        menu0.append(menu_items)
        menu_items.connect("activate", self._level_cb, 1)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("expert"))
        menu0.append(menu_items)
        menu_items.connect("activate", self._level_cb, 2)
        menu_items.show()
        #TRANS: Level of difficulty
        level_menu = Gtk.MenuItem(_("Level"))
        level_menu.show()
        level_menu.set_submenu(menu0)

        menu1 = Gtk.Menu()
        menu_items = Gtk.MenuItem(_("New pattern game"))
        menu1.append(menu_items)
        menu_items.connect("activate", self._new_game_cb, 'pattern')
        menu_items.show()
        '''
        menu_items = Gtk.MenuItem(_("New number game"))
        menu1.append(menu_items)
        menu_items.connect("activate", self._new_game_cb, 'number')
        menu_items.show()
        menu_items = Gtk.MenuItem(_("New word game"))
        menu1.append(menu_items)
        menu_items.connect("activate", self._new_game_cb, 'word')
        menu_items.show()
        '''
        game_menu = Gtk.MenuItem(_("Game"))
        game_menu.show()
        game_menu.set_submenu(menu1)

        menu2 = Gtk.Menu()
        menu_items = Gtk.MenuItem(_("Robot on/off"))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_cb)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("5 minutes"))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 300)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("2 minutes"))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 120)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("1 minute"))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 60)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("30 seconds"))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 30)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("15 seconds"))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 15)
        menu_items.show()
        tool_menu = Gtk.MenuItem(_('Play with the computer'))
        tool_menu.show()
        tool_menu.set_submenu(menu2)

        '''
        menu3 = Gtk.Menu()
        menu_items = Gtk.MenuItem(_("Product"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, PRODUCT)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Roman"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, ROMAN)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Word"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, WORD)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Chinese"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, CHINESE)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Mayan"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, MAYAN)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Quipu"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, INCAN)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Hash"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, HASH)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Dice"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, DICE)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Dots"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, DOTS)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Star"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, STAR)
        menu_items.show()
        menu_items = Gtk.MenuItem(_("Lines"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, LINES)
        menu_items.show()
        num_menu = Gtk.MenuItem("Numbers")
        num_menu.show()
        num_menu.set_submenu(menu3)
        '''

        # A vbox to put a menu and the canvas in:
        vbox = Gtk.VBox(False, 0)
        self.win.add(vbox)
        vbox.show()

        menu_bar = Gtk.MenuBar()
        vbox.pack_start(menu_bar, False, False, 2)
        menu_bar.show()

        canvas = Gtk.DrawingArea()
        vbox.pack_end(canvas, True, True, 0)
        canvas.show()

        menu_bar.append(game_menu)
        menu_bar.append(level_menu)
        menu_bar.append(tool_menu)
        # menu_bar.append(num_menu)
        self.win.show_all()

        # Join the activity
        self.vmw = Game(canvas)
        self.vmw.win = self.win
        self.vmw.activity = self
        self.vmw.card_type = 'pattern'
        self.vmw.level = 1
        self.vmw.robot = False
        self.vmw.robot_time = 60
        self.vmw.numberO = PRODUCT
        self.vmw.numberC = HASH
        self.vmw.matches = 0
        self.vmw.robot_matches = 0
        self.load_score()
        self.vmw.word_lists = [[_('mouse'), _('cat'), _('dog')],\
                           [_('cheese'), _('apple'), _('bread')],\
                           [_('moon'), _('sun'), _('earth')]]

        self.vmw.new_game()

    def load_score(self):
        try:
            f = file(os.path.join(os.path.abspath('.'),
                                  'visualmatch.score'), "r")
            s = f.readlines()
            f.close
            self.vmw.low_score = [int(s[0].split(':')[1].strip()),
                                  int(s[1].split(':')[1].strip())]
            print "low score is: %s" % (self.vmw.low_score)
        except:
            self.vmw.low_score = [-1, -1]

    def save_score(self):
        f = file(os.path.join(os.path.abspath('.'), 'visualmatch.score'), "w")
        f.writelines(["low_score_beginner:%d\n" % int(self.vmw.low_score[0]),
                      "low_score_expert:%d\n" % int(self.vmw.low_score[1])])
        f.close

    def set_title(self, title):
        self.win.set_title(title)

    def _new_game_cb(self, widget, game):
        self.vmw.card_type = game
        self.vmw.new_game()
        return True

    def _level_cb(self, widget, level):
        self.vmw.level = level
        self.vmw.new_game()

    def _robot_cb(self, widget):
        if self.vmw.robot:
            self.vmw.robot = False
        else:
            self.vmw.robot = True

    def _robot_time_cb(self, widget, time):
        self.vmw.robot_time = time

    def _number_card_O_cb(self, widget, numberO):
        self.vmw.numberO = numberO
        self.vmw.card_type = 'number'
        self.vmw.new_game()

    def _number_card_C_cb(self, widget, numberC):
        self.vmw.numberC = numberC
        self.vmw.card_type = 'number'
        self.vmw.new_game()


def main():
    Gtk.main()
    return 0


if __name__ == "__main__":
    DimensionsMain()
    main()
