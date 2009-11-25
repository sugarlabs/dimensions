#Copyright (c) 2009, Walter Bender
#Copyright (c) 2009, Michele Pratusevich

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

try:
   from sugar.graphics import style
   GRID_CELL_SIZE = style.GRID_CELL_SIZE
except:
   GRID_CELL_SIZE = 0

from grid import *
from card import *

from math import sqrt

CARD_W = 55
CARD_H = 125

class taWindow: pass

#
# handle launch from both within and without of Sugar environment
#
def new_window(canvas, path, parent=None):
   tw = taWindow()
   tw.path = path
   tw.activity = parent

   # starting from command line
   # we have to do all the work that was done in CardSortActivity.py
   if parent is None:
       tw.sugar = False
       tw.canvas = canvas

   # starting from Sugar
   else:
       tw.sugar = True
       tw.canvas = canvas
       parent.show_all()

   tw.canvas.set_flags(gtk.CAN_FOCUS)
   tw.canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
   tw.canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
   tw.canvas.connect("expose-event", _expose_cb, tw)
   tw.canvas.connect("button-press-event", _button_press_cb, tw)
   tw.canvas.connect("button-release-event", _button_release_cb, tw)
   tw.canvas.connect("key_press_event", _keypress_cb, tw)
   tw.width = gtk.gdk.screen_width()
   tw.height = gtk.gdk.screen_height()-GRID_CELL_SIZE
   tw.card_w = CARD_W
   tw.card_h = CARD_H
   tw.scale = 0.8 * tw.height/(tw.card_h*3)
   tw.area = tw.canvas.window
   tw.gc = tw.area.new_gc()
   tw.cm = tw.gc.get_colormap()
   tw.msgcolor = tw.cm.alloc_color('black')
   tw.sprites = []

   # make the cards, the deck and start playing...
   tw.deck = Grid(tw)
   tw.deck.start(tw)

   # Start doing something
   tw.keypress = ""
   tw.press = -1
   tw.release = -1
   tw.start_drag = [0,0]

   # make an array of three cards that are clicked
   tw.clicked = [None, None, None]

   return tw

#
# Button press
#
def _button_press_cb(win, event, tw):
   win.grab_focus()
   x, y = map(int, event.get_coords())
   tw.start_drag = [x,y]
   spr = findsprite(tw,(x,y))
   if spr is None:
       tw.press = None
       tw.release = None
       return True
   # take note of card under button press
   tw.press = spr
   return True

#
# Button release
#
def _button_release_cb(win, event, tw):
   win.grab_focus()
   x, y = map(int, event.get_coords())
   spr = findsprite(tw,(x,y))
   if spr is None:
       tw.press = None
       tw.release = None
       return True
   # take note of card under button release
   tw.release = spr
   for a in tw.clicked:
       if (a is None) and (tw.clicked.index(a) <= 2):
           tw.clicked[tw.clicked.index(a)]= spr

   #check to see if it's a set
   if (set_check()):
       for a in tw.clicked:
           a = None
   return True

#
# Keypress
#
def _keypress_cb(area, event, tw):
   tw.keypress = gtk.gdk.keyval_name(event.keyval)
   return True

#
# Repaint
#
def _expose_cb(win, event, tw):
   redrawsprites(tw)
   return True

#
# callbacks
#
def _destroy_cb(win, event, tw):
   gtk.main_quit()

#
# Check whether three cards are a set based on the criteria that
# in all characteristics, either all cards are the same of all cards are different
#

def set_check(cardarray):
   for a in cardarray:
       if a is None:
           return False
       else:
           break

   if (cardarray[0].num == cardarray[1].num):
       if (cardarray[1].num != cardarray[2].num):
           return False
   else:
       if (cardarray[1].num == cardarray[2].num):
           return False

   if (cardarray[0].color == cardarray[1].color):
       if (cardarray[1].color != cardarray[2].color):
           return False
   else:
       if (cardarray[1].color == cardarray[2].color):
           return False

   if (cardarray[0].fill == cardarray[1].fill):
       if (cardarray[1].fill != cardarray[2].fill):
           return False
   else:
       if (cardarray[1].fill == cardarray[2].fill):
           return False

   if (cardarray[0].shape == cardarray[1].shape):
       if (cardarray[1].shape != cardarray[2].shape):
           return False
   else:
       if (cardarray[1].shape == cardarray[2].shape):
           return False
   return True
