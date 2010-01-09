#Copyright (c) 2009, Walter Bender
#Copyright (c) 2009, Michele Pratusevich

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
import os.path

from constants import *
from sprites import *

#
# class for defining individual cards
# tw - image related
# pattern - game logic related
# card index is generated in the following loop:
#        for shape in range(0,SHAPES):
#            for color in range(0,COLORS):
#                for num in range(0,NUMBER):
#                    for fill in range(0,FILLS):
# if shape == SELECTMASK then generate special card-selected overlay
#
class Card:
    def __init__(self, sprites, path, cardtype, width, height, attributes):
        if attributes[0] == SELECTMASK:
            self.spr = Sprite(sprites, 0, 0,
                              self.load_image(path, "selected", width, height))
            self.index = SELECTMASK
        elif attributes[0] == MATCHMASK:
            self.spr = Sprite(sprites, 0, 0,
                              self.load_image(path, "match", width, height))
            self.index = MATCHMASK
        else:
            self.shape = attributes[0]
            self.color = attributes[1]
            self.num = attributes[2]
            self.fill = attributes[3]
            self.index = self.shape*COLORS*NUMBER*FILLS+\
                         self.color*NUMBER*FILLS+\
                         self.num*FILLS+\
                         self.fill
            self.spr = Sprite(sprites, 0, 0,
                              self.load_image(path, cardtype+"-"+\
                                              str(self.index),
                                              width, height))

    def show_card(self):
        self.spr.set_layer(2000)
        self.spr.draw()

    def hide_card(self):
        self.spr.hide()

    def load_image(self, path, file, w, h):
        return gtk.gdk.pixbuf_new_from_file_at_size(
            os.path.join(path, file+".svg"), int(w), int(h))

