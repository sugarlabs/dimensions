#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (c) 2009,10 Walter Bender

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
from math import sin, cos, pi
from constants import *

#
# SVG generators
#
class SVG:
    def __init__(self):
        self._scale = 1
        self._stroke_width = 1
        self._fill = RED_FILL
        self._stroke = RED_STROKE
        self._font = 'DejaVu'

    def _svg_style(self, extras=""):
        return "%s%s%s%s%s%f%s%s%s" % ("style=\"fill:", self._fill, ";stroke:",
                                       self._stroke, ";stroke-width:",
                                       self._stroke_width, ";", extras,
                                       "\" />\n")

    def _svg_rect(self, w, h, rx, ry, x, y):
        svg_string = "       <rect\n"
        svg_string += "          width=\"%f\"\n" % (w)
        svg_string += "          height=\"%f\"\n" % (h)
        svg_string += "          rx=\"%f\"\n" % (rx)
        svg_string += "          ry=\"%f\"\n" % (ry)
        svg_string += "          x=\"%f\"\n" % (x)
        svg_string += "          y=\"%f\"\n" % (y)
        svg_string += self._svg_style()
        return svg_string

    def _svg_circle(self, cx, cy, r):
        svg_string = "       <circle\n"
        svg_string += "          cx=\"%f\"\n" % (cx)
        svg_string += "          cy=\"%f\"\n" % (cy)
        svg_string += "          r=\"%f\"\n" % (r)
        svg_string += self._svg_style()
        return svg_string

    def _svg_line(self, x1, y1, x2, y2):
        svg_string = "<line x1=\"%f\" y1=\"%f\" x2=\"%f\" y2=\"%f\"\n" % \
                      (x1, y1, x2, y2)
        svg_string += self._svg_style("stroke-linecap:round;")
        return svg_string

    def _svg_text(self, x, y, size, style, string):
        svg_string = "  <text\n"
        svg_string += "%s%s%s%s%s%s%s" % (
            "     style=\"font-size:12px;text-anchor:middle;", style,
            ";text-align:center;font-family:", self._font, ";fill:",
            self._stroke, ";\">\n")
        svg_string += "      <tspan\n"
        svg_string += "       x=\"%f\"\n" % (x)
        svg_string += "       y=\"%f\"\n" % (y)
        svg_string += "       style=\"font-size:%fpx;\">%s</tspan>\n" %\
                      (size, string)
        svg_string += "  </text>\n"
        return svg_string

    def _svg_check(self, x):
        svg_string = "%s%s%s%s%s%f%s" %\
            ("<path d=\"m 22.5,76.1 l -5.9,-5.9 -4.1,-4.1 c -0.7,-0.7 -1.2,",
             "-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 4.1,-4.1 1.1,0 2.2,0.5 2.9,1.2 l ",
             "4.1,4.1 14.1,-14.1 c 0.8,-0.7 1.8,-1.2 2.9,-1.2 2.3,0 4.1,1.9 ",
             "4.1,4.1 0,1.1 -0.5,2.2 -1.2,2.9 l -14.1,14.1 -5.7,5.9 z\"\n",
             "   transform=\"translate(",x-10,", -25)\"\n")
        svg_string += self._svg_style()
        return svg_string

    def _svg_cross(self, x):
        svg_string = "%s%s%s%s%s%s%s%s" % (
                "<path d=\"m 33.4,62.5 l 10.1,10.1 c 0.8,0.8 1.2,1.8 1.2,2.9 ",
                "0,2.3 -1.9,4.1 -4.1,4.1 -1.1,0 -2.2,-0.5 -2.9,-1.2 l ",
                "-10.1,-10.1 -10.1,10.1 c -0.8,0.8 -1.8,1.2 -2.9,1.2 -2.3,0 ",
                "-4.1,-1.9 -4.1,-4.1 0,-1.1 0.5,-2.2 1.2,-2.9 l 10.1,-10.1 ",
                "-10.1,-10.1 c -0.7,-0.7 -1.2,-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 ",
                "4.1,-4.1 1.1,0 2.2,0.5 2.9,1.2 l 10.1,10.1 10.1,-10.1 c ",
                "0.8,-0.7 1.8,-1.2 2.9,-1.2 2.3,0 4.1,1.9 4.1,4.1 0,1.1 ",
                "-0.5,2.2 -1.2,2.9 l -10.1,10.1 z\"\n")
        svg_string += "%s%f%s" % ("   transform=\"translate(",x-10,", -25)\"\n")
        svg_string += self._svg_style()
        return svg_string

    def _svg_circle_of_dots(self, n, x, y):
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
        self.set_stroke_width(2.0)
        for i in range(n):
            svg_string += self._svg_circle(nx, ny, 3)
            a += da
            nx = ox+sin(a)*r
            ny = oy+cos(a)*r
        svg_string += "</g>\n"
        return svg_string

    def _svg_line_of_dots(self, n, x, y):
        cxtab = {5:37.5,7:27.5,11:7.5,10:37.5,14:27.5,22:7.5,15:37.5,21:27.5,\
                 33:7.5}
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                     ")\">\n")
        cx = cxtab[n]
        self.set_stroke_width(2.0)
        for i in range(n):
            svg_string += self._svg_circle(cx, 5, 3)
            cx += 10
        svg_string += "</g>\n"
        return svg_string

    def _svg_hash(self, n, x, y):
        cxtab = {5:42.5,7:32.5,11:22.5,10:42.5,14:32.5,22:22.5,\
                 15:42.5,21:32.5,33:22.5}
        cy = 5
        x2 = cxtab[n]
        x1 = 7.5+x2
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                     ")\">\n")
        self.set_stroke_width(2.0)
        for i in range(n):
            if (i+1)%5==0:
                svg_string += self._svg_line(x1-40, 7.5, x2, 7.5)
            else:
                svg_string += self._svg_line(x1, 0, x2, 15)
            x1 += 7.5
            x2 += 7.5
        svg_string += "</g>\n"
        return svg_string

    def _svg_quipu(self, n, x, y):
        print "quipu: %d %d %d" % (n, x, y)
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                     ")\">\n")
        x2 = x
        self.set_stroke_width(2.0)
        svg_string += self._svg_line(x2-40, 7.5, x2+40, 7.5)
        x2 -= 20
        x1 = x2+7.5
        for i in range(n):
            svg_string += self._svg_line(x1, 0, x2, 15)
            x1 += 7.5
            x2 += 7.5
        svg_string += "</g>\n"
        return svg_string

    def _svg_die(self, n, x, y):
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                     ")\">\n")
        self.set_stroke_width(1.5)
        self.set_colors([self._stroke,"none"])
        svg_string += self._svg_rect(25, 25, 2, 2, 0, 0)
        self.set_stroke_width(2)
        self.set_colors([self._stroke,self._stroke])
        if n in [2,3,4,5,6]:
            svg_string += self._svg_circle(6, 6, 1.5)
            svg_string += self._svg_circle(19, 19, 1.5)
        if n in [1,3,5]:
            svg_string += self._svg_circle(12.5, 12.5, 1.5)
        if n in [4,5,6]:
            svg_string += self._svg_circle(19, 6, 1.5)
            svg_string += self._svg_circle(6, 19, 1.5)
        if n in [6]:
            svg_string += self._svg_circle(6, 12.5, 1.5)
            svg_string += self._svg_circle(19, 12.5, 1.5)
        svg_string += "</g>\n"
        return svg_string

    def _svg_star(self, n, x, y):
        turntable = {5:3,7:3,11:5}
        turns = turntable[n]
        x1 = 0
        y1 = 0
        a = 0
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(",x,", ",y,
                                     ")\">\n")
        self.set_stroke_width(1.8)
        for i in range(n*turns):
            x2 = x1+sin(a)*40
            y2 = y1+cos(a)*40
            svg_string += self._svg_line(x1, y1, x2, y2)
            x1 = x2
            y1 = y2
            a += turns*2*pi/n
        svg_string += "</g>\n"
        return svg_string

    def _svg_donut(self, x, style, stroke, fill):
        svg_string = ""
        if style == "none":
            self.set_colors([stroke, WHITE])
        elif style == "gradient":
            self.set_colors([stroke, fill])
        else:
            self.set_colors([stroke, stroke])
        svg_string += self._svg_circle(x+17, 38, 16)
        self.set_colors([stroke, fill])
        svg_string += self._svg_circle(x+17, 38, 8)
        return svg_string

    def _svg_bar(self, x, y):
        self.set_stroke_width(1.8)
        svg_string = "       <rect\n"
        svg_string += "          width=\"%f\"\n" % (40)
        svg_string += "          height=\"%f\"\n" % (5)
        svg_string += "          x=\"%f\"\n" % (x)
        svg_string += "          y=\"%f\"\n" % (y)
        svg_string += self._svg_style()
        return svg_string

    def _background(self):
        return self._svg_rect(124.5, 74.5, 11, 9, 0.25, 0.25)

    def header(self):
        svg_string = "<?xml version=\"1.0\" encoding=\"UTF-8\""
        svg_string += " standalone=\"no\"?>\n"
        svg_string += "<!-- Created with Emacs -->\n"
        svg_string += "<svg\n"
        svg_string += "   xmlns:svg=\"http://www.w3.org/2000/svg\"\n"
        svg_string += "   xmlns=\"http://www.w3.org/2000/svg\"\n"
        svg_string += "   version=\"1.0\"\n"
        svg_string += "%s%f%s" % ("   width=\"", 125*self._scale, "\"\n")
        svg_string += "%s%f%s" % ("   height=\"", 75*self._scale, "\">\n")
        svg_string += "%s%f%s%f%s" % ("<g\n       transform=\"matrix(", 
                                      self._scale, ",0,0,", self._scale,
                                      ",0,0)\">\n")
        svg_string += self._background()
        return svg_string

    def footer(self):
        svg_string = "</g>\n"
        svg_string += "</svg>\n"
        return svg_string

    #
    # Utility functions
    #
    def set_font(self, font='DejaVu'):
        self._font = font

    def set_scale(self, scale=1.0):
        self._scale = scale

    def set_colors(self, colors):
        self._stroke = colors[0]
        self._fill = colors[1]

    def set_stroke_width(self, stroke_width=1.8):
        self._stroke_width = stroke_width

    #
    # Card pattern generators
    #
    def number_incan(self, n):
        x = 20
        y = 30
        print "number incan: %d" % (n)
        svg_string = self._svg_quipu(int(n/10), x, y)
        x = 40
        svg_string += self._svg_quipu(n % 10, x, y)
        return svg_string

    def number_mayan(self, n):
        x = 42.5
        x1,x2,xc,x3,x4 = x+5,x+15,x+20,x+25,x+35
        y = 60
        y1s,y5s,y10s,y20s = y,y-10,y-20,y-40
        if n == 5:
            svg_string = self._svg_bar(x, y1s)
        elif n == 7:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_circle(x2, y5s, 3)
            svg_string += self._svg_circle(x3, y5s, 3)
        elif n == 10:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
        elif n == 11:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
            svg_string += self._svg_circle(x+20, y10s, 3)
        elif n == 14:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
            svg_string += self._svg_circle(x1, y10s, 3)
            svg_string += self._svg_circle(x2, y10s, 3)
            svg_string += self._svg_circle(x3, y10s, 3)
            svg_string += self._svg_circle(x4, y10s, 3)
        elif n == 15:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
            svg_string += self._svg_bar(x, y10s)
        elif n == 21:
            svg_string = self._svg_circle(xc, y1s, 3)
            svg_string += self._svg_circle(xc, y20s, 3)
        elif n == 22:
            svg_string = self._svg_circle(x2, y1s, 3)
            svg_string += self._svg_circle(x3, y1s, 3)
            svg_string += self._svg_circle(xc, y20s, 3)
        elif n == 33:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
            svg_string += self._svg_circle(x1,y10s,3)
            svg_string += self._svg_circle(xc,y10s,3)
            svg_string += self._svg_circle(x4,y10s,3)
            svg_string += self._svg_circle(xc,y20s,3)
        return svg_string

    def dots_in_a_line(self, n):
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
            svg_string += self._svg_line_of_dots(nn, 5, y)
            y += 20
        return svg_string

    def points_in_a_star(self, n):
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
            svg_string += self._svg_star(nn, x, y)
            if n == 2:
                x += 50
            else:
                x += 37.5
        return svg_string

    def dots_in_a_circle(self, n):
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
            svg_string += self._svg_circle_of_dots(nn, x, y)
            if n == 2:
                x += 50
            else:
                x += 37.5
        return svg_string

    def number_hash(self, n):
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
            svg_string += self._svg_hash(nn, 5, y)
            y += 20
        return svg_string

    def dice(self, n):
        svg_string = ""
        if n == 5:
            svg_string += self._svg_die(5, 50, 25)
        elif n == 10:
            svg_string += self._svg_die(4, 30, 10)
            svg_string += self._svg_die(1, 30, 40)
            svg_string += self._svg_die(2, 70, 10)
            svg_string += self._svg_die(3, 70, 40)
        elif n == 15:
            svg_string += self._svg_die(3, 15, 10)
            svg_string += self._svg_die(2, 15, 40)
            svg_string += self._svg_die(5, 50, 25)
            svg_string += self._svg_die(4, 85, 10)
            svg_string += self._svg_die(1, 85, 40)
        elif n == 7:
            svg_string += self._svg_die(3, 50, 10)
            svg_string += self._svg_die(4, 50, 40)
        elif n == 14:
            svg_string += self._svg_die(5, 30, 10)
            svg_string += self._svg_die(2, 30, 40)
            svg_string += self._svg_die(1, 70, 10)
            svg_string += self._svg_die(6, 70, 40)
        elif n == 21:
            svg_string += self._svg_die(3, 15, 10)
            svg_string += self._svg_die(4, 15, 40)
            svg_string += self._svg_die(6, 50, 10)
            svg_string += self._svg_die(1, 50, 40)
            svg_string += self._svg_die(5, 85, 10)
            svg_string += self._svg_die(2, 85, 40)
        elif n == 11:
            svg_string += self._svg_die(5, 50, 10)
            svg_string += self._svg_die(6, 50, 40)
        elif n == 22:
            svg_string += self._svg_die(6, 30, 10)
            svg_string += self._svg_die(5, 70, 10)
            svg_string += self._svg_die(5, 30, 40)
            svg_string += self._svg_die(6, 70, 40)
        elif n == 33:
            svg_string += self._svg_die(5, 15, 10)
            svg_string += self._svg_die(6, 50, 10)
            svg_string += self._svg_die(5, 85, 10)
            svg_string += self._svg_die(6, 15, 40)
            svg_string += self._svg_die(5, 50, 40)
            svg_string += self._svg_die(6, 85, 40)
        return svg_string

    def check_card(self, n, style, stroke, fill):
        svg_string = ""
        if style == "none":
            self.set_colors([stroke, WHITE])
        elif style == "gradient":
            self.set_colors([stroke, fill])
        else:
            self.set_colors([stroke, stroke])
        if n == 1:
           svg_string += self._svg_check(45.5)
        elif n == 2:
           svg_string += self._svg_check(25.5)
           svg_string += self._svg_check(65.5)
        else:
           svg_string += self._svg_check( 5.5)
           svg_string += self._svg_check(45.5)
           svg_string += self._svg_check(85.5)
        return svg_string

    def cross_card(self, n, style, stroke, fill):
        svg_string = ""
        if style == "none":
            self.set_colors([stroke, WHITE])
        elif style == "gradient":
            self.set_colors([stroke, fill])
        else:
            self.set_colors([stroke, stroke])
        if n == 1:
           svg_string += self._svg_cross(45.5)
        elif n == 2:
           svg_string += self._svg_cross(25.5)
           svg_string += self._svg_cross(65.5)
        else:
           svg_string += self._svg_cross( 5.5)
           svg_string += self._svg_cross(45.5)
           svg_string += self._svg_cross(85.5)
        return svg_string

    def circle_card(self, n, style, stroke, fill):
        svg_string = ""
        if n == 1:
           svg_string += self._svg_donut(45.5, style, stroke, fill)
        elif n == 2:
           svg_string += self._svg_donut(25.5, style, stroke, fill)
           svg_string += self._svg_donut(65.5, style, stroke, fill)
        else:
           svg_string += self._svg_donut( 5.5, style, stroke, fill)
           svg_string += self._svg_donut(45.5, style, stroke, fill)
           svg_string += self._svg_donut(85.5, style, stroke, fill)
        return svg_string

    def number_arabic(self, n):
        self.set_font("DejaVu")
        return self._svg_text(63.5, 55, 48, "", str(n))
        return svg_string

    def number_roman(self, n):
        self.set_font("DejaVu Serif")
        return self._svg_text(63.5, 53, 32, "", ROMAN_NUMERALS[n])

    def number_chinese(self, n):
        self.set_font("DejaVu")
        return self._svg_text(63.5, 55, 48, "", CHINESE_NUMERALS[n])

    def number_product(self, n):
        self.set_font("DejaVu")
        return self._svg_text(63.5, 53, 36, "", NUMBER_PRODUCTS[n])

    def number_word(self, n):
        x = 63.5
        strings = NUMBER_NAMES[n].split(' ')
        svg_string = ""
        self.set_font("DejaVu Serif")
        if len(strings) == 1:
            svg_string += self._svg_text(x, 48, 26, "", strings[0])
        else:
            svg_string += self._svg_text(x, 35, 26, "", strings[0])
            svg_string += self._svg_text(x, 63, 26, "", strings[1])
        return svg_string

    def number_card(self, t, n, stroke, methodX, methodO, methodC):
        self.set_colors([stroke, stroke])
        if t == 0:
            return (methodX(n))
        elif t == 1:
            return (methodO(n))
        else:
            return (methodC(n))

    def word_card(self, t, c, n, s):
        return ""

    def pattern_card(self, t, c, n, s):
        self.set_stroke_width(1.8)
        pattern_styles = [self.cross_card, self.circle_card, self.check_card]
        return pattern_styles[CARD_TYPES.index(t)](n, s, c[0], c[1])

