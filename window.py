#Copyright (c) 2009, Walter Bender
#Copyright (c) 2009, Michele Pratusevich
#Copyright (c) 2009, Vincent Le

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
from gettext import gettext as _

try:
   from sugar.graphics import style
   GRID_CELL_SIZE = style.GRID_CELL_SIZE
except:
   GRID_CELL_SIZE = 0

from constants import *
from grid import *
from deck import *
from card import *

from math import sqrt

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
    tw.scale = 0.8 * tw.height/(tw.card_h*3.5)
    tw.area = tw.canvas.window
    tw.gc = tw.area.new_gc()
    tw.cm = tw.gc.get_colormap()
    tw.msgcolor = tw.cm.alloc_color('black')
    tw.sprites = []
    tw.selected = []

    tw.match_field = [Card(tw,MATCHMASK,0,0,0),\
                      Card(tw,MATCHMASK,0,0,0),\
                      Card(tw,MATCHMASK,0,0,0)]

    # create a deck of cards, shuffle, and then deal
    tw.deck = Deck(tw)
    tw.grid = Grid(tw)

    for i in range(0,3):
       tw.match_field[i].spr.x = 10
       tw.match_field[i].spr.y = tw.grid.top+i*tw.grid.yinc
       tw.match_field[i].show_card()

    # initialize three card-selected overlays
    for i in range(0,3):
        tw.selected.append(Card(tw,SELECTMASK,0,0,0))

    # make an array of three cards that are clicked
    tw.clicked = [None, None, None]

    # Start doing something
    tw.low_score = -1
    tw.keypress = ""
    new_game(tw)
    return tw

#
# Initialize for a new game
#
def new_game(tw):
    tw.deck.shuffle()
    tw.grid.deal(tw)
    tw.matches = 0
    tw.total_time = 0
    set_label(tw, "deck", "%d %s" % 
        (tw.deck.count-tw.deck.index, _("cards remaining")))
    set_label(tw,"match","%d %s" % (tw.matches,_("matches")))
    tw.start_time = gobject.get_current_time()
    tw.timeout_id = None
    _counter(tw)

#
# Button press
#
def _button_press_cb(win, event, tw):
    win.grab_focus()
    return True

#
# Button release, where all the work is done
#
def _button_release_cb(win, event, tw):
    win.grab_focus()
    x, y = map(int, event.get_coords())
    spr = findsprite(tw,(x,y))
    if spr is None:
        return True

    # check to make sure a card in the matched pile isn't selected
    if spr.x == 10:
       return True

    # check to make sure that the current card isn't already selected
    for a in tw.clicked:
        if a is spr:
            # on second click, unselect
            i = tw.clicked.index(a)
            tw.clicked[i] = None
            tw.selected[i].hide_card()
            return True

    # add the selected card to the list
    # and show the selection mask
    for a in tw.clicked:
        if a is None:
            i = tw.clicked.index(a)
            tw.clicked[i] = spr
            tw.selected[i].spr.x = spr.x
            tw.selected[i].spr.y = spr.y
            tw.selected[i].show_card()
            break # we only want to add the card to the list once

    # if we have three cards selected, test for a set
    #check to see if it's a set
    if None in tw.clicked:
        pass
    else:
        if match_check([tw.deck.spr_to_card(tw.clicked[0]),
                      tw.deck.spr_to_card(tw.clicked[1]),
                      tw.deck.spr_to_card(tw.clicked[2])]):
            # stop the timer
            if tw.timeout_id is not None:
                gobject.source_remove(tw.timeout_id)
            tw.total_time += gobject.get_current_time()-tw.start_time
            # out with the old and in with the new
            tw.grid.remove_and_replace(tw.clicked, tw)
            set_label(tw, "deck", "%d %s" % 
                    (tw.deck.count-tw.deck.index, _("cards remaining")))
            # test to see if the game is over
            if tw.deck.empty():
                if find_a_match(tw) is False:
                    set_label(tw,"deck","")
                    set_label(tw,"clock","")
                    set_label(tw,"status","%s (%d %s)" % 
                        (_("Game over"),int(tw.total_time),_("seconds")))
                    gobject.source_remove(tw.timeout_id)
                    unselect(tw)
                    if tw.low_score == -1:
                        tw.low_score = tw.total_time
                    elif tw.total_time < tw.low_score:
                        tw.low_score = tw.total_time
                        set_label(tw,"status","%s (%d %s)" % 
                            (_("New record"),int(tw.total_time),_("seconds")))
                    if tw.sugar is False:
                         tw.activity.save_score()
                    return True
            # test to see if we need to deal extra cards
            if find_a_match(tw) is False:
                tw.grid.deal_extra_cards(tw)            
            tw.matches += 1
            set_label(tw,"status",_("match"))
            if tw.matches == 1:
                set_label(tw,"match","%d %s" % (tw.matches,_("match")))
            else:
                set_label(tw,"match","%d %s" % (tw.matches,_("matches")))
            # reset the timer
            tw.start_time = gobject.get_current_time()
            tw.timeout_id = None
            _counter(tw)
        else:
            set_label(tw,"status",_("no match"))
        unselect(tw)
    return True

