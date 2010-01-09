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
import logging
_logger = logging.getLogger('visualmatch-activity')

try:
   from sugar.graphics import style
   GRID_CELL_SIZE = style.GRID_CELL_SIZE
except ImportError:
   GRID_CELL_SIZE = 0

from constants import *
from grid import *
from deck import *
from card import *
from sprites import *

difficulty_level = [LOW,HIGH]

class vmWindow: pass

#
# Handle launch from both within and without of Sugar environment.
#
def new_window(canvas, path, parent=None):
    vmw = vmWindow()
    vmw.path = path
    vmw.activity = parent

    # Starting from command line
    if parent is None:
        vmw.sugar = False
        vmw.canvas = canvas

    # Starting from Sugar
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
    scale = 0.8 * vmw.height/(CARD_HEIGHT*5.5)
    vmw.card_width = CARD_WIDTH*scale
    vmw.card_height = CARD_HEIGHT*scale
    vmw.sprites = Sprites(vmw.canvas)
    vmw.selected = []
    vmw.match_display_area = []
    vmw.clicked = [None, None, None]
    return vmw

#
# Start a new game.
#
def new_game(vmw, saved_state=None, deck_index=0):

    # If there is already a deck, hide it.
    if hasattr(vmw, 'deck'):
        vmw.deck.hide()

    # The first time through, initialize the deck, grid, and overlays.
    if not hasattr(vmw, 'grid'):
        vmw.grid = Grid(vmw.width, vmw.height, vmw.card_width, vmw.card_height)
        for i in range(0,3):
            vmw.selected.append(Card(vmw.sprites, vmw.path, "", vmw.card_width,
                                     vmw.card_height, [SELECTMASK,0,0,0]))
            vmw.match_display_area.append(Card(vmw.sprites, vmw.path, "",
                                               vmw.card_width,
                                               vmw.card_height,
                                               [MATCHMASK,0,0,0]))
            vmw.grid.display_match(vmw.match_display_area[i].spr, i) 

    _unselect(vmw)

    # Restore saved state on resume or share.
    if saved_state is not None:
        _logger.debug("Restoring state: %s" % (str(saved_state)))
        vmw.deck = Deck(vmw.sprites, vmw.path, vmw.cardtype, vmw.card_width, 
                        vmw.card_height, difficulty_level[vmw.level])
        vmw.deck.hide()
        vmw.deck.index = deck_index
        deck_start = ROW*COL+3
        deck_stop = deck_start+vmw.deck.count()
        vmw.deck.restore(saved_state[deck_start:deck_stop])
        vmw.grid.restore(vmw.deck, saved_state[0:ROW*COL])
        _restore_selected(vmw, saved_state[ROW*COL:ROW*COL+3])
        _restore_matches(vmw, saved_state[deck_stop:deck_stop+3*vmw.matches])
    elif not joiner(vmw):
        _logger.debug("Starting new game.")
        vmw.deck = Deck(vmw.sprites, vmw.path, vmw.cardtype, 
                        vmw.card_width, vmw.card_height, 
                        difficulty_level[vmw.level])
        vmw.deck.hide()
        vmw.deck.shuffle()
        vmw.grid.deal(vmw.deck)
        if _find_a_match(vmw) is False:
            vmw.grid.deal_extra_cards(vmw.deck)
        vmw.matches = 0
        vmw.robot_matches = 0
        vmw.match_list = []
        vmw.total_time = 0

    # When sharer starts a new game, joiners should be notified.
    if sharer(vmw):
        vmw.activity._send_event("J")

    _update_labels(vmw)
    if _game_over(vmw):
        if hasattr(vmw,'timeout_id') and vmw.timeout_id is not None:
            gobject.source_remove(vmw.timeout_id)
    else:
        if hasattr(vmw,'match_timeout_id') and vmw.match_timeout_id is not None:
            gobject.source_remove(vmw.match_timeout_id)
        _timer_reset(vmw)

def joiner(vmw):
    if vmw.sugar is True and \
        hasattr(vmw.activity, 'chattube') and \
        vmw.activity.chattube is not None and \
        vmw.activity.initiating is False:
        return True
    return False

def sharer(vmw):
    if vmw.sugar is True and \
        hasattr(vmw.activity, 'chattube') and \
        vmw.activity.chattube is not None and \
        vmw.activity.initiating is True:
        return True
    return False

#
# Button press
#
def _button_press_cb(win, event, vmw):
    win.grab_focus()
    return True

