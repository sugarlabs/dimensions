#Copyright (c) 2009,10 Walter Bender
#Copyright (c) 2009 Michele Pratusevich

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

import logging
_logger = logging.getLogger('visualmatch-activity')

from constants import SELECTMASK, MATCHMASK, COLORS, NUMBER, FILLS, \
    CARD_WIDTH, CARD_HEIGHT

from sprites import Sprite


class Card:
    """ Individual cards """

    def __init__(self, sprites, string, attributes, load_from_file=False,
                 scale=1.0):
        """ Create the card and store its attributes """
        if attributes[0] == SELECTMASK:
            self.spr = Sprite(sprites, 0, 0, svg_str_to_pixbuf(string))
            self.index = SELECTMASK
        elif attributes[0] == MATCHMASK:
            self.spr = Sprite(sprites, 0, 0, svg_str_to_pixbuf(string))
            self.index = MATCHMASK
        else:
            self.shape = attributes[0]
            self.color = attributes[1]
            self.num = attributes[2]
            self.fill = attributes[3]
            self.index = self.shape * COLORS * NUMBER * FILLS+\
                         self.color * NUMBER * FILLS +\
                         self.num * FILLS +\
                         self.fill
            if load_from_file:
                self.spr = Sprite(sprites, 0, 0, load_image(string, scale))
            else:
                self.spr = Sprite(sprites, 0, 0, svg_str_to_pixbuf(string))

    def show_card(self):
        """ Show the care """
        self.spr.set_layer(2000)
        self.spr.draw()

    def hide_card(self):
        self.spr.hide()


def svg_str_to_pixbuf(string):
    """ Load pixbuf from SVG string """
    pl = gtk.gdk.PixbufLoader('svg')
    pl.write(string)
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf


def load_image(path, scale):
    return gtk.gdk.pixbuf_new_from_file_at_size(path, int(scale * CARD_WIDTH),
                                                int(scale * CARD_HEIGHT))

