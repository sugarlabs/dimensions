# -*- coding: utf-8 -*-
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

import os
from gettext import gettext as _
from constants import *
from math import sin, cos, pi

#
# SVG generators
#
def svg_style(fill,stroke,stroke_width,extras=""):
    return "%s%s%s%s%s%f%s%s%s" % ("style=\"fill:",fill,";stroke:",stroke,
                                   ";stroke-width:",stroke_width,";",extras,
                                   "\" />\n")

def svg_rect(w,h,rx,ry,x,y,stroke,fill,stroke_width):
    svg_string = "       <rect\n"
    svg_string += "          width=\"%f\"\n" % (w)
    svg_string += "          height=\"%f\"\n" % (h)
    svg_string += "          rx=\"%f\"\n" % (rx)
    svg_string += "          ry=\"%f\"\n" % (ry)
    svg_string += "          x=\"%f\"\n" % (x)
    svg_string += "          y=\"%f\"\n" % (y)
    svg_string += svg_style(fill,stroke,stroke_width)
    return svg_string

def svg_circle(cx,cy,r,stroke,fill,stroke_width):
    svg_string = "       <circle\n"
    svg_string += "          cx=\"%f\"\n" % (cx)
    svg_string += "          cy=\"%f\"\n" % (cy)
    svg_string += "          r=\"%f\"\n" % (r)
    svg_string += svg_style(fill,stroke,stroke_width)
    return svg_string

def svg_line(x1,y1,x2,y2,stroke,fill,stroke_width):
    svg_string = "<line x1=\"%f\" y1=\"%f\" x2=\"%f\" y2=\"%f\"\n" % \
                  (x1,y1,x2,y2)
    svg_string += svg_style(fill,stroke,stroke_width,"stroke-linecap:round;")
    return svg_string

def svg_text(x,y,size,stroke,font,style,string):
    svg_string = "  <text\n"
    svg_string += "%s%s%s%s%s%s%s" % (
        "     style=\"font-size:12px;text-anchor:middle;",style,
        ";text-align:center;font-family:",font,";fill:",stroke,";\">\n")
    svg_string += "      <tspan\n"
    svg_string += "       x=\"%f\"\n" % (x)
    svg_string += "       y=\"%f\"\n" % (y)
    svg_string += "       style=\"font-size:%fpx;\">%s</tspan>\n" %\
                  (size,string)
    svg_string += "  </text>\n"
    return svg_string

def svg_check(x, style, stroke, fill):
    svg_string = "%s%s%s%s%s%f%s" %\
        ("<path d=\"m 28.4,70.2 -5.9,5.9 -5.9,-5.9 -4.1,-4.1 c -0.7,-0.7",
         " -1.2,-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 4.1,-4.1 1.1,0 2.2,0.5",
         " 2.9,1.2 l 4.1,4.1 14.1,-14.1 c 0.8,-0.7 1.8,-1.2 2.9,-1.2 2.3,",
         "0 4.1,1.9 4.1,4.1 0,1.1 -0.5,2.2 -1.2,2.9 l -14.1,14.1 z\"\n",
         "   transform=\"translate(",x-10,", -25)\"\n")
    if style == "none":
        svg_string += svg_style(WHITE,stroke,1.8)
    elif style == "gradient":
        svg_string += svg_style(fill,stroke,1.8)
    else:
        svg_string += svg_style(stroke,stroke,1.8)
    return svg_string

def svg_cross(x, style, stroke, fill):
    svg_string = "%s%s%s%s%s%s%s" % (
            "<path d=\"m 33.4,62.5 10.1,10.1 c 0.8,0.8 1.2,1.8 1.2,2.9 0,2.3",
            " -1.9,4.1 -4.1,4.1 -1.1,0 -2.2,-0.5 -2.9,-1.2 l -10.1,-10.1",
            " -10.1,10.1 c -0.8,0.8 -1.8,1.2 -2.9,1.2 -2.3,0 -4.1,-1.9 -4.1,",
            "-4.1 0,-1.1 0.5,-2.2 1.2,-2.9 l 10.1,-10.1 -10.1,-10.1 c -0.7,",
            "-0.7 -1.2,-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 4.1,-4.1 1.1,0 2.2,",
            "0.5 2.9,1.2 l 10.1,10.1 10.1,-10.1 c 0.8,-0.7 1.8,-1.2 2.9,-1.2",
            " 2.3,0 4.1,1.9 4.1,4.1 0,1.1 -0.5,2.2 -1.2,2.9 l -10.1,10.1 z\"\n")
    svg_string += "%s%f%s" % ("   transform=\"translate(",x-10,", -25)\"\n")
    if style == "none":
        svg_string += svg_style(WHITE,stroke,1.8)
    elif style == "gradient":
        svg_string += svg_style(fill,stroke,1.8)
    else:
        svg_string += svg_style(stroke,stroke,1.8)
    return svg_string

