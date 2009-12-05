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

from constants import *

#
# class for defining 4x3 matrix of cards
#
class Grid:
    def __init__(self, tw):
        # the playing surface is a 3x4 grid
        self.grid = []
        # create the deck of cards
        self.deck = {}
        # remember the position in the deck
        self.index = 0
        # how many cards are in the deck?
        self.count = 0
        # how many cards are on the playing field
        self.cards = 0
        # card spacing
        self.left = int((tw.width-(tw.card_w*5.5*tw.scale))/2)
        self.xinc = int(tw.card_w*1.5*tw.scale)
        self.top = int((tw.height-(tw.card_h*3.5*tw.scale))/2)
        self.yinc = int(tw.card_h*1.25*tw.scale)

        # Initialize the deck of cards
        # some loop through all the patterns
        for shape in range(0,3):
            for color in range(0,4):
                for num in range(0,3):
                    for fill in range(0,3):
                        self.deck[self.count] = Card(tw,shape,color,num,fill)
                        self.count += 1

    def deal(self, tw):
        # layout the initial 12 cards from the deck
        # find upper left corner of grid
        self.cards = 0
        self.grid = []
        x = self.left
        y = self.top
        for r in range(0,3):
            for c in range(0,4):
                self.grid.append(self.deck[self.index])
                self.draw_a_card(x,y)
                x += self.xinc
                self.cards += 1
            self.grid.append(None) # leave a space for the extra cards
            x = self.left
            y += self.yinc

    def deal_3_extra_cards(self, tw):
        # if there are still cards in the deck and only 12 cards in the grid
        if self.index < self.count and self.cards == DEAL:
            # add 3 extra cards to the playing field
            for r in range(0,3):
                i = self.grid.index(None)
                self.grid[i] = self.deck[self.index]
                x = self.left+self.xinc*(i%5)
                y = self.top+self.yinc*int(i/5)
                self.draw_a_card(x,y)
                self.cards += 1

    # shuffle the deck
    def shuffle(self):
        # hide all the cards
        for c in self.deck:
            self.deck[c].hide_card()
        # randomize the deck
        for n in range(0,DECKSIZE*4):
            i = random.randrange(DECKSIZE)
            j = random.randrange(DECKSIZE)
            self.swap_cards(i,j)            
        # reset the index to the beginning of the deck after a shuffle
        self.index = 0
        return

    def swap_cards(self,i,j):
        tmp = self.deck[j]
        self.deck[j] = self.deck[i]
        self.deck[i] = tmp
        return

    # given a spr, find the corresponding card in the deck
    def spr_to_card(self, spr):
        for c in self.deck:
            if self.deck[c].spr == spr:
                return self.deck[c]
        return None

    # remove a set from grid
    # and deal new cards from the deck
    def remove_and_replace(self, clicked_set, tw):
        for a in clicked_set:
            # only add new cards if we are down to 12 cards
            i = int(5*(a.y-self.top)/self.yinc) + \
                int((a.x-self.left)/self.xinc)
            if self.cards == DEAL:
                if self.index < self.count:
                    # save card in grid position of card we are replacing
                    self.grid[i] = self.deck[self.index]
                    self.draw_a_card(a.x,a.y)
                else:
                    self.grid[i] = None
            else:
                self.cards -= 1
                # mark grid positions of cards we are not replacing
                self.grid[i] = None
            # move clicked card to the set area
            a.x = 10
            a.y = self.top + clicked_set.index(a)*self.yinc
            self.spr_to_card(a).show_card()

    def draw_a_card(self,x,y):
        self.deck[self.index].spr.x = x
        self.deck[self.index].spr.y = y
        self.deck[self.index].show_card()
        self.index += 1
