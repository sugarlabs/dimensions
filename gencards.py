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
from constants import *
from math import sin, cos, pi

RED_STROKE = "#FF6040"
RED_FILL = "#FFC4B8"
BLUE_STROKE = "#0060C8"
BLUE_FILL = "#ACC8E4"
GREEN_STROKE = "#00B418"
GREEN_FILL = "#AFE8A8"

color_pairs = ([RED_STROKE,RED_FILL],
               [GREEN_STROKE,GREEN_FILL],
               [BLUE_STROKE,BLUE_FILL])
fill_styles = ["solid","none","gradient"]
card_types = ["X","O","C"]

roman_numerals = {5:'V',7:'VII',10:'X',11:'XI',14:'XIV',15:'XV',\
                  21:'XXI',22:'XXII',33:'XXXIII'}
number_names = {5:_('five'),7:_('seven'),11:_('eleven'),10:_('ten'),\
                14:_('fourteen'),15:_('fifteen'),22:_('twenty two'),\
                21:_('twenty one'),33:_('thirty three')}
number_products = {5:'1×5',7:'1×7',11:'1×11',10:'2×5',\
                   14:'2×7',15:'3×5',22:'2×11',\
                   21:'3×7',33:'3×11'}
chinese_numerals = {5:'五',7:'七',10:'十',11:'十一',14:'十四',15:'十五',\
                  21:'廿一',22:'廿二',33:'卅三'}

word_lists = [[_('mouse'),_('cat'),_('dog')],\
              [_('cheese'),_('apple'),_('bread')],\
              [_('moon'),_('sun'),_('earth')]]
word_styles = ["font-weight:bold;","","font-style:italic;"]

#
# SVG generators
#
def svg_rect(f,w,h,rx,ry,x,y,stroke,fill,stroke_width):
    f.write("       <rect\n")
    f.write("          width=\""+str(w)+"\"\n")
    f.write("          height=\""+str(h)+"\"\n")
    f.write("          rx=\""+str(rx)+"\"\n")
    f.write("          ry=\""+str(ry)+"\"\n")
    f.write("          x=\""+str(x)+"\"\n")
    f.write("          y=\""+str(y)+"\"\n")
    f.write("          style=\"fill:"+str(fill)+";stroke:"+str(stroke)+\
            ";stroke-width:"+str(stroke_width)+";stroke-opacity:1\" />\n")

def svg_circle(f,cx,cy,r,stroke,fill,stroke_width):
    f.write("       <circle\n")
    f.write("          cx=\""+str(cx)+"\"\n")
    f.write("          cy=\""+str(cy)+"\"\n")
    f.write("          r=\""+str(r)+"\"\n")
    f.write("          style=\"fill:"+str(fill)+";stroke:"+str(stroke)+\
            ";stroke-width:"+str(stroke_width)+";stroke-opacity:1\" />\n")

def svg_line(f,x1,y1,x2,y2,stroke,fill,stroke_width):
    f.write("<line x1=\""+str(x1)+"\" y1=\""+str(y1)+\
            "\" x2=\""+str(x2)+"\" y2=\""+str(y2)+"\"\n")
    f.write("   style=\"fill:"+str(fill)+";stroke:"+str(stroke)+\
            ";stroke-width:"+str(stroke_width)+";stroke-linecap:round;\" />\n")

def svg_text(f,x,y,size,stroke,font,style,string):
    f.write("  <text\n")
    f.write("     style=\"font-size:12px;text-anchor:middle;"+style+\
            "text-align:center;font-family:"+font+";fill:"+stroke+"\">\n")
    f.write("      <tspan\n")
    f.write("       x=\""+str(x)+"\"\n")
    f.write("       y=\""+str(y)+"\"\n")
    f.write("       style=\"font-size:"+str(size)+"px;\">"+string+"</tspan>\n")
    f.write("  </text>\n")

