#Copyright (c) 2009,10 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import pygtk
pygtk.require('2.0')
import gtk
import random

from constants import ROW, COL


class Grid:
    """ Class for managing ROWxCOL matrix of cards """

    def __init__(self, width, height, card_width, card_height):
        """ Initialize the playing surface """
        self.grid = []
        for i in range(ROW * COL):
            self.grid.append(None)
        # Card spacing
        self.left = int((width - (card_width * 2)) / 2)
        self.xinc = int(card_width * 1.2)
        self.top = 10
        self.yinc = int(card_height * 1.33)

    def deal(self, deck):
        """ Deal an initial set of cards. """
        for i in range(ROW * COL):
            if i < (ROW - 1) * COL:
                self.grid[i] = deck.deal_next_card()
                self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                                  self.grid_to_xy(i)[1])
            else:         # Leave a blank row for extra cards at the bottom.
                self.grid[i] = None

    def deal_extra_cards(self, deck):
        """ Add cards to the bottom row when there is no match.
            But only if there are still cards in the deck
            and only 12 cards in the grid
        """
        if deck.empty() is False and self.cards_in_grid() == DEAL:
            for c in range(0, COL):
                i = self.grid.index(None)
                self.grid[i] = deck.deal_next_card()
                self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                                  self.grid_to_xy(i)[1])

    def cards_in_grid(self):
        """ How many cards are on the grid? """
        return ROW * COL - self.grid.count(None)

    def restore(self, deck, saved_card_index):
        """ Restore cards to grid upon resume or share. """
        self.hide()
        j = 0
        for i in saved_card_index:
            if i is None:
                self.grid[j] = None
            else:
                self.grid[j] = deck.index_to_card(i)
            j += 1
        self.show()

    def remove_and_replace(self, clicked_set, deck):
        """ Remove a match from the grid and replace with new cards. """
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

    def display_match(self, spr, i):
        """ Move card to the match area. """
        spr.move((MATCH_POSITION, self.top + i * self.yinc))
        spr.set_layer(2000)

    def consolidate(self):
        """ If we have removed cards from an expanded grid,
            we have to consolidate.
        """
        for j in range((ROW - 1) * COL, ROW * COL):
            i = 0
            while(self.grid[j] is not None):
                if self.grid[i] is None:
                    self.grid[i] = self.grid[j]
                    self.grid[i].spr.move(self.grid_to_xy(i))
                    self.grid[i].spr.set_layer(2000)
                    self.grid[j] = None
                else:
                    i += 1

    def place_a_card(self, c, x, y):
        """ Place a card at position x,y and display it. """
        if c is not None:
            c.spr.move((x, y))
            c.show_card()

    def xy_to_grid(self, x, y):
        """ Convert from sprite x,y to grid index. """
        return int(COL * (y - self.top) / self.yinc)\
            + int((x - self.left) / self.xinc)

    def grid_to_xy(self, i):
        """ Convert from grid index to sprite x,y. """
        return ((self.left + i % COL * self.xinc),
                (self.top + (i / COL) * self.yinc))

    def grid_to_spr(self, i):
        """ Return the sprite in grid-position i. """
        return self.grid[i].spr

    def spr_to_grid(self, spr):
        """ Return the index of a sprite in grid. """
        for i in range(ROW * COL):
            if self.grid[i] is not None and self.grid[i].spr == spr:
                return(i)
        return None

    def hide(self):
        """ Hide all of the cards on the grid. """
        for i in range(ROW * COL):
            if self.grid[i] is not None:
                self.grid[i].hide_card()

    def show(self):
        """ Restore all card on the grid to their x,y positions. """
        for i in range(ROW * COL):
            self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                              self.grid_to_xy(i)[1])
