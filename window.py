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

class vmWindow: pass

#
# handle launch from both within and without of Sugar environment
#
def new_window(canvas, path, cardtype, parent=None):
    vmw = vmWindow()
    vmw.path = path
    vmw.activity = parent

    # starting from command line
    # we have to do all the work that was done in CardSortActivity.py
    if parent is None:
        vmw.sugar = False
        vmw.canvas = canvas

    # starting from Sugar
    else:
        vmw.sugar = True
        vmw.canvas = canvas
        parent.show_all()

    vmw.canvas.set_flags(gtk.CAN_FOCUS)
    vmw.canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
    vmw.canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
    vmw.canvas.connect("expose-event", _expose_cb, vmw)
    vmw.canvas.connect("button-press-event", _button_press_cb, vmw)
    vmw.canvas.connect("button-release-event", _button_release_cb, vmw)
    vmw.canvas.connect("key_press_event", _keypress_cb, vmw)
    vmw.width = gtk.gdk.screen_width()
    vmw.height = gtk.gdk.screen_height()-GRID_CELL_SIZE
    vmw.card_w = CARD_W
    vmw.card_h = CARD_H
    vmw.cardtype = cardtype
    vmw.scale = 0.8 * vmw.height/(vmw.card_h*5.5)
    vmw.area = vmw.canvas.window
    vmw.gc = vmw.area.new_gc()
    vmw.cm = vmw.gc.get_colormap()
    vmw.msgcolor = vmw.cm.alloc_color('black')
    vmw.sprites = []
    vmw.selected = []

    # a place to put the matched cards
    vmw.match_field = [Card(vmw,MATCHMASK,0,0,0),\
                       Card(vmw,MATCHMASK,0,0,0),\
                       Card(vmw,MATCHMASK,0,0,0)]

    # create a deck of cards, shuffle, and then deal
    vmw.deck = Deck(vmw)
    vmw.grid = Grid(vmw)

    for i in range(0,3):
       vmw.match_field[i].spr.x = 10
       vmw.match_field[i].spr.y = vmw.grid.top+i*vmw.grid.yinc
       vmw.match_field[i].show_card()

    # initialize three card-selected overlays
    for i in range(0,3):
        vmw.selected.append(Card(vmw,SELECTMASK,0,0,0))

    # make an array of three cards that are clicked
    vmw.clicked = [None, None, None]

    # Start doing something
    vmw.low_score = -1
    vmw.keypress = ""
    new_game(vmw, cardtype)
    return vmw

#
# Initialize for a new game
#
def new_game(vmw,cardtype):
    vmw.deck.hide()
    if vmw.cardtype is not cardtype:
        vmw.cardtype = cardtype
        vmw.deck = Deck(vmw)
    vmw.deck.shuffle()
    vmw.grid.deal(vmw)
    if find_a_match(vmw) is False:
        vmw.grid.deal_extra_cards(vmw)            
    vmw.matches = 0
    vmw.total_time = 0
    set_label(vmw, "deck", "%d %s" % 
        (vmw.deck.count-vmw.deck.index, _("cards remaining")))
    set_label(vmw,"match","%d %s" % (vmw.matches,_("matches")))
    vmw.start_time = gobject.get_current_time()
    vmw.timeout_id = None
    _counter(vmw)

#
# Button press
#
def _button_press_cb(win, event, vmw):
    win.grab_focus()
    return True