def svg_check(f, x, style, stroke, fill):
    f.write("<path d=\"m 28.4,70.2 -5.9,5.9 -5.9,-5.9 -4.1,-4.1 c -0.7,-0.7" +\
            " -1.2,-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 4.1,-4.1 1.1,0 2.2,0.5" +\
            " 2.9,1.2 l 4.1,4.1 14.1,-14.1 c 0.8,-0.7 1.8,-1.2 2.9,-1.2 2.3,"+\
            "0 4.1,1.9 4.1,4.1 0,1.1 -0.5,2.2 -1.2,2.9 l -14.1,14.1 z\"\n")
    f.write("   transform=\"translate("+str(x-10)+", -25)\"\n")
    if style == "none":
        f.write("   style=\"fill:#FFFFFF;stroke:"+stroke+\
              ";stroke-width:1.8;\" />\n")
    elif style == "gradient":
        f.write("   style=\"fill:"+fill+";stroke:"+stroke+\
              ";stroke-width:1.8;\" />\n")
    else:
        f.write("   style=\"fill:"+stroke+";stroke:"+stroke+\
              ";stroke-width:1.8;\" />\n")

def svg_cross(f, x, style, stroke, fill):
    f.write("<path d=\"m 33.4,62.5 10.1,10.1 c 0.8,0.8 1.2,1.8 1.2,2.9 0,2.3"+\
            " -1.9,4.1 -4.1,4.1 -1.1,0 -2.2,-0.5 -2.9,-1.2 l -10.1,-10.1"+\
            " -10.1,10.1 c -0.8,0.8 -1.8,1.2 -2.9,1.2 -2.3,0 -4.1,-1.9 -4.1,"+\
            "-4.1 0,-1.1 0.5,-2.2 1.2,-2.9 l 10.1,-10.1 -10.1,-10.1 c -0.7,"+\
            "-0.7 -1.2,-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 4.1,-4.1 1.1,0 2.2,"+\
            "0.5 2.9,1.2 l 10.1,10.1 10.1,-10.1 c 0.8,-0.7 1.8,-1.2 2.9,-1.2"+\
            " 2.3,0 4.1,1.9 4.1,4.1 0,1.1 -0.5,2.2 -1.2,2.9 l -10.1,10.1 z\"\n")
    f.write("   transform=\"translate("+str(x-10)+", -25)\"\n")
    if style == "none":
        f.write("   style=\"fill:#FFFFFF;stroke:"+stroke+\
              ";stroke-width:1.8;\" />\n")
    elif style == "gradient":
        f.write("   style=\"fill:"+fill+";stroke:"+stroke+\
              ";stroke-width:1.8;\" />\n")
    else:
        f.write("   style=\"fill:"+stroke+";stroke:"+stroke+\
              ";stroke-width:1.8;\" />\n")

def background(f,stroke,fill,width):
    svg_rect(f,124.5,74.5,11,9,0.25,0.25,stroke,fill,width)

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

#
# Card pattern generators
#
def line_of_dots(f, n, x, y, stroke):
    f.write("<g\n")
    f.write("   transform=\"translate("+str(x)+", "+str(y)+")\">\n")
    if n%5 == 0:
        cx = 37.5
    elif n%7 == 0:
        cx = 27.5
    else:
        cx = 7.5
    cy = 5
    for i in range(n):
        svg_circle(f,cx,cy,3,stroke,stroke,2)
        cx += 10
    f.write("</g>\n")

def hash(f, n, x, y, stroke):
    f.write("<g\n")
    f.write("   transform=\"translate("+str(x)+", "+str(y)+")\">\n")
    if n%5 == 0:
        cx = 42.5
    elif n%7 == 0:
        cx = 32.5
    else:
        cx = 22.5
    cy = 5
    x1 = 7.5+cx
    x2 = cx
    for i in range(n):
        if (i+1)%5==0:
            svg_line(f,x1-40,7.5,x2,7.5,stroke,"none",1.8)
        else:
            svg_line(f,x1,0,x2,15,stroke,"none",1.8)
        x1 += 7.5
        x2 += 7.5
    f.write("</g>\n")

def dots_in_a_line(f, t, n, stroke):
    if n%3 == 0:
        y = 12.5
        nn = n/3
    elif n%2 == 0:
        y = 22.5
        nn = n/2
    else:
        y = 32.5
        nn = n
    if n%5 == 0:
        n/=5
    elif n%7 == 0:
        n/=7
    else:
        n/=11
    for i in range(n):
        line_of_dots(f, nn, 5, y, stroke)
        y += 20