def svg_circle_of_dots(n, x, y, stroke, fill):
    rtab = {5:9,7:13,11:17}
    r = rtab[n]
    ox = 0
    oy = 32.5
    da = pi*2/n
    a = 0
    nx = ox+sin(a)*r
    ny = oy+cos(a)*r
    svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                 ")\">\n")
    print svg_string
    for i in range(n):
        svg_string += svg_circle(nx,ny,3,stroke,fill,2)
        a += da
        nx = ox+sin(a)*r
        ny = oy+cos(a)*r
    svg_string += "</g>\n"
    return svg_string

def svg_line_of_dots(n, x, y, stroke):
    cxtab = {5:37.5,7:27.5,11:7.5,10:37.5,14:27.5,22:7.5,15:37.5,21:27.5,33:7.5}
    svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                 ")\">\n")
    cx = cxtab[n]
    for i in range(n):
        svg_string += svg_circle(cx,5,3,stroke,stroke,2)
        cx += 10
    svg_string += "</g>\n"
    return svg_string

def svg_hash(n, x, y, stroke):
    cxtab = {5:42.5,7:32.5,11:22.5,10:42.5,14:32.5,22:22.5,\
             15:42.5,21:32.5,33:22.5}
    cy = 5
    x2 = cxtab[n]
    x1 = 7.5+x2
    svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                 ")\">\n")
    for i in range(n):
        if (i+1)%5==0:
            svg_string += svg_line(x1-40,7.5,x2,7.5,stroke,"none",1.8)
        else:
            svg_string += svg_line(x1,0,x2,15,stroke,"none",1.8)
        x1 += 7.5
        x2 += 7.5
    svg_string += "</g>\n"
    return svg_string

def svg_die(n, x, y, stroke):
    svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                 ")\">\n")
    svg_string += svg_rect(25,25,2,2,0,0,stroke,"none",1.5)
    if n in [2,3,4,5,6]:
        svg_string += svg_circle(6,6,1.5,stroke,stroke,2)
        svg_string += svg_circle(19,19,1.5,stroke,stroke,2)
    if n in [1,3,5]:
        svg_string += svg_circle(12.5,12.5,1.5,stroke,stroke,2)
    if n in [4,5,6]:
        svg_string += svg_circle(19,6,1.5,stroke,stroke,2)
        svg_string += svg_circle(6,19,1.5,stroke,stroke,2)
    if n in [6]:
        svg_string += svg_circle(6,12.5,1.5,stroke,stroke,2)
        svg_string += svg_circle(19,12.5,1.5,stroke,stroke,2)
    svg_string += "</g>\n"
    return svg_string

def svg_star(n, x, y, stroke, fill):
    turntable = {5:3,7:3,11:5}
    turns = turntable[n]
    x1 = 0
    y1 = 0
    a = 0
    svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                 ")\">\n")
    for i in range(n*turns):
        x2 = x1+sin(a)*40
        y2 = y1+cos(a)*40
        svg_string += svg_line(x1,y1,x2,y2,stroke,fill,1.8)
        x1 = x2
        y1 = y2
        a += turns*2*pi/n
    svg_string += "</g>\n"
    return svg_string

def svg_bar(x, y, stroke):
    svg_string = "       <rect\n"
    svg_string += "          width=\"%f\"\n" % (40)
    svg_string += "          height=\"%f\"\n" % (5)
    svg_string += "          x=\"%f\"\n" % (x)
    svg_string += "          y=\"%f\"\n" % (y)
    svg_string += svg_style(stroke,stroke,1.8)
    return svg_string

def background(stroke,fill,width):
    return svg_rect(124.5,74.5,11,9,0.25,0.25,stroke,fill,width)

