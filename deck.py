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
from constants import *
from card import *

#
# class for defining deck of cards
#
class Deck:
    def __init__(self, sprites, path, cardtype, width, height, level=HIGH):
        # Create the deck of cards.
        self.cards = []
        # If level is 'simple', only generate one fill type
        if level == HIGH:
            fill_range = FILLS
        else:
            fill_range = 1
        # Initialize the deck of cards by looping through all the patterns
        for shape in range(0, SHAPES):
            for color in range(0, COLORS):
                for num in range(0, NUMBER):
                    for fill in range(0, fill_range):
                        self.cards.append(Card(sprites, path, cardtype, 
                                               width, height,
                                               [shape,color,num,fill]))
        # Track how many cards are in the deck.
        self.count = len(self.cards)
        # Remember the position in the deck.
        self.index = 0

    # shuffle the deck
    def shuffle(self):
        decksize = self.count
        # hide all the cards
        for c in self.cards:
            c.hide_card()
        # randomize the deck
        for n in range(decksize*4):
            i = random.randrange(decksize)
            j = random.randrange(decksize)
            self.swap_cards(i,j)            
        # reset the index to the beginning of the deck after a shuffle
        self.index = 0
        return

    # restore deck upon resume
    def restore(self, saved_deck_indices):
        self.count = len(saved_deck_indices)
        _deck = []
        for i in saved_deck_indices:
             _deck.append(self.index_to_card(i))
        for i in range(self.count):
             self.cards[i] = _deck[i]

    # swap the position of two cards in the deck
    def swap_cards(self,i,j):
        tmp = self.cards[j]
        self.cards[j] = self.cards[i]
        self.cards[i] = tmp
        return

    # given a sprite, find the corresponding card in the deck
    def spr_to_card(self, spr):
        for c in self.cards:
            if c.spr == spr:
                return c
        return None

    # given a card index, find the corresponding card in the deck
    def index_to_card(self, i):
        for c in self.cards:
            if c.index == i:
                return c
        return None

    # deal the next card from the deck
    def deal_next_card(self):
        if self.empty():
            return None
        next_card = self.cards[self.index]
        self.index += 1
        return next_card
 
    # is the deck empty?
    def empty(self):
        if self.cards_remaining() > 0:
            return False
        else:
            return True

    # cards remaining in the deck
    def cards_remaining(self):
       return(self.count-self.index)

    # hide the deck
    def hide(self):
        for c in self.cards:
            c.hide_card()




