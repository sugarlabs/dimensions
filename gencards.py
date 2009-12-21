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

import os
from gettext import gettext as _
import random

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
               [BLUE_STROKE,BLUE_FILL])

fill_styles = ("none","gradient","solid")
card_types = ("X","O","C")

def background(f,stroke,fill,width):
    f.write("<rect width=\"124.5\" height=\"74.5\" rx=\"11\" ry=\"9\"" +\
            " x=\"0.25\" y=\"0.25\"\n")
    f.write("style=\"fill:" + fill + ";fill-opacity:1;stroke:" + stroke + \
            ";stroke-width:"+width+"\" />\n")

def header(f,stroke,fill,width):
    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
    f.write("<!-- Created with Emacs -->\n")
    f.write("<svg\n")
    f.write("   xmlns:svg=\"http://www.w3.org/2000/svg\"\n")
    f.write("   xmlns=\"http://www.w3.org/2000/svg\"\n")
    f.write("   version=\"1.0\"\n")
    f.write("   width=\"125\"\n")
    f.write("   height=\"75\">\n")
    background(f,stroke,fill,width)
    f.write("<g>\n")

def footer(f):
    f.write("</g>\n")
    f.write("</svg>\n")

def dots(f, n, x, y, stroke):
    f.write("     <g\n")
    f.write("   transform=\"translate(" + str(x) + ", " + str(y) + ")\">\n")
    if n%5 == 0:
        ox = 37.5
        j = 5
    elif n%7 == 0:
        ox = 27.5
        j = 7
    else:
        ox = 7.5
        j = 11
    if n%3 == 0:
        oy = 12.5
    elif n%2 == 0:
        oy = 22.5
    else:
        oy = 32.5
    x = ox
    y = oy
    for i in range(n):
        f.write("       <circle\n")
        f.write("          cx=\""+str(x)+"\"\n")
        f.write("          cy=\""+str(y)+"\"\n")
        f.write("          r=\"3\"\n")
        f.write("          style=\"fill:"+str(stroke)+";stroke:"+\
                str(stroke)+";stroke-width:2;stroke-opacity:1\" />\n")
        x += 10
        if (i+1)%j == 0:
            x = ox
            y += 20
    f.write("     </g>\n")

def die(f, n, x, y, stroke):
    f.write("     <g\n")
    f.write("   transform=\"translate(" + str(x) + ", " + str(y) + ")\">\n")
    f.write("       <rect\n")
    f.write("          width=\"25\"\n")
    f.write("          height=\"25\"\n")
    f.write("          rx=\"2\"\n")
    f.write("          ry=\"2\"\n")
    f.write("          x=\"0\"\n")
    f.write("          y=\"0\"\n")
    f.write("          style=\"fill:none;stroke:"+str(stroke)+\
            ";stroke-width:2;stroke-opacity:1\" />\n")
    if n in [2,3,4,5,6]:
        f.write("       <circle\n")
        f.write("          cx=\"6\"\n")
        f.write("          cy=\"6\"\n")
        f.write("          r=\"1.5\"\n")
        f.write("          style=\"fill:"+str(stroke)+";stroke:"+str(stroke)+\
                ";stroke-width:2;stroke-opacity:1\" />\n")
        f.write("       <circle\n")
        f.write("          cx=\"19\"\n")
        f.write("          cy=\"19\"\n")
        f.write("          r=\"1.5\"\n")
        f.write("          style=\"fill:"+str(stroke)+";stroke:"+str(stroke)+\
                ";stroke-width:2;stroke-opacity:1\" />\n")
    if n in [1,3,5]:
        f.write("       <circle\n")
        f.write("          cx=\"12.5\"\n")
        f.write("          cy=\"12.5\"\n")
        f.write("          r=\"1.5\"\n")
        f.write("          style=\"fill:"+str(stroke)+";stroke:"+str(stroke)+\
                ";stroke-width:2;stroke-opacity:1\" />\n")
    if n in [4,5,6]:
        f.write("       <circle\n")
        f.write("          cx=\"19\"\n")
        f.write("          cy=\"6\"\n")
        f.write("          r=\"1.5\"\n")
        f.write("          style=\"fill:"+str(stroke)+";stroke:"+str(stroke)+\
                ";stroke-width:2;stroke-opacity:1\" />\n")
        f.write("       <circle\n")
        f.write("          cx=\"6\"\n")
        f.write("          cy=\"19\"\n")
        f.write("          r=\"1.5\"\n")
        f.write("          style=\"fill:"+str(stroke)+";stroke:"+str(stroke)+\
                ";stroke-width:2;stroke-opacity:1\" />\n")
    if n in [6]:
        f.write("       <circle\n")
        f.write("          cx=\"6\"\n")
        f.write("          cy=\"12.5\"\n")
        f.write("          r=\"1.5\"\n")
        f.write("          style=\"fill:"+str(stroke)+";stroke:"+str(stroke)+\
                ";stroke-width:2;stroke-opacity:1\" />\n")
        f.write("       <circle\n")
        f.write("          cx=\"19\"\n")
        f.write("          cy=\"12.5\"\n")
        f.write("          r=\"1.5\"\n")
        f.write("          style=\"fill:"+str(stroke)+";stroke:"+str(stroke)+\
                ";stroke-width:2;stroke-opacity:1\" />\n")
    f.write("     </g>\n")

