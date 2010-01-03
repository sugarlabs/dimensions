#!/usr/bin/env python

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

from gettext import gettext as _
import os

import window
import grid
import card
import sprites
import gencards
from constants import *

class VisualMatchMain:
    def __init__(self):
        self.r = 0
        self.tw = None
        # create a new window
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.maximize()
        self.win.set_title("%s: %s" % (_("Visual Match"),
                           _("Click on cards to create sets of three.")))
        self.win.connect("delete_event", lambda w,e: gtk.main_quit())

        if not os.path.exists(os.path.join(os.path.abspath('.'), 'images')):
            os.mkdir(os.path.join(os.path.abspath('.'), 'images'))
        gencards.generator(os.path.join(os.path.abspath('.'), 'images'))

        menu1 = gtk.Menu()
        menu_items = gtk.MenuItem(_("New pattern game"))
        menu1.append(menu_items)
        menu_items.connect("activate", self._new_game_cb, 'pattern')
        menu_items.show()
        menu_items = gtk.MenuItem(_("New number game"))
        menu1.append(menu_items)
        menu_items.connect("activate", self._new_game_cb, 'number')
        menu_items.show()
        menu_items = gtk.MenuItem(_("New word game"))
        menu1.append(menu_items)
        menu_items.connect("activate", self._new_game_cb, 'word')
        menu_items.show()
        game_menu = gtk.MenuItem("Games")
        game_menu.show()
        game_menu.set_submenu(menu1)

        menu2 = gtk.Menu()
        menu_items = gtk.MenuItem(_("Robot on/off"))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_cb)
        menu_items.show()
        menu_items = gtk.MenuItem(_("90 sec."))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 90)
        menu_items.show()
        menu_items = gtk.MenuItem(_("60 sec."))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 60)
        menu_items.show()
        menu_items = gtk.MenuItem(_("45 sec."))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 45)
        menu_items.show()
        menu_items = gtk.MenuItem(_("30 sec."))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 30)
        menu_items.show()
        menu_items = gtk.MenuItem(_("15 sec."))
        menu2.append(menu_items)
        menu_items.connect("activate", self._robot_time_cb, 15)
        menu_items.show()
        tool_menu = gtk.MenuItem("Robot")
        tool_menu.show()
        tool_menu.set_submenu(menu2)

        menu3 = gtk.Menu()
        menu_items = gtk.MenuItem(_("Product"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, PRODUCT)
        menu_items.show()
        menu_items = gtk.MenuItem(_("Roman"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, ROMAN)
        menu_items.show()
        menu_items = gtk.MenuItem(_("Word"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, WORD)
        menu_items.show()
        menu_items = gtk.MenuItem(_("Chinese"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_O_cb, CHINESE)
        menu_items.show()
        menu_items = gtk.MenuItem(_("Hash"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, HASH)
        menu_items.show()
        menu_items = gtk.MenuItem(_("Dice"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, DICE)
        menu_items.show()
        menu_items = gtk.MenuItem(_("Dots"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, DOTS)
        menu_items.show()
        menu_items = gtk.MenuItem(_("Star"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, STAR)
        menu_items.show()
        menu_items = gtk.MenuItem(_("Lines"))
        menu3.append(menu_items)
        menu_items.connect("activate", self._number_card_C_cb, LINES)
        menu_items.show()
        num_menu = gtk.MenuItem("Numbers")
        num_menu.show()
        num_menu.set_submenu(menu3)

        # A vbox to put a menu and the canvas in:
        vbox = gtk.VBox(False, 0)
        self.win.add(vbox)
        vbox.show()

        menu_bar = gtk.MenuBar()
        vbox.pack_start(menu_bar, False, False, 2)
        menu_bar.show()

        canvas = gtk.DrawingArea()
        vbox.pack_end(canvas, True, True)
        canvas.show()

        menu_bar.append(game_menu)
        menu_bar.append(tool_menu)
        menu_bar.append(num_menu)
        self.win.show_all()

        # Join the activity
        self.vmw = window.new_window(canvas, \
                               os.path.join(os.path.abspath('.'), \
                                            'images/'))
        self.vmw.win = self.win
        self.vmw.activity = self
        self.vmw.cardtype = 'pattern'
        self.vmw.level = 1
        self.vmw.robot = False
        self.vmw.robot_time = 60
        self.vmw.numberO = PRODUCT
        self.vmw.numberC = HASH
        self.load_score()

        window.new_game(self.vmw, self.vmw.cardtype)

    def load_score(self):
         try:
             f = file(os.path.join(os.path.abspath('.'),
                                   'visualmatch.score'),"r")
             s = f.read().split(":")
             f.close
             self.vmw.low_score = int(s[1])
             print "low score is: %d" % (self.vmw.low_score)
         except:
             self.vmw.low_score = -1

    def save_score(self):
         print "saving low score: %d" % (int(self.vmw.low_score))        
         f = file(os.path.join(os.path.abspath('.'),'visualmatch.score'),"w")
         f.write("low_score:%s" % str(int(self.vmw.low_score)))
         f.close

    def set_title(self, title):
        self.win.set_title(title)

    def _new_game_cb(self, widget, game):
        window.new_game(self.vmw, game)
        return True

    def _robot_cb(self, widget):
        if self.vmw.robot is True:
            self.vmw.robot = False
        else:
            self.vmw.robot = True

    def _robot_time_cb(self, widget, time):
        self.vmw.robot_time = time

    def _number_card_O_cb(self, widget, numberO):
        self.vmw.numberO = numberO
        gencards.generate_number_cards(self.vmw.path,
                                       self.vmw.numberO,
                                       self.vmw.numberC)
        self.vmw.cardtype = ''
        window.new_game(self.vmw, 'number')

    def _number_card_C_cb(self, widget, numberC):
        self.vmw.numberC = numberC
        gencards.generate_number_cards(self.vmw.path,
                                       self.vmw.numberO,
                                       self.vmw.numberC)
        self.vmw.cardtype = ''
        window.new_game(self.vmw, 'number')

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    VisualMatchMain()
    main()