#
# Button release
#
def _button_release_cb(win, event, vmw):
    win.grab_focus()
    x, y = map(int, event.get_coords())
    spr = vmw.sprites.find_sprite((x, y))
    if spr is None:
        return True
    if vmw.sugar is True and \
        hasattr(vmw.activity, 'chattube') and \
        vmw.activity.chattube is not None:
        if vmw.deck.spr_to_card(spr) is not None:
            vmw.activity._send_event("B:"+str(vmw.deck.spr_to_card(spr).index))
        i =  _selected(vmw, spr)
        if i is not -1:
            vmw.activity._send_event("S:"+str(i))
    return _process_selection(vmw, spr)

def _selected(vmw, spr):
    for i in range(3):
        if vmw.selected[i].spr == spr:
            return i
    return -1

def _process_selection(vmw, spr):
    # Make sure a card in the matched pile isn't selected.
    if spr.x == MATCH_POSITION:
       return True

    # Make sure that the current card isn't already selected.
    i = _selected(vmw, spr)
    if i is not -1:
        # On a second click, unselect it.
        vmw.clicked[i] = None
        vmw.selected[i].hide_card()
        return True

    # Otherwise highlight the card with a selection mask.
    for a in vmw.clicked:
        if a is None:
            i = vmw.clicked.index(a)
            vmw.clicked[i] = spr
            vmw.selected[i].spr.x = spr.x
            vmw.selected[i].spr.y = spr.y
            vmw.selected[i].show_card()
            break

    # If we have three cards selected, test for a match.
    if None not in vmw.clicked:
        _test_for_a_match(vmw)
    return True

#
# Game is over when the deck is empty and there are no more matches.
#
def _game_over(vmw):
    if vmw.deck.empty() and _find_a_match(vmw) is False:
        set_label(vmw,"deck","")
        set_label(vmw,"clock","")
        set_label(vmw,"status","%s (%d:%02d)" % 
            (_("Game over"),int(vmw.total_time/60),int(vmw.total_time%60)))
        vmw.match_timeout_id = gobject.timeout_add(2000,_show_matches,vmw,0)
        return True
    return False

#
# Lots of work to do if we have a match
#
def _test_for_a_match(vmw):
    if _match_check([vmw.deck.spr_to_card(vmw.clicked[0]),
                    vmw.deck.spr_to_card(vmw.clicked[1]),
                    vmw.deck.spr_to_card(vmw.clicked[2])],
                   vmw.cardtype):

        # Stop the timer.
        if vmw.timeout_id is not None:
            gobject.source_remove(vmw.timeout_id)
        vmw.total_time += gobject.get_current_time()-vmw.start_time

        # Increment the match counter and add the match to the match list.
        vmw.matches += 1
        for i in vmw.clicked:
            vmw.match_list.append(i)

        # Remove the match and deal three new cards.
        vmw.grid.remove_and_replace(vmw.clicked, vmw.deck)
        set_label(vmw, "deck", "%d %s" % 
                (vmw.deck.cards_remaining(), _("cards")))

        # Test to see if the game is over.
        if _game_over(vmw):
            gobject.source_remove(vmw.timeout_id)
            _unselect(vmw)
            if vmw.low_score[vmw.level] == -1:
                vmw.low_score[vmw.level] = vmw.total_time
            elif vmw.total_time < vmw.low_score[vmw.level]:
                vmw.low_score[vmw.level] = vmw.total_time
                set_label(vmw,"status","%s (%d:%02d)" % 
                    (_("New record"),int(vmw.total_time/60),
                     int(vmw.total_time%60)))
            if vmw.sugar is False:
                 vmw.activity.save_score()
            return True

        # Consolidate the grid.
        vmw.grid.consolidate()

        # Test to see if we need to deal extra cards.
        if _find_a_match(vmw) is False:
            vmw.grid.deal_extra_cards(vmw.deck)

        # Keep playing.
        _update_labels(vmw)
        _timer_reset(vmw)

    # Whether or not there was a match, unselect all cards.
    _unselect(vmw)

#
# Unselect the cards
#
def _unselect(vmw):
     vmw.clicked = [None, None, None]
     for a in vmw.selected:
         a.hide_card()

#
# Callbacks
#
def _keypress_cb(area, event, vmw):
    k = gtk.gdk.keyval_name(event.keyval)
    if k in KEYMAP:
        return _process_selection(vmw, vmw.grid.grid_to_spr(KEYMAP.index(k)))
    return True

