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

ROW = 5
COL = 3

#
# class for managing 3x5 matrix of cards
#
class Grid:
    def __init__(self, vmw):
        # the playing surface is a 3x5 grid
        self.grid = []
        # how many cards are on the playing field
        self.cards = 0
        # card spacing
        self.left = int((vmw.width-(vmw.card_w*2*vmw.scale))/2)
        self.xinc = int(vmw.card_w*1.2*vmw.scale)
        # self.top = int((vmw.height-(vmw.card_h*3.5*vmw.scale))/2)
        self.top = 10
        self.yinc = int(vmw.card_h*1.33*vmw.scale)

    # deal the initial deck of cards
    def deal(self, vmw):
        # find upper left corner of grid
        self.cards = 0
        self.grid = []
        x = self.left
        y = self.top
        for r in range(0,ROW-1):
            for c in range(0,COL):
                a = vmw.deck.deal_next_card()
                self.grid.append(a)
                self.place_a_card(a,x,y)
                x += self.xinc
                self.cards += 1
            x = self.left
            y += self.yinc
        for c in range(0,COL):
            # leave a blank row for extra cards
            self.grid.append(None)

    # add cards when there is no match
    def deal_extra_cards(self, vmw):
        # if there are still cards in the deck and only 12 cards in the grid
        if vmw.deck.empty() is False and self.cards == DEAL:
            # add three extra cards to the playing field
            for c in range(0,COL):
                i = self.grid.index(None)
                self.grid[i] = vmw.deck.deal_next_card()
                x = self.left+self.xinc*(i%COL)
                y = self.top+self.yinc*int(i/COL)
                self.place_a_card(self.grid[i],x,y)
                self.cards += 1

    # remove a match from the grid and deal new cards from the deck
    def remove_and_replace(self, clicked_set, vmw):
        for a in clicked_set:
            # find the position in the grid of the clicked card
            i = self.xy_to_grid(a.x,a.y)
            # only add new cards if we are down to 12 cards
            if self.cards == DEAL:
                if vmw.deck.empty():
                    self.grid[i] = None
                else:
                    # save card in grid position of card we are replacing
                    self.grid[i] = vmw.deck.deal_next_card()
                    self.place_a_card(self.grid[i],a.x,a.y)
            else:
                self.cards -= 1
                # mark grid positions of cards we are not replacing
                self.grid[i] = None
            # move clicked card to the match area
            a.x = 10
            a.y = self.top + clicked_set.index(a)*self.yinc
            vmw.deck.spr_to_card(a).show_card()

    # place a card at position x,y and display it
    def place_a_card(self,c,x,y):
        if c is not None:
            c.spr.x = x
            c.spr.y = y
            c.show_card()

    # convert from sprite x,y to grid index
    def xy_to_grid(self,x,y):
        return int(COL*(y-self.top)/self.yinc) + int((x-self.left)/self.xinc)