def circle_of_dots(f, n, x, y, stroke):
    f.write("<g\n")
    f.write("   transform=\"translate("+str(x)+", "+str(y)+")\">\n")
    j = n
    ox = 0
    oy = 32.5
    if j == 5:
       r = 9
    elif j == 7:
       r = 13
    else:
       r = 17
    da = pi*2/j
    a = 0
    x = ox+sin(a)*r
    y = oy+cos(a)*r
    for i in range(n):
        svg_circle(f,x,y,3,stroke,stroke,2)
        a += da
        x = ox+sin(a)*r
        y = oy+cos(a)*r
    f.write("</g>\n")

def points_in_a_star(f, t, n, stroke):
    if n%3 == 0:
        x = 25
        nn = n/3
    elif n%2 == 0:
        x = 37.5
        nn = n/2
    else:
        x = 62.5
        nn = n
    if n%5 == 0:
        n/=5
        y = 15
    elif n%7 == 0:
        n/=7
        y = 15
    else:
        n/=11
        y = 15
    for i in range(n):
        if n == 3:
            if i == 0:
                y+=12
            elif i == 1:
                y-=24
            else:
                y+=24
        star(f, nn, x, y, stroke)
        if n == 2:
            x += 50
        else:
            x += 37.5

def dots_in_a_circle(f, t, n, stroke):
    if n%3 == 0:
        x = 25
        nn = n/3
    elif n%2 == 0:
        x = 37.5
        nn = n/2
    else:
        x = 62.5
        nn = n
    if n%5 == 0:
        n/=5
        y = 5
    elif n%7 == 0:
        n/=7
        y = 5
    else:
        n/=11
        y = 5
    for i in range(n):
        if n == 3:
            if i == 0:
                y+=12
            elif i == 1:
                y-=24
            else:
                y+=24
        circle_of_dots(f, nn, x, y, stroke)
        if n == 2:
            x += 50
        else:
            x += 37.5

def die(f, n, x, y, stroke):
    f.write("<g\n")
    f.write("   transform=\"translate("+str(x)+", "+str(y)+")\">\n")
    svg_rect(f,25,25,2,2,0,0,stroke,"none",1.5)
    if n in [2,3,4,5,6]:
        svg_circle(f,6,6,1.5,stroke,stroke,2)
        svg_circle(f,19,19,1.5,stroke,stroke,2)
    if n in [1,3,5]:
        svg_circle(f,12.5,12.5,1.5,stroke,stroke,2)
    if n in [4,5,6]:
        svg_circle(f,19,6,1.5,stroke,stroke,2)
        svg_circle(f,6,19,1.5,stroke,stroke,2)
    if n in [6]:
        svg_circle(f,6,12.5,1.5,stroke,stroke,2)
        svg_circle(f,19,12.5,1.5,stroke,stroke,2)
    f.write("</g>\n")

def number_hash(f, t, n, stroke):
    if n%3 == 0:
        y = 12.5
        nn = n/3
    elif n%2 == 0:
        y = 22.5
        nn = n/2
    else:
        y = 32.5
        nn = n
    if n%5 == 0:
        n/=5
    elif n%7 == 0:
        n/=7
    else:
        n/=11
    for i in range(n):
        hash(f, nn, 5, y, stroke)
        y += 20

def dice(f, t, n, stroke):
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

def star(f, n, x, y, stroke):
    turntable = {5:3,7:3,11:5}
    f.write("<g\n")
    f.write("   transform=\"translate("+str(x)+", "+ str(y)+")\">\n")    
    turns = turntable[n]
    x1 = 0
    y1 = 0
    a = 0
    for i in range(n*turns):
        x2 = x1+sin(a)*40
        y2 = y1+cos(a)*40
        svg_line(f,x1,y1,x2,y2,stroke,stroke,1.8)
        x1 = x2
        y1 = y2
        a += turns*2*pi/n
    f.write("</g>\n")

def circle(f, x, style, stroke, fill):
    if style == "none":
        svg_circle(f,x+17,38,16,stroke,"#FFFFFF",1.8)
    elif style == "gradient":
        svg_circle(f,x+17,38,16,stroke,fill,1.8)
    else:
        svg_circle(f,x+17,38,16,stroke,stroke,1.8)
    svg_circle(f,x+17,38,8,stroke,fill,1.8)

