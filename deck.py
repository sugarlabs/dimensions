#Copyright (c) 2009, Walter Bender

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
import gobject
import random

from sprites import *
from constants import *
from card import *

#
# Class for defining deck of cards
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
        # Remember the current position in the deck.
        self.index = 0

    # Shuffle the deck.
    def shuffle(self):
        decksize = self.count()
        # Hide all the cards.
        for c in self.cards:
            c.hide_card()
        # Randomize the card order.
        for n in range(decksize*4):
            i = random.randrange(decksize)
            j = random.randrange(decksize)
            self.swap_cards(i,j)            
        # Reset the index to the beginning of the deck after a shuffle,
        self.index = 0
        return

    # Restore the deck upon resume.
    def restore(self, saved_deck_indices):
        decksize = len(saved_deck_indices)
        # If we have a short deck, then we need to abort.
        if self.count() < decksize:
            return False
        _deck = []
        for i in saved_deck_indices:
             _deck.append(self.index_to_card(i))
        for i in range(decksize):
             self.cards[i] = _deck[i]
        return True

    # Swap the position of two cards in the deck.
    def swap_cards(self,i,j):
        tmp = self.cards[j]
        self.cards[j] = self.cards[i]
        self.cards[i] = tmp
        return

    # Given a sprite, find the corresponding card in the deck.
    def spr_to_card(self, spr):
        for c in self.cards:
            if c.spr == spr:
                return c
        return None

    # Given a card index, find the corresponding card in the deck.
    def index_to_card(self, i):
        for c in self.cards:
            if c.index == i:
                return c
        return None

    # Return the next card from the deck.
    def deal_next_card(self):
        if self.empty():
            return None
        next_card = self.cards[self.index]
        self.index += 1
        return next_card
 
    # Is the deck empty?
    def empty(self):
        if self.cards_remaining() > 0:
            return False
        else:
            return True

    # Return how many cards are remaining in the deck.
    def cards_remaining(self):
       return(self.count()-self.index)

    # Hide the deck.
    def hide(self):
        for c in self.cards:
            c.hide_card()

    # Return the length of the deck.
    def count(self):
        return len(self.cards)




