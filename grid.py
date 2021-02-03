# Copyright (c) 2009-14 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

from gi.repository import GLib

from constants import ROW, COL, DEAL, LABELH
try:
    from sugar3.graphics.style import DEFAULT_SPACING
except:
    DEFAULT_SPACING = 16

DELTA = 20
STEP_PAUSE = 50


def _distance_squared(pos1, pos2):
    ''' simple distance function '''
    return (pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) + \
        (pos1[1] - pos2[1]) * (pos1[1] - pos2[1])


class Grid:

    ''' Class for managing ROWxCOL matrix of cards '''

    def __init__(self, width, height, card_width, card_height):
        ''' Initialize the playing surface '''
        self.grid = []
        self.card_width = card_width
        self.card_height = card_height
        for i in range(ROW * COL):
            self.grid.append(None)

        # Card spacing
        self.left = int((width - (card_width * 3)) / 2)
        if width < height:
            self.portrait = True
            self.top = int(LABELH * 6)
        else:
            self.portrait = False
            self.top = int(LABELH)
        self.xinc = int(card_width + DEFAULT_SPACING)
        self.yinc = int(card_height + DEFAULT_SPACING)
        self.bottom = int(self.top + 5 * self.yinc)
        self.dx = [0, 0, 0, 0, 0, 0]
        self.dy = [0, 0, 0, 0, 0, 0]
        self.sx = [0, 0, 0, 0, 0, 0]
        self.sy = [0, 0, 0, 0, 0, 0]
        self.ex = [0, 0, 0, 0, 0, 0]
        self.ey = [0, 0, 0, 0, 0, 0]
        self.stop_animation = False
        self.animation_lock = [False, False, False, False, False, False]

    def rotate(self, width, height):
        if width < height:
            self.portrait = True
            self.top = int(LABELH * 6)
        else:
            self.portrait = False
            self.top = int(LABELH)
        self.left = int((width - (self.card_width * 3)) / 2)
        self.bottom = int(self.top + 5 * self.yinc)

        for i in range(ROW * COL):
            self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                              self.grid_to_xy(i)[1])

    def deal(self, deck):
        ''' Deal an initial set of cards. '''
        for i in range(ROW * COL):
            self.grid[i] = None
            if i < (ROW - 1) * COL:
                if not deck.empty():
                    self.grid[i] = deck.deal_next_card()
                    self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                                      self.grid_to_xy(i)[1])

    def deal_extra_cards(self, deck):
        ''' Add cards to the bottom row when there is no match.
            But only if there are still cards in the deck
            and only 12 cards in the grid
        '''
        if not deck.empty() and self.cards_in_grid() == DEAL:
            for c in range(0, COL):
                i = self.grid.index(None)
                self.grid[i] = deck.deal_next_card()
                self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                                  self.grid_to_xy(i)[1])

    def cards_in_grid(self):
        ''' How many cards are on the grid? '''
        return ROW * COL - self.grid.count(None)

    def restore(self, deck, saved_card_index):
        ''' Restore cards to grid upon resume or share. '''
        self.hide()
        j = 0
        for i in saved_card_index:
            if i is None:
                self.grid[j] = None
            else:
                self.grid[j] = deck.index_to_card(i)
            j += 1
        self.show()

    def find_an_empty_slot(self):
        ''' Return the position of an empty slot in the grid '''
        for i in range(len(self.grid)):
            if self.grid[i] is None:
                return i
        return None  # No empty slots

    def replace(self, deck):
        ''' Deal new cards. '''
        for j in range(3):
            # Don't add new cards if bottom row is occupied
            if self.cards_in_grid() < DEAL:
                if not deck.empty():
                    i = self.find_an_empty_slot()
                    # Put new card in grid position of card we are replacing.
                    self.grid[i] = deck.deal_next_card()
                    GLib.timeout_add(
                        1200, self.place_a_card, self.grid[i],
                        self.grid_to_xy(i)[0], self.grid_to_xy(i)[1], j)

    def display_match(self, spr, i, animate=True):
        ''' Move card to the match area. '''
        spr.set_layer(2000)
        self.ex[i] = self.left + i * self.xinc
        self.ey[i] = self.bottom
        if animate:
            self.stop_animation = False
            self.sx[i] = spr.get_xy()[0]
            self.sy[i] = spr.get_xy()[1]
            self.dx[i] = int((self.ex[i] - self.sx[i]) / DELTA)
            self.dy[i] = int((self.ey[i] - self.sy[i]) / DELTA)
            GLib.timeout_add(STEP_PAUSE, self._move_to_position, spr, i)
        else:
            self.stop_animation = True
            spr.move((self.ex[i], self.ey[i]))

    def return_to_grid(self, spr, i, j):
        ''' Move card from the match area. '''
        self.stop_animation = False
        self.animation_lock[j] = True
        spr.set_layer(2000)
        self.ex[j] = self.grid_to_xy(i)[0]
        self.ey[j] = self.grid_to_xy(i)[1]
        self.sx[j] = spr.get_xy()[0]
        self.sy[j] = spr.get_xy()[1]
        self.dx[j] = int((self.ex[j] - self.sx[j]) / DELTA)
        self.dy[j] = int((self.ey[j] - self.sy[j]) / DELTA)
        GLib.timeout_add(STEP_PAUSE, self._move_to_position, spr, j)

    def _move_to_position(self, spr, i):
        ''' Piece-wise animation of card movement '''
        spr.move_relative((self.dx[i], self.dy[i]))
        if self.stop_animation:
            # spr.move((self.sx[i], self.sy[i]))
            spr.move((self.ex[i], self.ey[i]))
            self.animation_lock[i] = False
        elif _distance_squared(spr.get_xy(), (self.ex[i], self.ey[i])) < 1000:
            spr.move((self.ex[i], self.ey[i]))
            self.animation_lock[i] = False
        else:
            GLib.timeout_add(STEP_PAUSE, self._move_to_position, spr, i)

    def consolidate(self):
        ''' If we have removed cards from an expanded grid,
            we have to consolidate.
        '''
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

    def place_a_card(self, c, x, y, animate=-1):
        ''' Place a card at position x,y and display it. '''
        self.stop_animation = False
        if c is not None:
            if animate == -1:
                c.spr.move((x, y))
                c.show_card()
            else:
                c.spr.set_layer(3000)
                self.ex[animate + 3] = x
                self.ey[animate + 3] = y
                self.dx[animate + 3] = int(
                    (self.ex[animate + 3] - c.spr.get_xy()[0]) / DELTA)
                self.dy[animate + 3] = int(
                    (self.ey[animate + 3] - c.spr.get_xy()[1]) / DELTA)
                self.animation_lock[animate + 3] = True
                GLib.timeout_add(STEP_PAUSE, self._move_to_position,
                                    c.spr, animate + 3)

    def xy_to_match(self, pos):
        ''' Convert from sprite x,y to match index. '''
        return int((pos[0] - self.left) / self.xinc)

    def xy_in_match(self, pos):
        ''' Is a position at one of the match points? '''
        for i in range(3):
            x, y = self.match_to_xy(i)
            if pos[0] == x and pos[1] == y:
                return True
        return False

    def match_to_xy(self, i):
        ''' Convert from match index to x, y position. '''
        return ((self.left + i * self.xinc, self.bottom))

    def xy_in_grid(self, pos):
        ''' Is a position at one of the grid points? '''
        for i in range(ROW * COL):
            x, y = self.grid_to_xy(i)
            if pos[0] == x and pos[1] == y:
                return True
        return False

    def xy_to_grid(self, pos):
        ''' Convert from sprite x,y to grid index. '''
        return COL * int((pos[1] - self.top) / self.yinc)\
            + int((pos[0] - self.left) / self.xinc)

    def grid_to_xy(self, i):
        ''' Convert from grid index to sprite x,y. '''
        x = self.left + i % COL * self.xinc
        y = self.top + (i // COL) * self.yinc
        return (x, y)

    def grid_to_spr(self, i):
        ''' Return the sprite in grid-position i. '''
        return self.grid[i].spr

    def spr_to_grid(self, spr):
        ''' Return the index of a sprite in grid. '''
        for i in range(ROW * COL):
            if self.grid[i] is not None and self.grid[i].spr == spr:
                return(i)
        return None

    def hide(self):
        ''' Hide all of the cards on the grid. '''
        for i in range(ROW * COL):
            if self.grid[i] is not None:
                self.grid[i].hide_card()

    def show(self):
        ''' Restore all card on the grid to their x,y positions. '''
        for i in range(ROW * COL):
            self.place_a_card(self.grid[i], self.grid_to_xy(i)[0],
                              self.grid_to_xy(i)[1])
