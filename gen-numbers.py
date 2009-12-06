# -*- coding: utf-8 -*-
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

RED_STROKE = "#FF6040"
RED_FILL = "#FFC4B8"
BLUE_STROKE = "#0060C8"
BLUE_FILL = "#ACC8E4"
GREEN_STROKE = "#00B418"
GREEN_FILL = "#AFE8A8"
PURPLE_STROKE = "#780078"
PURPLE_FILL = "#E4AAE4"

color_pairs = ([RED_STROKE,RED_FILL],
               [GREEN_STROKE,GREEN_FILL],
               [BLUE_STROKE,BLUE_FILL],
               [PURPLE_STROKE,PURPLE_FILL])

fill_styles = (5,7,11)
card_types = (['[',']'],['(',')'],['{','}'])

def background(f,fill):
    f.write("<rect width=\"74.5\" height=\"124.5\" rx=\"11\" ry=\"9\" x=\"0.25\" y=\"0.25\"\n")
    f.write("style=\"fill:" + fill + ";fill-opacity:1;stroke:#000000;stroke-width:0.5\" />\n")

def header(f,fill):
    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
    f.write("<!-- Created with Emacs -->\n")
    f.write("<svg\n")
    f.write("   xmlns:svg=\"http://www.w3.org/2000/svg\"\n")
    f.write("   xmlns=\"http://www.w3.org/2000/svg\"\n")
    f.write("   version=\"1.0\"\n")
    f.write("   width=\"75\"\n")
    f.write("   height=\"125\">\n")
    background(f,fill)
    f.write("<g>\n")

def footer(f):
    f.write("</g>\n")
    f.write("</svg>\n")

def number(f, y, string, stroke):
    f.write("  <text\n")
    f.write("     style=\"font-size:12px;text-anchor:middle;text-align:center;font-family:Bitstream Vera Sans;fill:"+stroke+"\">\n")
    f.write("      <tspan\n")
    f.write("       x=\"37.25\"\n")
    f.write("       y=\""+str(y)+"\"\n")
    f.write("       style=\"font-size:48px;\">"+string+"</tspan>\n")
    f.write("  </text>")

def number_card(f, t, n, stroke):
    # number(f, 75, t[0]+str(n)+t[1], stroke)
    number(f, 75, str(n), stroke)

def open_file(i):
    return file("images/number-"+str(i)+".svg", "w")

def close_file(f):
    f.close()

i = 0
for t in card_types:
    for c in color_pairs:
        for n in range(1,4):
            for s in fill_styles:
                f = open_file(i)
                header(f,c[1])
                number_card(f,t,n*s,c[0])
                footer(f)
                close_file(f)
                i += 1