def _expose_cb(win, event, vmw):
    vmw.sprites.redraw_sprites()
    return True

def _destroy_cb(win, event, vmw):
    gtk.main_quit()

#
# Write strings to a label in the toolbar.
#
def _update_labels(vmw):
    set_label(vmw, "deck", "%d %s" % 
        (vmw.deck.cards_remaining(), _("cards")))
    set_label(vmw, "status", "")
    if vmw.matches == 1:
        if vmw.robot_matches > 0:
            set_label(vmw,"match","%d (%d) %s" % \
                (vmw.matches-vmw.robot_matches,vmw.robot_matches,_("match")))
        else:
            set_label(vmw,"match","%d %s" % (vmw.matches,_("match")))
    else:
        if vmw.robot_matches > 0:
            set_label(vmw,"match","%d (%d) %s" % \
                (vmw.matches-vmw.robot_matches,vmw.robot_matches,_("matches")))
        else:
            set_label(vmw,"match","%d %s" % (vmw.matches,_("matches")))

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
# Restore the selected cards upon resume or share.
#
def _restore_selected(vmw, saved_selected_indices):
    j = 0
    for i in saved_selected_indices:
        if i is None:
            vmw.clicked[j] = None
        else:
            vmw.clicked[j] = vmw.deck.index_to_card(i).spr
            k = vmw.grid.spr_to_grid(vmw.clicked[j])
            vmw.selected[j].spr.x = vmw.grid.grid_to_xy(k)[0]
            vmw.selected[j].spr.y = vmw.grid.grid_to_xy(k)[1]
            vmw.selected[j].show_card()
        j += 1

#
# Restore the match list upon resume or share.
#
def _restore_matches(vmw, saved_match_list_indices):
    j = 0
    vmw.match_list = []
    for i in saved_match_list_indices:
        if i is not None:
            vmw.match_list.append(vmw.deck.index_to_card(i).spr)
    if vmw.matches > 0:
        l = len(vmw.match_list)
        for j in range(3):
            vmw.grid.display_match(vmw.match_list[l-3+j], j) 

#
# Display of seconds since start_time.
#
def _counter(vmw):
     seconds = int(gobject.get_current_time()-vmw.start_time)
     set_label(vmw,"clock",str(seconds))
     if vmw.robot is True and vmw.robot_time < seconds:
         _find_a_match(vmw, True)
     else:
         vmw.timeout_id = gobject.timeout_add(1000,_counter,vmw)

def _timer_reset(vmw):
    vmw.start_time = gobject.get_current_time()
    vmw.timeout_id = None
    _counter(vmw)

#
# Show all the matches as a simple animation.
#
def _show_matches(vmw, i):
    if i < vmw.matches:
        for j in range(3):
            vmw.grid.display_match(vmw.match_list[i*3+j], j) 
        vmw.match_timeout_id = gobject.timeout_add(2000,_show_matches,vmw,i+1)

#
# Check to see whether there are any matches on the board.
#
def _find_a_match(vmw, robot_match=False):
     a = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
     for i in Permutation(a): # TODO: really should be combination
         cardarray = [vmw.grid.grid[i[0]],\
                      vmw.grid.grid[i[1]],\
                      vmw.grid.grid[i[2]]]
         if _match_check(cardarray, vmw.cardtype) is True:
             if robot_match is True:
                 for j in range(3):
                     vmw.clicked[j]=vmw.grid.grid[i[j]].spr
                 vmw.robot_matches += 1
                 _test_for_a_match(vmw)
             return True
     return False

#
# For each attribute, either it is the same or different on every card.
#
def _match_check(cardarray, cardtype):
    for a in cardarray:
        if a is None:
            return False

    if (cardarray[0].shape + cardarray[1].shape + cardarray[2].shape)%3 != 0:
        return False
    if (cardarray[0].color + cardarray[1].color + cardarray[2].color)%3 != 0:
        return False
    if (cardarray[0].fill + cardarray[1].fill + cardarray[2].fill)%3 != 0:
       return False
    # Special case: only check number when shapes are the same
    if cardtype == 'word':
        if cardarray[0].shape == cardarray[1].shape and \
           cardarray[0].shape == cardarray[2].shape and \
           (cardarray[0].num + cardarray[1].num + cardarray[2].num)%3 != 0:
            return False
    else:
        if (cardarray[0].num + cardarray[1].num + cardarray[2].num)%3 != 0:
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

