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
        x = int((tw.width-(tw.card_w*5.5*tw.scale))/2)
        y = int((tw.height-(tw.card_h*3*tw.scale))/2)
        for r in range(0,3):
            for c in range(0,4):
                # print "dealing card " + str(self.index)
                self.deck[self.index].spr.x = x
                self.deck[self.index].spr.y = y
                self.deck[self.index].draw_card()
                self.index += 1
                x += int(tw.card_w*1.5*tw.scale)
            x = int((tw.width-(tw.card_w*5.5*tw.scale))/2)
            y += int(tw.card_h*tw.scale)

    # shuffle the deck
    def shuffle(self):
        # hide all the cards
        for c in self.deck:
            self.deck[c].hide_card()
        # randomize the deck
        for n in range(0,532):
            i = random.randrange(108)
            j = random.randrange(108)
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

    # remove a set from positions
    def remove_a_set(self, set, tw):
        for a in set:
            c = self.draw_a_card()
            if c is not None:
                c.spr.x = a.x
                c.spr.y = a.y
                # self.spr_to_card(a).hide_card()
                a.x = 10
                a.y = set.index(a)*int(tw.card_h*tw.scale) + \
                      int((tw.height-(tw.card_h*3*tw.scale))/2)
                self.spr_to_card(a).draw_card()
                c.draw_card()
        if c is None:
            return False
        else:
            return True

    def draw_a_card(self):
        self.index += 1
        if self.index == self.count:
            return None
        else:
            return self.deck[self.index]        
        return

