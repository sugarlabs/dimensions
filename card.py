#Copyright (c) 2009, Walter Bender
#Copyright (c) 2009, Michele Pratusevich

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
    def __init__(self,vmw,shape,color,num,fill):
        # what do we need to know about each card?
        if shape == SELECTMASK:
            self.spr = sprNew(vmw,0,0,self.load_image(
                                          vmw.path,
                                          "selected",
                                          vmw.card_w*vmw.scale,
                                          vmw.card_h*vmw.scale))
            self.index = SELECTMASK
        elif shape == MATCHMASK:
            self.spr = sprNew(vmw,0,0,self.load_image(
                                          vmw.path,
                                          "match",
                                          vmw.card_w*vmw.scale,
                                          vmw.card_h*vmw.scale))
            self.index = MATCHMASK
        else:
            # include card shape only for pattern cards
            if vmw.cardtype == 'pattern':
                self.shape = shape
            else:
                self.shape = 0
            self.color = color
            self.num = num
            self.fill = fill
            self.index = self.shape*COLORS*NUMBER*FILLS+\
                         self.color*NUMBER*FILLS+\
                         self.num*FILLS+\
                         self.fill
            # create sprite from svg file
            self.spr = sprNew(vmw,0,0,self.load_image(
                                vmw.path,
                                vmw.cardtype+"-"+str(self.index),
                                vmw.card_w*vmw.scale,
                                vmw.card_h*vmw.scale))
        self.spr.label = ""

    def show_card(self):
        setlayer(self.spr,2000)
        draw(self.spr)

    def hide_card(self):
        hide(self.spr)

    def load_image(self, path, file, w, h):
        return gtk.gdk.pixbuf_new_from_file_at_size(
            os.path.join(path, file+".svg"), int(w), int(h))