def check_card(f, n, style, stroke, fill):
    if n == 1:
       svg_check(f, 45.5, style, stroke, fill)
    elif n == 2:
       svg_check(f, 25.5, style, stroke, fill)
       svg_check(f, 65.5, style, stroke, fill)
    else:
       svg_check(f,  5.5, style, stroke, fill)
       svg_check(f, 45.5, style, stroke, fill)
       svg_check(f, 85.5, style, stroke, fill)

def cross_card(f, n, style, stroke, fill):
    if n == 1:
       svg_cross(f, 45.5, style, stroke, fill)
    elif n == 2:
       svg_cross(f, 25.5, style, stroke, fill)
       svg_cross(f, 65.5, style, stroke, fill)
    else:
       svg_cross(f,  5.5, style, stroke, fill)
       svg_cross(f, 45.5, style, stroke, fill)
       svg_cross(f, 85.5, style, stroke, fill)

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

def number_arabic(f, t, n, stroke):
    x = 63.5
    string = str(n)
    svg_text(f,x,55,48,stroke,"DejaVu","",string)

def number_roman(f, t, n, stroke):
    x = 63.5
    string = roman_numerals[n]
    svg_text(f,x,53,32,stroke,"DejaVu Serif","",string)

def number_chinese(f, t, n, stroke):
    x = 63.5
    string = chinese_numerals[n]
    svg_text(f,x,55,48,stroke,"DejaVu","",string)

def number_product(f, t, n, stroke):
    x = 63.5
    string = number_products[n]
    svg_text(f,x,53,36,stroke,"DejaVu","",string)

def number_word(f, t, n, stroke):
    x = 63.5
    strings = number_names[n].split(' ')
    if len(strings) == 1:
        svg_text(f,x,48,26,stroke,"DejaVu Serif","",strings[0])
    else:
        svg_text(f,x,35,26,stroke,"DejaVu Serif","",strings[0])
        svg_text(f,x,63,26,stroke,"DejaVu Serif","",strings[1])

def number_card(f, t, n, stroke, methodX, methodO, methodC):
    if t == 'X':
        methodX(f, t, n, stroke)
    elif t == 'O':
        methodO(f, t, n, stroke)
    else:
        methodC(f, t, n, stroke)

def word_card(f, t, c, n, s):
    svg_text(f,63.5,45.5,30,c[0],"DejaVu",s,word_lists[card_types.index(t)][n])

def pattern_card(f, t, c, n, s):
    pattern_styles = [cross_card, circle_card, check_card]
    pattern_styles[card_types.index(t)](f,n,s,c[0],c[1])

def open_file(datapath, filename):
    return file(os.path.join(datapath, filename), "w")

def close_file(f):
    f.close()

def generator(datapath,numberO=PRODUCT,numberC=HASH):
    generate_pattern_cards(datapath)
    generate_number_cards(datapath,numberO,numberC)
    generate_word_cards(datapath)

def generate_pattern_cards(datapath):
    i = 0
    for t in card_types:
        for c in color_pairs:
            for n in range(1,4):
                for s in fill_styles:
                    filename = "pattern-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    header(f,"#000000",c[1],"0.5")
                    pattern_card(f,t,c,n,s)
                    footer(f)
                    close_file(f)
                    i += 1

def generate_number_cards(datapath,numberO,numberC):
    methodO = [number_roman, number_product, number_chinese, number_word]
    methodC = [dots_in_a_line, dots_in_a_circle, points_in_a_star,\
                number_hash, dice]
    methodX = number_arabic
    i = 0
    for t in card_types:
        for c in color_pairs:
            for n in range(1,4):
                for s in [5,7,11]:
                    filename = "number-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    header(f,"#000000",c[1],"0.5")
                    number_card(f,t,n*s,c[0],
                                methodX,methodO[numberO],methodC[numberC])
                    footer(f)
                    close_file(f)
                    i += 1

def generate_word_cards(datapath):
    i = 0
    for t in card_types:
        for c in color_pairs:
            for n in range(0,3):
                for s in word_styles:
                    filename = "word-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    header(f,"#000000",c[1],"0.5")
                    word_card(f,t,c,n,s)
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