def header(stroke,fill,width,scale):
    svg_string = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"
    svg_string += "<!-- Created with Emacs -->\n"
    svg_string += "<svg\n"
    svg_string += "   xmlns:svg=\"http://www.w3.org/2000/svg\"\n"
    svg_string += "   xmlns=\"http://www.w3.org/2000/svg\"\n"
    svg_string += "   version=\"1.0\"\n"
    svg_string += "%s%f%s" % ("   width=\"",125*scale,"\"\n")
    svg_string += "%s%f%s" % ("   height=\"",75*scale,"\">\n")
    svg_string += "%s%f%s%f%s" % ("<g\n       transform=\"matrix(",scale,
                                  ",0,0,",scale,",0,0)\">\n")
    svg_string += background(stroke,fill,width)
    return svg_string

def footer():
    svg_string = "</g>\n"
    svg_string += "</svg>\n"
    return svg_string

#
# Card pattern generators
#
def number_mayan(n, stroke):
    x = 45
    y = 60
    if n == 5:
        svg_string = svg_bar(x,y,stroke)
    elif n == 7:
        svg_string = svg_bar(x,y,stroke)
        svg_string += svg_circle(x+15,y-10,3,stroke,stroke,2)
        svg_string += svg_circle(x+25,y-10,3,stroke,stroke,2)
    elif n == 10:
        svg_string = svg_bar(x,y,stroke)
        svg_string += svg_bar(x,y-10,stroke)
    elif n == 11:
        svg_string = svg_bar(x,y,stroke)
        svg_string += svg_bar(x,y-10,stroke)
        svg_string += svg_circle(x+20,y-20,3,stroke,stroke,2)
    elif n == 14:
        svg_string = svg_bar(x,y,stroke)
        svg_string += svg_bar(x,y-10,stroke)
        svg_string += svg_circle(x+5,y-20,3,stroke,stroke,2)
        svg_string += svg_circle(x+15,y-20,3,stroke,stroke,2)
        svg_string += svg_circle(x+25,y-20,3,stroke,stroke,2)
        svg_string += svg_circle(x+35,y-20,3,stroke,stroke,2)
    elif n == 15:
        svg_string = svg_bar(x,y,stroke)
        svg_string += svg_bar(x,y-10,stroke)
        svg_string += svg_bar(x,y-20,stroke)
    elif n == 21:
        svg_string = svg_circle(x+20,y,3,stroke,stroke,2)
        svg_string += svg_circle(x+20,y-40,3,stroke,stroke,2)
    elif n == 22:
        svg_string = svg_circle(x+15,y,3,stroke,stroke,2)
        svg_string += svg_circle(x+25,y,3,stroke,stroke,2)
        svg_string += svg_circle(x+20,y-40,3,stroke,stroke,2)
    elif n == 33:
        svg_string = svg_bar(x,y,stroke)
        svg_string += svg_bar(x,y-10,stroke)
        svg_string += svg_circle(x+20,y-20,3,stroke,stroke,2)
        svg_string += svg_circle(x+20,y-40,3,stroke,stroke,2)
    return svg_string

def dots_in_a_line(n, stroke):
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
    svg_string = ""
    for i in range(n):
        svg_string += svg_line_of_dots(nn, 5, y, stroke)
        y += 20
    return svg_string

def points_in_a_star(n, stroke):
    svg_string = ""
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
        svg_string += svg_star(nn, x, y, stroke, stroke)
        if n == 2:
            x += 50
        else:
            x += 37.5
    return svg_string

def dots_in_a_circle(n, stroke):
    svg_string = ""
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
        svg_string += svg_circle_of_dots(nn, x, y, stroke, stroke)
        if n == 2:
            x += 50
        else:
            x += 37.5
    return svg_string

def number_hash(n, stroke):
    svg_string = ""
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
        svg_string += svg_hash(nn, 5, y, stroke)
        y += 20
    return svg_string

