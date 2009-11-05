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
        # stuff to keep around for the graphics
        self.w = tw.width
        self.h = tw.height
        self.d = tw.card_dim
        self.s = tw.scale
        # Initialize the deck of cards
        # some loop through all the patterns
        # self.deck[i] = Card(tw,pattern)

    # shuffle the deck
    def shuffle(self,tw):
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