def circle(f, x, style, stroke, fill):
    f.write("<circle cx=\"11\" cy=\"27\" r=\"16\"\n")
    f.write("   transform=\"translate(" + str(x+6) + ", 11)\"\n")
    if style == "none":
        f.write("   style=\"fill:#FFFFFF;stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    elif style == "gradient":
        f.write("   style=\"fill:" + fill + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    else:
        f.write("   style=\"fill:" + stroke + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    f.write("<circle cx=\"11\" cy=\"27\" r=\"8\"\n")
    f.write("   transform=\"translate(" + str(x+6) + ", 11)\"\n")
    f.write("   style=\"fill:" + fill + ";stroke:" + stroke + \
            ";stroke-width:1.8;\" />\n")

def check(f, x, style, stroke, fill):
    f.write("<path d=\"m 28.4,70.2 -5.9,5.9 -5.9,-5.9 -4.1,-4.1 c -0.7,-0.7" +\
            " -1.2,-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 4.1,-4.1 1.1,0 2.2,0.5" +\
            " 2.9,1.2 l 4.1,4.1 14.1,-14.1 c 0.8,-0.7 1.8,-1.2 2.9,-1.2 2.3,"+\
            "0 4.1,1.9 4.1,4.1 0,1.1 -0.5,2.2 -1.2,2.9 l -14.1,14.1 z\"\n")
    f.write("   transform=\"translate(" + str(x-10) + ", -25)\"\n")
    if style == "none":
        f.write("   style=\"fill:#FFFFFF;stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    elif style == "gradient":
        f.write("   style=\"fill:" + fill + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    else:
        f.write("   style=\"fill:" + stroke + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")

def cross(f, x, style, stroke, fill):
    f.write("<path d=\"m 33.4,62.5 10.1,10.1 c 0.8,0.8 1.2,1.8 1.2,2.9 0,2.3"+\
            " -1.9,4.1 -4.1,4.1 -1.1,0 -2.2,-0.5 -2.9,-1.2 l -10.1,-10.1"+\
            " -10.1,10.1 c -0.8,0.8 -1.8,1.2 -2.9,1.2 -2.3,0 -4.1,-1.9 -4.1,"+\
            "-4.1 0,-1.1 0.5,-2.2 1.2,-2.9 l 10.1,-10.1 -10.1,-10.1 c -0.7,"+\
            "-0.7 -1.2,-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 4.1,-4.1 1.1,0 2.2,"+\
            "0.5 2.9,1.2 l 10.1,10.1 10.1,-10.1 c 0.8,-0.7 1.8,-1.2 2.9,-1.2"+\
            " 2.3,0 4.1,1.9 4.1,4.1 0,1.1 -0.5,2.2 -1.2,2.9 l -10.1,10.1 z\"\n")
    f.write("   transform=\"translate(" + str(x-10) + ", -25)\"\n")
    if style == "none":
        f.write("   style=\"fill:#FFFFFF;stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    elif style == "gradient":
        f.write("   style=\"fill:" + fill + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")
    else:
        f.write("   style=\"fill:" + stroke + ";stroke:" + stroke + \
              ";stroke-width:1.8;\" />\n")

def check_card(f, n, style, stroke, fill):
    if n == 1:
       check(f, 45.5, style, stroke, fill)
    elif n == 2:
       check(f, 25.5, style, stroke, fill)
       check(f, 65.5, style, stroke, fill)
    else:
       check(f,  5.5, style, stroke, fill)
       check(f, 45.5, style, stroke, fill)
       check(f, 85.5, style, stroke, fill)

def cross_card(f, n, style, stroke, fill):
    if n == 1:
       cross(f, 45.5, style, stroke, fill)
    elif n == 2:
       cross(f, 25.5, style, stroke, fill)
       cross(f, 65.5, style, stroke, fill)
    else:
       cross(f,  5.5, style, stroke, fill)
       cross(f, 45.5, style, stroke, fill)
       cross(f, 85.5, style, stroke, fill)

def circle_card(f, n, style, stroke, fill):
    if n == 1:
       circle(f, 45.5, style, stroke, fill)
    elif n == 2:
       circle(f, 25.5, style, stroke, fill)
       circle(f, 65.5, style, stroke, fill)
    else:
       circle(f,  5.5, style, stroke, fill)
       circle(f, 45.5, style, stroke, fill)
       circle(f, 85.5, style, stroke, fill)

def number(f, x, string, stroke):
    f.write("  <text\n")
    f.write("     style=\"font-size:12px;text-anchor:middle;"+\
            "text-align:center;font-family:Bitstream Vera Sans;fill:"+\
            stroke+"\">\n")
    f.write("      <tspan\n")
    f.write("       x=\""+str(x)+"\"\n")
    f.write("       y=\"55.25\"\n")
    f.write("       style=\"font-size:48px;\">"+string+"</tspan>\n")
    f.write("  </text>")

def number_card(f, t, n, stroke):
    if t == 'X':
        number(f, 63.5, str(n), stroke)
    elif t == 'O':
        if n == 5:
            die(f, 5, 50, 25, stroke)
        elif n == 10:
            die(f, 5, 30, 25, stroke)
            die(f, 5, 70, 25, stroke)
        elif n == 15:
            die(f, 5, 15, 25, stroke)
            die(f, 5, 50, 25, stroke)
            die(f, 5, 85, 25, stroke)
        elif n == 7:
            die(f, 3, 50, 10, stroke)
            die(f, 4, 50, 40, stroke)
        elif n == 14:
            die(f, 4, 30, 10, stroke)
            die(f, 3, 70, 10, stroke)
            die(f, 3, 30, 40, stroke)
            die(f, 4, 70, 40, stroke)
        elif n == 21:
            die(f, 3, 15, 10, stroke)
            die(f, 4, 50, 10, stroke)
            die(f, 3, 85, 10, stroke)
            die(f, 4, 15, 40, stroke)
            die(f, 3, 50, 40, stroke)
            die(f, 4, 85, 40, stroke)
        elif n == 11:
            die(f, 5, 50, 10, stroke)
            die(f, 6, 50, 40, stroke)
        elif n == 22:
            die(f, 6, 30, 10, stroke)
            die(f, 5, 70, 10, stroke)
            die(f, 5, 30, 40, stroke)
            die(f, 6, 70, 40, stroke)
        elif n == 33:
            die(f, 5, 15, 10, stroke)
            die(f, 6, 50, 10, stroke)
            die(f, 5, 85, 10, stroke)
            die(f, 6, 15, 40, stroke)
            die(f, 5, 50, 40, stroke)
            die(f, 6, 85, 40, stroke)
    else:
        dots(f, n, 5, 5, stroke)

def word(f, x, string, stroke,style):
    f.write("  <text\n")
    f.write("     style=\"font-size:12px;text-anchor:middle;"+style+\
            "text-align:center;font-family:Bitstream Vera Sans;fill:"+\
            stroke+"\">\n")
    f.write("      <tspan\n")
    f.write("       x=\""+str(x)+"\"\n")
    f.write("       y=\"45.25\"\n")
    f.write("       style=\"font-size:30px;\">"+string+"</tspan>\n")
    f.write("  </text>")

def word_card(f, t, s, string, stroke):
    if t == 'X':
        word(f, 63.5, string[s], stroke, "font-weight:bold;")
    elif t == 'O':
        word(f, 63.5, string[s], stroke, "font-style:italic;")
    else:
        word(f, 63.5, string[s], stroke, "")

def open_file(datapath, filename):
    return file(os.path.join(datapath, filename), "w")

def close_file(f):
    f.close()

def generator(datapath):
    # pattern cards
    i = 0
    for t in card_types:
        for c in color_pairs:
            for n in range(1,4):
                for s in fill_styles:
                    filename = "pattern-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    header(f,"#000000",c[1],"0.5")
                    if t == "O":
                        circle_card(f,n,s,c[0],c[1])
                    elif t == "C":
                        check_card(f,n,s,c[0],c[1])
                    else:
                        cross_card(f,n,s,c[0],c[1])
                    footer(f)
                    close_file(f)
                    i += 1

    # number cards
    i = 0
    for t in card_types: # ignoring this field
        for c in color_pairs:
            for n in range(1,4):
                for s in [5,7,11]:
                    filename = "number-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    header(f,"#000000",c[1],"0.5")
                    number_card(f,t,n*s,c[0])
                    footer(f)
                    close_file(f)
                    i += 1

    # word cards
    i = 0
    for t in card_types: # ignoring this field
        for c in color_pairs:
            for n in range(0,3):
                for s in range(0,3):
                    filename = "word-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    header(f,"#000000",c[1],"0.5")
                    if n == 0:
                        word_card(f,t,s,[_("dog"),_("cat"),_("mouse")],c[0])
                    elif n == 1:
                        word_card(f,t,s,[_("apple"),_("bread"),_("cheese")],
                                  c[0])
                    else:
                        word_card(f,t,s,[_("sun"),_("moon"),_("earth")],c[0])
                    footer(f)
                    close_file(f)
                    i += 1

    f = open_file(datapath, "match.svg")
    header(f,"#A0A0A0","#F0F0F0","3.0")
    footer(f)
    close_file(f)

    f = open_file(datapath, "selected.svg")
    header(f,"#000000","none","3.0")
    footer(f)
    close_file(f)

def main():
    return 0

if __name__ == "__main__":
    if not os.path.exists(os.path.join(os.path.abspath('.'), 'images')):
        os.mkdir(os.path.join(os.path.abspath('.'), 'images'))
    generator(os.path.join(os.path.abspath('.'), 'images'))
    main()