#
# unselect the cards
#
def unselect(tw):
     tw.clicked = [None, None, None]
     for a in tw.selected:
         a.hide_card()


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
# write a string to a label in the toolbar
def set_label(tw, label, s):
    if tw.sugar is True:
        if label == "deck":
            tw.activity.deck_label.set_text(s)
        elif label == "status":
            tw.activity.status_label.set_text(s)
        elif label == "clock":
            tw.activity.clock_label.set_text(s)
        elif label == "match":
            tw.activity.match_label.set_text(s)
    else:
        if hasattr(tw,"win") and label is not "clock":
            tw.win.set_title("%s: %s" % (_("Visual Match"),s))

#
# Display # of seconds since start_time
#
def _counter(tw):
     set_label(tw,"clock",str(int(gobject.get_current_time()-\
                                              tw.start_time)))
     tw.timeout_id = gobject.timeout_add(1000,_counter,tw)

#
# Check to see whether there are any matches on the board
#
def find_a_match(tw):
     a = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
     for i in Permutation(a): # really should be Combination
         cardarray = [tw.grid.grid[i[0]],tw.grid.grid[i[1]],tw.grid.grid[i[2]]]
         if match_check(cardarray) is True:
             tw.msg = str(i)
             return True
     return False

#
# Check whether three cards are a match based on the criteria that
# in all characteristics:
# either all cards are the same of all cards are different
#
def match_check(cardarray):
    for a in cardarray:
        if a is None:
            return False

    if (cardarray[0].num + cardarray[1].num + cardarray[2].num)%3 != 0:
       return False
    if (cardarray[0].fill + cardarray[1].fill + cardarray[2].fill)%3 != 0:
       return False
    if (cardarray[0].shape + cardarray[1].shape + cardarray[2].shape)%3 != 0:
       return False
    if cardarray[0].color == cardarray[1].color and \
       cardarray[1].color != cardarray[2].color:
       return False
    if cardarray[0].color != cardarray[1].color and \
       cardarray[1].color != cardarray[2].color and \
       cardarray[0].color == cardarray[2].color:
       return False
    if cardarray[0].color != cardarray[1].color and \
       cardarray[1].color == cardarray[2].color and \
       cardarray[0].color != cardarray[2].color:
       return False
    if cardarray[0].color == cardarray[1].color and \
       cardarray[1].color == cardarray[2].color and \
       cardarray[0].color != cardarray[2].color:
       return False
    return True

#
# Permutaion class for checking for all possible matches on the grid
#    
class Permutation: 
     def __init__(self, justalist): 
         self._data = justalist[:] 
         self._sofar = [] 
     def __iter__(self): 
         return self.next() 
     def next(self): 
          for elem in self._data: 
              if elem not in self._sofar: 
                  self._sofar.append(elem) 
                  if len(self._sofar) == 3: 
                      yield self._sofar[:] 
                  else: 
                      for v in self.next(): 
                          yield v 
                  self._sofar.pop() 

