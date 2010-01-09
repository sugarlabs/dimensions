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
import random

from sprites import *
from card import *
from deck import *

from constants import *

#
# Class for managing ROWxCOL matrix of cards
#
class Grid:
    def __init__(self, width, height, card_width, card_height):
        # The playing surface
        self.grid = []
        for i in range(ROW*COL):
            self.grid.append(None)
        # Card spacing
        self.left = int((width-(card_width*2))/2)
        self.xinc = int(card_width*1.2)
        self.top = 10
        self.yinc = int(card_height*1.33)

    # Deal an initial set of cards.
    def deal(self, deck):
        for i in range(ROW*COL):
            if i < (ROW-1)*COL:
                self.grid[i] = deck.deal_next_card()
                self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                                  self.grid_to_xy(i)[1])
            else:         # Leave a blank row for extra cards at the bottom.
                self.grid[i] = None

    # Add cards to the bottom row when there is no match.
    def deal_extra_cards(self, deck):
        # But only if there are still cards in the deck
        #         and only 12 cards in the grid
        if deck.empty() is False and self.cards_in_grid() == DEAL:
            for c in range(0,COL):
                i = self.grid.index(None)
                self.grid[i] = deck.deal_next_card()
                self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                                  self.grid_to_xy(i)[1])

    # How many cards are on the grid?
    def cards_in_grid(self):
        return ROW*COL-self.grid.count(None)

    # Restore cards to grid upon resume or share.
    def restore(self, deck, saved_card_index):
        self.hide()
        j = 0
        for i in saved_card_index:
            if i is None:
                self.grid[j] = None
            else:
                self.grid[j] = deck.index_to_card(i)
            j += 1
        self.show()

    # Remove a match from the grid and replace it with new cards from the deck.
    def remove_and_replace(self, clicked_set, deck):
        for a in clicked_set:
            # Move the match to the match display area
            self.display_match(a, clicked_set.index(a))
            # Find the index into the grid of the match card
            i = self.spr_to_grid(a)
            # Don't add new cards if bottom row is occupied
            if self.cards_in_grid() == DEAL:
                if deck.empty():
                    self.grid[i] = None
                else:
                    # Put new card in grid position of card we are replacing.
                    self.grid[i] = deck.deal_next_card()
                    self.place_a_card(self.grid[i],
                                      self.grid_to_xy(i)[0],
                                      self.grid_to_xy(i)[1])
            else:
                # Mark as empty the grid positions we are not refilling
                self.grid[i] = None

    # Move card to the match area.
    def display_match(self, spr, i):
        spr.move((MATCH_POSITION, self.top + i*self.yinc))
        spr.set_layer(2000)

    # If we have removed cards from an expanded grid, we have to consolidate.
    def consolidate(self):
        for j in range((ROW-1)*COL,ROW*COL):
            i = 0
            while(self.grid[j] is not None):
                if self.grid[i] is None:
                    self.grid[i] = self.grid[j]
                    self.grid[i].spr.move(self.grid_to_xy(i))
                    self.grid[i].spr.set_layer(2000)
                    self.grid[j] = None
                else:
                    i+=1

    # Place a card at position x,y and display it.
    def place_a_card(self, c, x, y):
        if c is not None:
            c.spr.x = x
            c.spr.y = y
            c.show_card()

    # Convert from sprite x,y to grid index.
    def xy_to_grid(self, x, y):
        return int(COL*(y-self.top)/self.yinc) + int((x-self.left)/self.xinc)

    # Convert from grid index to sprite x,y.
    def grid_to_xy(self, i):
        return ((self.left+i%COL*self.xinc),(self.top+(i/COL)*self.yinc))

    # Return the sprite in grid-position i.
    def grid_to_spr(self, i):
        return self.grid[i].spr

    # Return the index of a sprite in grid.
    def spr_to_grid(self, spr):
        for i in range(ROW*COL):
            if self.grid[i] is not None and self.grid[i].spr == spr:
                return(i)
        return None

    # Hide all of the cards on the grid.
    def hide(self):
        for i in range(ROW*COL):
            if self.grid[i] is not None:
                self.grid[i].hide_card()

    # Restore all card on the grid to their x,y positions.
    def show(self):
        for i in range(ROW*COL):
            self.place_a_card(self.grid[i],self.grid_to_xy(i)[0],
                              self.grid_to_xy(i)[1])
  