#
# Card generators
#
def generate_pattern_card(t,c,n,s,scale):
    svg = SVG()
    svg.set_scale(scale)
    svg.set_stroke_width(0.5)
    svg.set_colors([BLACK,COLOR_PAIRS[c][1]])
    svg_string = svg.header()
    svg_string += svg.pattern_card(CARD_TYPES[t],COLOR_PAIRS[c],n+1,
                                   FILL_STYLES[s])
    svg_string += svg.footer()
    return svg_string

def generate_number_card(t,c,n,s,number_types,scale):
    svg = SVG()
    stab = {0:5,1:7,2:11}
    methodO = [svg.number_roman, svg.number_product, svg.number_chinese,\
               svg.number_word, svg.nummber_mayan, svg.number_incan]
    methodC = [svg.dots_in_a_line, svg.dots_in_a_circle, svg.points_in_a_star,\
               svg.number_hash, svg.dice]
    methodX = svg.number_arabic
    svg.set_scale(scale)
    svg.set_stroke_width(0.5)
    svg.set_colors([BLACK,COLOR_PAIRS[c][1]])
    svg_string = svg.header()
    svg_string += svg.number_card(t,(n+1)*stab[s],COLOR_PAIRS[c][0],
                              methodX,methodO[number_types[0]],
                              methodC[number_types[1]])
    svg_string += svg.footer()
    return svg_string

def generate_word_card(t,c,n,s,scale):
    svg = SVG()
    svg.set_scale(scale)
    svg.set_stroke_width(0.5)
    svg.set_colors([BLACK,COLOR_PAIRS[c][1]])
    svg_string = svg.header()
    svg_string += svg.word_card(t,COLOR_PAIRS[c],n,WORD_STYLES[s])
    svg_string += svg.footer()
    return svg_string

def generate_match_card(scale):
    svg = SVG()
    svg.set_scale(scale)
    svg.set_stroke_width(3.0)
    svg.set_colors(["#A0A0A0","#F0F0F0"])
    svg_string = svg.header()
    svg_string += svg.footer()
    return svg_string

def generate_selected_card(scale):
    svg = SVG()
    svg.set_scale(scale)
    svg.set_stroke_width(3.0)
    svg.set_colors([BLACK,"none"])
    svg_string = svg.header()
    svg_string += svg.footer()
    return svg_string

#
# Command line utilities used for testing purposed only
#
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
