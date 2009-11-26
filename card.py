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

from sprites import *

#
# class for defining individual cards
# tw - image related
# pattern - game logic related
# card index is generated in the following loop:
"""
        for shape in range(0,3):
            for color in range(0,4):
                for num in range(0,3):
                    for fill in range(0,3):
"""
# if shape == -1 then generate special card-selected overlay
#
class Card:
    def __init__(self,tw,shape,color,num,fill):
        # what do we need to know about each card?
        if shape == -1:
            self.spr = sprNew(tw, 0, 0, self.load_image(tw.path+"selected",
                                                        tw.card_w*tw.scale,
                                                        tw.card_h*tw.scale))
            self.index = 0
        else:
            self.shape = shape
            self.color = color
            self.num = num
            self.fill = fill
            self.index = self.shape*4*3*3+self.color*3*3+self.num*3+self.fill+1
            # create sprite from svg file
            self.spr = sprNew(tw, 0, 0, self.load_image(tw.path+\
                                                        str(self.index),
                                                        tw.card_w*tw.scale,
                                                        tw.card_h*tw.scale))
        self.spr.label = ""

    def draw_card(self):
        setlayer(self.spr,2000)
        draw(self.spr)

    def hide_card(self):
        hide(self.spr)

    def load_image(self, file, w, h):
        return gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(file+".svg"),
                                                    int(w),
                                                    int(h))