def dice(n, stroke):
    svg_string = ""
    if n == 5:
        svg_string += svg_die(5, 50, 25, stroke)
    elif n == 10:
        svg_string += svg_die(5, 30, 25, stroke)
        svg_string += svg_die(5, 70, 25, stroke)
    elif n == 15:
        svg_string += svg_die(5, 15, 25, stroke)
        svg_string += svg_die(5, 50, 25, stroke)
        svg_string += svg_die(5, 85, 25, stroke)
    elif n == 7:
        svg_string += svg_die(3, 50, 10, stroke)
        svg_string += svg_die(4, 50, 40, stroke)
    elif n == 14:
        svg_string += svg_die(4, 30, 10, stroke)
        svg_string += svg_die(3, 70, 10, stroke)
        svg_string += svg_die(3, 30, 40, stroke)
        svg_string += svg_die(4, 70, 40, stroke)
    elif n == 21:
        svg_string += svg_die(3, 15, 10, stroke)
        svg_string += svg_die(4, 50, 10, stroke)
        svg_string += svg_die(3, 85, 10, stroke)
        svg_string += svg_die(4, 15, 40, stroke)
        svg_string += svg_die(3, 50, 40, stroke)
        svg_string += svg_die(4, 85, 40, stroke)
    elif n == 11:
        svg_string += svg_die(5, 50, 10, stroke)
        svg_string += svg_die(6, 50, 40, stroke)
    elif n == 22:
        svg_string += svg_die(6, 30, 10, stroke)
        svg_string += svg_die(5, 70, 10, stroke)
        svg_string += svg_die(5, 30, 40, stroke)
        svg_string += svg_die(6, 70, 40, stroke)
    elif n == 33:
        svg_string += svg_die(5, 15, 10, stroke)
        svg_string += svg_die(6, 50, 10, stroke)
        svg_string += svg_die(5, 85, 10, stroke)
        svg_string += svg_die(6, 15, 40, stroke)
        svg_string += svg_die(5, 50, 40, stroke)
        svg_string += svg_die(6, 85, 40, stroke)
    return svg_string

def circle(x, style, stroke, fill):
    svg_string = ""
    if style == "none":
        svg_string += svg_circle(x+17,38,16,stroke,WHITE,1.8)
    elif style == "gradient":
        svg_string += svg_circle(x+17,38,16,stroke,fill,1.8)
    else:
        svg_string += svg_circle(x+17,38,16,stroke,stroke,1.8)
    svg_string += svg_circle(x+17,38,8,stroke,fill,1.8)
    return svg_string

def check_card(n, style, stroke, fill):
    svg_string = ""
    if n == 1:
       svg_string += svg_check(45.5, style, stroke, fill)
    elif n == 2:
       svg_string += svg_check(25.5, style, stroke, fill)
       svg_string += svg_check(65.5, style, stroke, fill)
    else:
       svg_string += svg_check( 5.5, style, stroke, fill)
       svg_string += svg_check(45.5, style, stroke, fill)
       svg_string += svg_check(85.5, style, stroke, fill)
    return svg_string

def cross_card(n, style, stroke, fill):
    svg_string = ""
    if n == 1:
       svg_string += svg_cross(45.5, style, stroke, fill)
    elif n == 2:
       svg_string += svg_cross(25.5, style, stroke, fill)
       svg_string += svg_cross(65.5, style, stroke, fill)
    else:
       svg_string += svg_cross( 5.5, style, stroke, fill)
       svg_string += svg_cross(45.5, style, stroke, fill)
       svg_string += svg_cross(85.5, style, stroke, fill)
    return svg_string

def circle_card(n, style, stroke, fill):
    svg_string = ""
    if n == 1:
       svg_string += circle(45.5, style, stroke, fill)
    elif n == 2:
       svg_string += circle(25.5, style, stroke, fill)
       svg_string += circle(65.5, style, stroke, fill)
    else:
       svg_string += circle( 5.5, style, stroke, fill)
       svg_string += circle(45.5, style, stroke, fill)
       svg_string += circle(85.5, style, stroke, fill)
    return svg_string

def number_arabic(n, stroke):
    return svg_text(63.5,55,48,stroke,"DejaVu","",str(n))
    return svg_string

def number_roman(n, stroke):
    return svg_text(63.5,53,32,stroke,"DejaVu Serif","",ROMAN_NUMERALS[n])

def number_chinese(n, stroke):
    return svg_text(63.5,55,48,stroke,"DejaVu","",CHINESE_NUMERALS[n])

def number_product(n, stroke):
    return svg_text(63.5,53,36,stroke,"DejaVu","",NUMBER_PRODUCTS[n])