#
# Button release, where all the work is done
#
def _button_release_cb(win, event, vmw):
    win.grab_focus()
    x, y = map(int, event.get_coords())
    spr = findsprite(vmw,(x,y))
    if spr is None:
        return True

    # check to make sure a card in the matched pile isn't selected
    if spr.x == 10:
       return True

    # check to make sure that the current card isn't already selected
    for a in vmw.clicked:
        if a is spr:
            # on second click, unselect
            i = vmw.clicked.index(a)
            vmw.clicked[i] = None
            vmw.selected[i].hide_card()
            return True

    # add the selected card to the list
    # and highlight it with the selection mask
    for a in vmw.clicked:
        if a is None:
            i = vmw.clicked.index(a)
            vmw.clicked[i] = spr
            vmw.selected[i].spr.x = spr.x
            vmw.selected[i].spr.y = spr.y
            vmw.selected[i].show_card()
            break # we only want to add the card to the list once

    # if we have three cards selected, test for a match
    if None in vmw.clicked:
        pass
    else:
        if match_check([vmw.deck.spr_to_card(vmw.clicked[0]),
                        vmw.deck.spr_to_card(vmw.clicked[1]),
                        vmw.deck.spr_to_card(vmw.clicked[2])],
                       vmw.cardtype):
            # stop the timer
            if vmw.timeout_id is not None:
                gobject.source_remove(vmw.timeout_id)
            vmw.total_time += gobject.get_current_time()-vmw.start_time
            # out with the old and in with the new
            vmw.grid.remove_and_replace(vmw.clicked, vmw)
            set_label(vmw, "deck", "%d %s" % 
                    (vmw.deck.count-vmw.deck.index, _("cards remaining")))
            # test to see if the game is over
            if vmw.deck.empty():
                if find_a_match(vmw) is False:
                    set_label(vmw,"deck","")
                    set_label(vmw,"clock","")
                    set_label(vmw,"status","%s (%d:%02d)" % 
                        (_("Game over"),int(vmw.total_time/60),
                         int(vmw.total_time%60)))
                    gobject.source_remove(vmw.timeout_id)
                    unselect(vmw)
                    if vmw.low_score == -1:
                        vmw.low_score = vmw.total_time
                    elif vmw.total_time < vmw.low_score:
                        vmw.low_score = vmw.total_time
                        set_label(vmw,"status","%s (%d:%02d)" % 
                            (_("New record"),int(vmw.total_time/60),
                             int(vmw.total_time%60)))
                    if vmw.sugar is False:
                         vmw.activity.save_score()
                    return True
            # test to see if we need to deal extra cards
            if find_a_match(vmw) is False:
                vmw.grid.deal_extra_cards(vmw)            
            else:
                # set_label(vmw,"status",vmw.msg)
                set_label(vmw,"status",_("match"))
            vmw.matches += 1
            if vmw.matches == 1:
                set_label(vmw,"match","%d %s" % (vmw.matches,_("match")))
            else:
                set_label(vmw,"match","%d %s" % (vmw.matches,_("matches")))
            # reset the timer
            vmw.start_time = gobject.get_current_time()
            vmw.timeout_id = None
            _counter(vmw)
        else:
            set_label(vmw,"status",_("no match"))
        unselect(vmw)
    return True

#
# unselect the cards
#
def unselect(vmw):
     vmw.clicked = [None, None, None]
     for a in vmw.selected:
         a.hide_card()

#
# Keypress
#
def _keypress_cb(area, event, vmw):
    vmw.keypress = gtk.gdk.keyval_name(event.keyval)
    return True

#
# Repaint
#
def _expose_cb(win, event, vmw):
    redrawsprites(vmw)
    return True

#
# callbacks
#
def _destroy_cb(win, event, vmw):
    gtk.main_quit()

#
# write a string to a label in the toolbar
def set_label(vmw, label, s):
    if vmw.sugar is True:
        if label == "deck":
            vmw.activity.deck_label.set_text(s)
        elif label == "status":
            vmw.activity.status_label.set_text(s)
        elif label == "clock":
            vmw.activity.clock_label.set_text(s)
        elif label == "match":
            vmw.activity.match_label.set_text(s)
    else:
        if hasattr(vmw,"win") and label is not "clock":
            vmw.win.set_title("%s: %s" % (_("Visual Match"),s))

#
# Display # of seconds since start_time
#
def _counter(vmw):
     set_label(vmw,"clock",str(int(gobject.get_current_time()-\
                                              vmw.start_time)))
     vmw.timeout_id = gobject.timeout_add(1000,_counter,vmw)

#
# Check to see whether there are any matches on the board
#
def find_a_match(vmw):
     a = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
     for i in Permutation(a): # really should be Combination
         cardarray = [vmw.grid.grid[i[0]],\
                      vmw.grid.grid[i[1]],\
                      vmw.grid.grid[i[2]]]
         if match_check(cardarray, vmw.cardtype) is True:
             vmw.msg = str(i)
             return True
     return False

#
# Check whether three cards are a match based on the criteria that
# in all characteristics:
# either all cards are the same of all cards are different
#
def match_check(cardarray, cardtype):
    for a in cardarray:
        if a is None:
            return False

    if (cardarray[0].num + cardarray[1].num + cardarray[2].num)%3 != 0:
        return False
    if (cardarray[0].color + cardarray[1].color + cardarray[2].color)%3 != 0:
        return False
    # special case for the word game
    # only check fill when numbers are the same
    if cardtype == 'word':
        if cardarray[0].num == cardarray[1].num and \
           cardarray[0].num == cardarray[2].num and \
           (cardarray[0].fill + cardarray[1].fill + cardarray[2].fill)%3 != 0:
            return False
    else:
        if (cardarray[0].fill + cardarray[1].fill + cardarray[2].fill)%3 != 0:
            return False
    if (cardarray[0].shape + cardarray[1].shape + cardarray[2].shape)%3 != 0:
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

