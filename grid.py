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

        # shuffle the deck
        self.shuffle()

        # layout the initial 12 cards from the deck
        # find upper left corner of grid
        x = int((tw.width-(tw.card_w*5.5*tw.scale))/2)
        y = int((tw.height-(tw.card_h*3*tw.scale))/2)
        for r in range(0,3):
            for c in range(0,4):
                print "dealing card " + str(self.index)
                self.deck[self.index].spr.x = x
                self.deck[self.index].spr.y = y
                self.deck[self.index].draw_card()
                self.index += 1
                x += int(tw.card_w*1.5*tw.scale)
            x = int((tw.width-(tw.card_w*5.5*tw.scale))/2)
            y += int(tw.card_h*tw.scale)

    # shuffle the deck
    def shuffle(self):
        return

    # initial layout of 12 cards on the table
    def start(self, tw):
        return

    # draw a card from the deck
    def draw_a_card(self, tw):
        return

    # find a set
    def find_a_set(self, tw):
        return