def number_word(n, stroke):
    x = 63.5
    strings = NUMBER_NAMES[n].split(' ')
    svg_string = ""
    if len(strings) == 1:
        svg_string += svg_text(x,48,26,stroke,"DejaVu Serif","",strings[0])
    else:
        svg_string += svg_text(x,35,26,stroke,"DejaVu Serif","",strings[0])
        svg_string += svg_text(x,63,26,stroke,"DejaVu Serif","",strings[1])
    return svg_string

def number_card(t, n, stroke, methodX, methodO, methodC):
    if t == 0:
        return (methodX(n, stroke))
    elif t == 1:
        return (methodO(n, stroke))
    else:
        return (methodC(n, stroke))

def word_card(t, c, n, s):
    return svg_text(63.5,45.5,30,c[0],"DejaVu",s,"")

def pattern_card(t, c, n, s):
    pattern_styles = [cross_card, circle_card, check_card]
    return pattern_styles[CARD_TYPES.index(t)](n,s,c[0],c[1])

#
# Card generators
#
def generate_pattern_card(t,c,n,s,scale):
    svg_string = header(BLACK,COLOR_PAIRS[c][1],0.5,scale)
    svg_string += pattern_card(CARD_TYPES[t],COLOR_PAIRS[c],n+1,FILL_STYLES[s])
    svg_string += footer()
    return svg_string

def generate_number_card(t,c,n,s,number_types,scale):
    stab = {0:5,1:7,2:11}
    methodO = [number_roman, number_product, number_chinese, number_word,\
               number_mayan]
    methodC = [dots_in_a_line, dots_in_a_circle, points_in_a_star,\
                number_hash, dice]
    methodX = number_arabic
    svg_string = header(BLACK,COLOR_PAIRS[c][1],0.5,scale)
    svg_string += number_card(t,(n+1)*stab[s],COLOR_PAIRS[c][0],
                              methodX,methodO[number_types[0]],
                              methodC[number_types[1]])
    svg_string += footer()
    return svg_string

def generate_word_card(t,c,n,s,scale):
    svg_string = header(BLACK,COLOR_PAIRS[c][1],0.5,scale)
    svg_string += word_card(t,COLOR_PAIRS[c],n,WORD_STYLES[s])
    svg_string += footer()
    return svg_string

def generate_match_card(scale):
    svg_string = header("#A0A0A0","#F0F0F0",3.0,scale)
    svg_string += footer()
    return svg_string

def generate_selected_card(scale):
    svg_string = header(BLACK,"none",3.0,scale)
    svg_string += footer()
    return svg_string

def open_file(datapath, filename):
    return file(os.path.join(datapath, filename), "w")

def close_file(f):
    f.close()

def generator(datapath,mO=MAYAN,mC=HASH):
    generate_pattern_cards(datapath)
    generate_number_cards(datapath,[mO,mC])
    generate_word_cards(datapath)
    generate_extras(datapath)

def generate_pattern_cards(datapath):
    i = 0
    for t in range(3):
        for c in range(3):
            for n in range(3):
                for s in range(3):
                    filename = "pattern-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    f.write(generate_pattern_card(t,c,n,s,1))
                    close_file(f)
                    i += 1

def generate_number_cards(datapath,number_types):
    i = 0
    for t in range(3):
        for c in range(3):
            for n in range(3):
                for s in range(3):
                    filename = "number-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    f.write(generate_number_card(t,c,n,s,number_types,1))
                    close_file(f)
                    i += 1

def generate_word_cards(datapath):
    i = 0
    for t in range(3):
        for c in range(3):
            for n in range(3):
                for s in range(3):
                    filename = "word-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    f.write(generate_word_card(t,c,n,s,1))
                    close_file(f)
                    i += 1

def generate_extras(datapath):
    f = open_file(datapath, "match.svg")
    f.write(generate_match_card(1))
    close_file(f)
    f = open_file(datapath, "selected.svg")
    f.write(generate_selected_card(1))
    close_file(f)

def main():
    return 0

if __name__ == "__main__":
    if not os.path.exists(os.path.join(os.path.abspath('.'), 'images')):
        os.mkdir(os.path.join(os.path.abspath('.'), 'images'))
    generator(os.path.join(os.path.abspath('.'), 'images'))
    main()
