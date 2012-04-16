#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (c) 2009, 10 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA


import os
from gettext import gettext as _
from math import sin, cos, pi
from constants import *
FROWN = '☹'


class SVG:
    ''' SVG generators '''

    def __init__(self):
        self._scale = 1
        self._stroke_width = 1.0
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
        svg_string = "%s%s%s%s%s%f%s" % \
            ("<path d=\"m 22.5,76.1 l -5.9,-5.9 -4.1,-4.1 c -0.7,-0.7 -1.2,",
             "-1.8 -1.2,-2.9 0,-2.3 1.9,-4.1 4.1,-4.1 1.1,0 2.2,0.5 2.9,1.2 l",
             " 4.1,4.1 14.1,-14.1 c 0.8,-0.7 1.8,-1.2 2.9,-1.2 2.3,0 4.1,1.9 ",
             "4.1,4.1 0,1.1 -0.5,2.2 -1.2,2.9 l -14.1,14.1 -5.7,5.9 z\"\n",
             "   transform=\"translate(", x - 10, ", -25)\"\n")
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
        svg_string += "%s%f%s" % ("   transform=\"translate(", x - 10,
                                  ", -25)\"\n")
        svg_string += self._svg_style()
        return svg_string

    def _svg_circle_of_dots(self, n, x, y):
        rtab = {5: 9, 7: 13, 11: 17}
        r = rtab[n]
        ox = 0
        oy = 32.5
        da = pi * 2 / n
        a = 0
        nx = ox + sin(a) * r
        ny = oy + cos(a) * r
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(", x, ", ",
                                     y, ")\">\n")
        self._set_stroke_width(2.0)
        for i in range(n):
            svg_string += self._svg_circle(nx, ny, 3)
            a += da
            nx = ox + sin(a) * r
            ny = oy + cos(a) * r
        svg_string += "</g>\n"
        return svg_string

    def _svg_line_of_dots(self, n, x, y):
        cxtab = {5: 37.5, 7: 27.5, 11: 7.5, 10: 37.5, 14: 27.5, 22: 7.5,
                 15: 37.5, 21: 2.5, 33: 7.5}
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(", x, ", ",
                                     y, ")\">\n")
        cx = cxtab[n]
        self._set_stroke_width(2.0)
        for i in range(n):
            svg_string += self._svg_circle(cx, 5, 3)
            cx += 10
        svg_string += "</g>\n"
        return svg_string

    def _svg_hash(self, n, x, y):
        cxtab = {5: 42.5, 7: 32.5, 11: 22.5, 10: 42.5, 14: 32.5, 22: 22.5,
                 15: 42.5, 21: 32.5, 33: 22.5}
        cy = 5
        x2 = cxtab[n]
        x1 = 7.5 + x2
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(", x, ", ",
                                     y, ")\">\n")
        self._set_stroke_width(2.0)
        for i in range(n):
            if (i + 1) % 5 == 0:
                svg_string += self._svg_line(x1 - 40, 7.5, x2, 7.5)
            else:
                svg_string += self._svg_line(x1, 0, x2, 15)
            x1 += 7.5
            x2 += 7.5
        svg_string += "</g>\n"
        return svg_string

    def _svg_quipu(self, n, x, y):
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(", x, ", ",
                                     y, ")\">\n")
        x2 = x
        self._set_stroke_width(2.0)
        svg_string += self._svg_line(x2 - 40, 7.5, x2 + 40, 7.5)
        x2 -= 20
        x1 = x2 + 7.5
        for i in range(n):
            svg_string += self._svg_line(x1, 0, x2, 15)
            x1 += 7.5
            x2 += 7.5
        svg_string += "</g>\n"
        return svg_string

    def _svg_die(self, n, x, y):
        self._set_stroke_width(1.5)
        self._set_colors([self._stroke, "none"])
        svg_string = self._svg_rect(25, 25, 2, 2, x, y)
        self._set_stroke_width(2)
        self._set_colors([self._stroke, self._stroke])
        if n in [2, 3, 4, 5, 6]:
            svg_string += self._svg_circle(6 + x, 6 + y, 1.5)
            svg_string += self._svg_circle(19 + x, 19 + y, 1.5)
        if n in [1, 3, 5]:
            svg_string += self._svg_circle(12.5 + x, 12.5 + y, 1.5)
        if n in [4, 5, 6]:
            svg_string += self._svg_circle(19 + x, 6 + y, 1.5)
            svg_string += self._svg_circle(6 + x, 19 + y, 1.5)
        if n in [6]:
            svg_string += self._svg_circle(6 + x, 12.5 + y, 1.5)
            svg_string += self._svg_circle(19 + x, 12.5 + y, 1.5)
        return svg_string

    def _svg_star(self, n, x, y):
        turntable = {5: 3, 7: 3, 11: 5}
        turns = turntable[n]
        x1 = 0
        y1 = 0
        a = 0
        svg_string = "%s%f%s%f%s" % ("<g\n   transform=\"translate(", x, ", ",
                                     y, ")\">\n")
        self._set_stroke_width(1.8)
        for i in range(n * turns):
            x2 = x1 + sin(a) * 40
            y2 = y1 + cos(a) * 40
            svg_string += self._svg_line(x1, y1, x2, y2)
            x1 = x2
            y1 = y2
            a += turns * 2 * pi / n
        svg_string += "</g>\n"
        return svg_string

    def _svg_donut(self, x, style, stroke, fill):
        svg_string = ""
        if style == "none":
            self._set_colors([stroke, WHITE])
        elif style == "gradient":
            self._set_colors([stroke, fill])
        else:
            self._set_colors([stroke, stroke])
        svg_string += self._svg_circle(x + 17, 38, 16)
        self._set_colors([stroke, fill])
        svg_string += self._svg_circle(x + 17, 38, 8)
        return svg_string

    def _svg_bar(self, x, y):
        self._set_stroke_width(1.8)
        svg_string = "       <rect\n"
        svg_string += "          width=\"%f\"\n" % (40)
        svg_string += "          height=\"%f\"\n" % (5)
        svg_string += "          x=\"%f\"\n" % (x)
        svg_string += "          y=\"%f\"\n" % (y)
        svg_string += self._svg_style()
        return svg_string

    def _background(self):
        return self._svg_rect(124.5, 74.5, 11, 9, 0.25, 0.25)

    def _header(self):
        svg_string = "<?xml version=\"1.0\" encoding=\"UTF-8\""
        svg_string += " standalone=\"no\"?>\n"
        svg_string += "<!-- Created with Emacs -->\n"
        svg_string += "<svg\n"
        svg_string += "   xmlns:svg=\"http://www.w3.org/2000/svg\"\n"
        svg_string += "   xmlns=\"http://www.w3.org/2000/svg\"\n"
        svg_string += "   version=\"1.0\"\n"
        svg_string += "%s%f%s" % ("   width=\"", 125 * self._scale, "\"\n")
        svg_string += "%s%f%s" % ("   height=\"", 75 * self._scale, "\">\n")
        svg_string += "%s%f%s%f%s" % ("<g\n       transform=\"matrix(",
                                      self._scale, ", 0, 0, ", self._scale,
                                      ", 0, 0)\">\n")
        svg_string += self._background()
        return svg_string

    def _footer(self):
        svg_string = "</g>\n"
        svg_string += "</svg>\n"
        return svg_string

    #
    # Utility functions
    #
    def _set_font(self, font='DejaVu'):
        self._font = font

    def _set_scale(self, scale=1.0):
        self._scale = scale

    def _set_colors(self, colors):
        self._stroke = colors[0]
        self._fill = colors[1]

    def _set_stroke_width(self, stroke_width=1.8):
        self._stroke_width = stroke_width

    #
    # Card pattern generators
    #
    def _smiley(self):
        self._set_font("DejaVu")
        return self._svg_text(63.5, 63.5, 72, "", '☻')

    def _frowny(self):
        self._set_font("DejaVu")
        return self._svg_text(117, 63.5, 72, "", '☹')

    def _number_incan(self, number):
        x = 20
        y = 30
        svg_string = self._svg_quipu(int(number / 10), x, y)
        x = 40
        svg_string += self._svg_quipu(number % 10, x, y)
        return svg_string

    def _number_mayan(self, number):
        x = 42.5
        x1, x2, xc, x3, x4 = x + 5, x + 15, x + 20, x + 25, x + 35
        y = 60
        y1s, y5s, y10s, y20s = y, y - 10, y - 20, y - 40
        if number == 5:
            svg_string = self._svg_bar(x, y1s)
        elif number == 7:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_circle(x2, y5s, 3)
            svg_string += self._svg_circle(x3, y5s, 3)
        elif number == 10:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
        elif number == 11:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
            svg_string += self._svg_circle(x + 20, y10s, 3)
        elif number == 14:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
            svg_string += self._svg_circle(x1, y10s, 3)
            svg_string += self._svg_circle(x2, y10s, 3)
            svg_string += self._svg_circle(x3, y10s, 3)
            svg_string += self._svg_circle(x4, y10s, 3)
        elif number == 15:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
            svg_string += self._svg_bar(x, y10s)
        elif number == 21:
            svg_string = self._svg_circle(xc, y1s, 3)
            svg_string += self._svg_circle(xc, y20s, 3)
        elif number == 22:
            svg_string = self._svg_circle(x2, y1s, 3)
            svg_string += self._svg_circle(x3, y1s, 3)
            svg_string += self._svg_circle(xc, y20s, 3)
        elif number == 33:
            svg_string = self._svg_bar(x, y1s)
            svg_string += self._svg_bar(x, y5s)
            svg_string += self._svg_circle(x1, y10s, 3)
            svg_string += self._svg_circle(xc, y10s, 3)
            svg_string += self._svg_circle(x4, y10s, 3)
            svg_string += self._svg_circle(xc, y20s, 3)
        return svg_string

    def _dots_in_a_line(self, number):
        if number % 3 == 0:
            y = 12.5
            n = number / 3
        elif number % 2 == 0:
            y = 22.5
            n = number / 2
        else:
            y = 32.5
            n = number
        if number % 5 == 0:
            number /= 5
        elif number % 7 == 0:
            number /= 7
        else:
            number /= 11
        svg_string = ""
        for i in range(number):
            svg_string += self._svg_line_of_dots(n, 5, y)
            y += 20
        return svg_string

    def _points_in_a_star(self, number):
        svg_string = ""
        if number % 3 == 0:
            x = 25
            n = number / 3
        elif number % 2 == 0:
            x = 37.5
            n = number / 2
        else:
            x = 62.5
            n = number
        if number % 5 == 0:
            number /= 5
            y = 15
        elif number % 7 == 0:
            number /= 7
            y = 15
        else:
            number /= 11
            y = 15
        for i in range(number):
            if number == 3:
                if i == 0:
                    y += 12
                elif i == 1:
                    y -= 24
                else:
                    y += 24
            svg_string += self._svg_star(n, x, y)
            if number == 2:
                x += 50
            else:
                x += 37.5
        return svg_string

    def _dots_in_a_circle(self, number):
        svg_string = ""
        if number % 3 == 0:
            x = 25
            n = number / 3
        elif number % 2 == 0:
            x = 37.5
            n = number / 2
        else:
            x = 62.5
            n = number
        if number % 5 == 0:
            number /= 5
            y = 5
        elif number % 7 == 0:
            number /= 7
            y = 5
        else:
            number /= 11
            y = 5
        for i in range(number):
            if number == 3:
                if i == 0:
                    y += 12
                elif i == 1:
                    y -= 24
                else:
                    y += 24
            svg_string += self._svg_circle_of_dots(n, x, y)
            if number == 2:
                x += 50
            else:
                x += 37.5
        return svg_string

    def _number_hash(self, number):
        svg_string = ""
        if number % 3 == 0:
            y = 12.5
            n = number / 3
        elif number % 2 == 0:
            y = 22.5
            n = number / 2
        else:
            y = 32.5
            n = number
        if number % 5 == 0:
            number /= 5
        elif number % 7 == 0:
            number /= 7
        else:
            number /= 11
        for i in range(number):
            svg_string += self._svg_hash(n, 5, y)
            y += 20
        return svg_string

    def _dice(self, number):
        svg_string = ""
        if number == 5:
            svg_string += self._svg_die(5, 50, 25)
        elif number == 10:
            svg_string += self._svg_die(4, 30, 10)
            svg_string += self._svg_die(1, 30, 40)
            svg_string += self._svg_die(2, 70, 10)
            svg_string += self._svg_die(3, 70, 40)
        elif number == 15:
            svg_string += self._svg_die(3, 15, 10)
            svg_string += self._svg_die(2, 15, 40)
            svg_string += self._svg_die(5, 50, 25)
            svg_string += self._svg_die(4, 85, 10)
            svg_string += self._svg_die(1, 85, 40)
        elif number == 7:
            svg_string += self._svg_die(3, 50, 10)
            svg_string += self._svg_die(4, 50, 40)
        elif number == 14:
            svg_string += self._svg_die(5, 30, 10)
            svg_string += self._svg_die(2, 30, 40)
            svg_string += self._svg_die(1, 70, 10)
            svg_string += self._svg_die(6, 70, 40)
        elif number == 21:
            svg_string += self._svg_die(3, 15, 10)
            svg_string += self._svg_die(4, 15, 40)
            svg_string += self._svg_die(6, 50, 10)
            svg_string += self._svg_die(1, 50, 40)
            svg_string += self._svg_die(5, 85, 10)
            svg_string += self._svg_die(2, 85, 40)
        elif number == 11:
            svg_string += self._svg_die(5, 50, 10)
            svg_string += self._svg_die(6, 50, 40)
        elif number == 22:
            svg_string += self._svg_die(6, 30, 10)
            svg_string += self._svg_die(5, 70, 10)
            svg_string += self._svg_die(5, 30, 40)
            svg_string += self._svg_die(6, 70, 40)
        elif number == 33:
            svg_string += self._svg_die(5, 15, 10)
            svg_string += self._svg_die(6, 50, 10)
            svg_string += self._svg_die(5, 85, 10)
            svg_string += self._svg_die(6, 15, 40)
            svg_string += self._svg_die(5, 50, 40)
            svg_string += self._svg_die(6, 85, 40)
        return svg_string

    def _check_card(self, number, style, stroke, fill):
        svg_string = ""
        if style == "none":
            self._set_colors([stroke, WHITE])
        elif style == "gradient":
            self._set_colors([stroke, fill])
        else:
            self._set_colors([stroke, stroke])
        if number == 1:
            svg_string += self._svg_check(45.5)
        elif number == 2:
            svg_string += self._svg_check(25.5)
            svg_string += self._svg_check(65.5)
        else:
            svg_string += self._svg_check(5.5)
            svg_string += self._svg_check(45.5)
            svg_string += self._svg_check(85.5)
        return svg_string

    def _cross_card(self, number, style, stroke, fill):
        svg_string = ""
        if style == "none":
            self._set_colors([stroke, WHITE])
        elif style == "gradient":
            self._set_colors([stroke, fill])
        else:
            self._set_colors([stroke, stroke])
        if number == 1:
            svg_string += self._svg_cross(45.5)
        elif number == 2:
            svg_string += self._svg_cross(25.5)
            svg_string += self._svg_cross(65.5)
        else:
            svg_string += self._svg_cross(5.5)
            svg_string += self._svg_cross(45.5)
            svg_string += self._svg_cross(85.5)
        return svg_string

    def _circle_card(self, number, style, stroke, fill):
        svg_string = ""
        if number == 1:
            svg_string += self._svg_donut(45.5, style, stroke, fill)
        elif number == 2:
            svg_string += self._svg_donut(25.5, style, stroke, fill)
            svg_string += self._svg_donut(65.5, style, stroke, fill)
        else:
            svg_string += self._svg_donut(5.5, style, stroke, fill)
            svg_string += self._svg_donut(45.5, style, stroke, fill)
            svg_string += self._svg_donut(85.5, style, stroke, fill)
        return svg_string

    def _number_arabic(self, number):
        self._set_font("DejaVu")
        return self._svg_text(63.5, 55, 48, "", str(number))
        return svg_string

    def _number_roman(self, number):
        self._set_font("DejaVu Serif")
        return self._svg_text(63.5, 53, 32, "", ROMAN_NUMERALS[number])

    def _number_chinese(self, number):
        self._set_font("DejaVu")
        return self._svg_text(63.5, 55, 48, "", CHINESE_NUMERALS[number])

    def _number_product(self, number):
        self._set_font("DejaVu")
        return self._svg_text(63.5, 53, 36, "", NUMBER_PRODUCTS[number])

    def _number_word(self, number):
        x = 63.5
        strings = NUMBER_NAMES[number].split(' ')
        svg_string = ""
        self._set_font("DejaVu Serif")
        if len(strings) == 1:
            svg_string += self._svg_text(x, 48, 26, "", strings[0])
        else:
            svg_string += self._svg_text(x, 35, 26, "", strings[0])
            svg_string += self._svg_text(x, 63, 26, "", strings[1])
        return svg_string

    def _number_card(self, shape, number, stroke, methodX, methodO, methodC):
        self._set_colors([stroke, stroke])
        if shape == 0:
            return (methodX(number))
        elif shape == 1:
            return (methodO(number))
        else:
            return (methodC(number))

    def _pattern_card(self, shape, color, number, fill):
        self._set_stroke_width(1.8)
        pattern_styles = [self._cross_card, self._circle_card,
                          self._check_card]
        return pattern_styles[CARD_TYPES.index(shape)](number, fill, color[0],
                                                       color[1])

# Card generators


def generate_smiley(scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_colors([YELLOW, BLACK])
    svg_string = svg._header()
    svg_string += svg._smiley()
    svg_string += svg._footer()
    return svg_string


def generate_frowny(scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_colors([BLACK, YELLOW])
    svg_string = svg._header()
    # svg_string += svg._frowny()
    svg_string += svg._footer()
    return svg_string


def generate_frowny_shape(scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_colors([BLACK, YELLOW])
    svg_string = svg._header()
    svg_string += '\
  <path\
     d="m 40.725683,37.5 5.05,5.05 c 0.4,0.4 0.6,0.9 0.6,1.45 0,1.15 -0.95,2.05 -2.05,2.05 -0.55,0 -1.1,-0.25 -1.45,-0.6 l -5.05,-5.05 -5.05,5.05 c -0.4,0.4 -0.9,0.6 -1.45,0.6 -1.15,0 -2.05,-0.95 -2.05,-2.05 0,-0.55 0.25,-1.1 0.6,-1.45 l 5.05,-5.05 -5.05,-5.05 c -0.35,-0.35 -0.6,-0.9 -0.6,-1.45 0,-1.15 0.95,-2.05 2.05,-2.05 0.55,0 1.1,0.25 1.45,0.6 l 5.05,5.05 5.05,-5.05 c 0.4,-0.35 0.9,-0.6 1.45,-0.6 1.15,0 2.05,0.95 2.05,2.05 0,0.55 -0.25,1.1 -0.6,1.45 l -5.05,5.05 z"\
     style="fill:%s;fill-opacity:1;stroke:%s;stroke-width:0.9;stroke-opacity:1" />\
  <g\
     transform="translate(0.26,0)">\
    <circle\
       cx="42.5"\
       cy="38"\
       r="16"\
       transform="matrix(0.53254438,0,0,0.53254438,39.618381,17.263314)"\
       style="fill:%s;fill-opacity:1;stroke:%s;stroke-width:1.8;stroke-opacity:1" />\
    <circle\
       cx="42.5"\
       cy="38"\
       r="8"\
       transform="matrix(0.53254438,0,0,0.53254438,39.618381,17.263314)"\
       style="fill:%s;fill-opacity:1;stroke:%s;stroke-width:1.8;stroke-opacity:1" />\
  </g>\
  <g\
     transform="translate(1.4,0)">\
    <circle\
       cx="82.5"\
       cy="38"\
       r="16"\
       transform="matrix(0.53254438,0,0,0.53254438,41.902464,17.263314)"\
       style="fill:%s;fill-opacity:1;stroke:%s;stroke-width:1.8;stroke-opacity:1" />\
    <circle\
       cx="82.5"\
       cy="38"\
       r="8"\
       transform="matrix(0.53254438,0,0,0.53254438,41.902464,17.263314)"\
       style="fill:%s;fill-opacity:1;stroke:%s;stroke-width:1.8;stroke-opacity:1" />\
  </g>\
  <text\
     x="3.1"\
     y="44.1"\
     style="font-size:18px;fill:%s;stroke:none;font-family:Sans"><tspan\
       x="3.8"\
       y="44.1"\
       style="font-size:18px;fill:%s;fill-opacity:1;stroke:none">%s</tspan></text>\
  <text\
     x="102.5"\
     y="44.1"\
     style="font-size:18px;fill:%s;stroke:none;font-family:Sans"><tspan\
       x="102.5"\
       y="44.1"\
       style="font-size:18px;fill:%s;fill-opacity:1;stroke:none">%s</tspan></text>\
' % (
        BLACK, BLACK, BLACK, BLACK, YELLOW, BLACK, BLACK, BLACK,
        YELLOW, BLACK, BLACK, BLACK, FROWN, BLACK, BLACK, FROWN)
    svg_string += svg._footer()
    return svg_string


def generate_frowny_color(scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_colors([BLACK, YELLOW])
    svg_string = svg._header()
    svg_string += '\
  <path\
     d="m 40.725683,37.5 5.05,5.05 c 0.4,0.4 0.6,0.9 0.6,1.45 0,1.15 -0.95,2.05 -2.05,2.05 -0.55,0 -1.1,-0.25 -1.45,-0.6 l -5.05,-5.05 -5.05,5.05 c -0.4,0.4 -0.9,0.6 -1.45,0.6 -1.15,0 -2.05,-0.95 -2.05,-2.05 0,-0.55 0.25,-1.1 0.6,-1.45 l 5.05,-5.05 -5.05,-5.05 c -0.35,-0.35 -0.6,-0.9 -0.6,-1.45 0,-1.15 0.95,-2.05 2.05,-2.05 0.55,0 1.1,0.25 1.45,0.6 l 5.05,5.05 5.05,-5.05 c 0.4,-0.35 0.9,-0.6 1.45,-0.6 1.15,0 2.05,0.95 2.05,2.05 0,0.55 -0.25,1.1 -0.6,1.45 l -5.05,5.05 z"\
     style="fill:#ff6040;fill-opacity:1;stroke:#ff6040;stroke-width:0.89999998;stroke-opacity:1" />\
  <path\
     d="m 90.100682,37.5 5.05,5.05 c 0.4,0.4 0.6,0.9 0.6,1.45 0,1.15 -0.95,2.05 -2.05,2.05 -0.55,0 -1.1,-0.25 -1.45,-0.6 l -5.05,-5.05 -5.05,5.05 c -0.4,0.4 -0.9,0.6 -1.45,0.6 -1.15,0 -2.05,-0.95 -2.05,-2.05 0,-0.55 0.25,-1.1 0.6,-1.45 l 5.05,-5.05 -5.05,-5.05 c -0.35,-0.35 -0.6,-0.9 -0.6,-1.45 0,-1.15 0.95,-2.05 2.05,-2.05 0.55,0 1.1,0.25 1.45,0.6 l 5.05,5.05 5.05,-5.05 c 0.4,-0.35 0.9,-0.6 1.45,-0.6 1.15,0 2.05,0.95 2.05,2.05 0,0.55 -0.25,1.1 -0.6,1.45 l -5.05,5.05 z"\
     style="fill:#00b418;fill-opacity:1;stroke:#00b418;stroke-width:0.89999998;stroke-opacity:1" />\
  <path\
     d="m 65.413182,37.5 5.05,5.05 c 0.4,0.4 0.6,0.9 0.6,1.45 0,1.15 -0.95,2.05 -2.05,2.05 -0.55,0 -1.1,-0.25 -1.45,-0.6 l -5.05,-5.05 -5.05,5.05 c -0.4,0.4 -0.9,0.6 -1.45,0.6 -1.15,0 -2.05,-0.95 -2.05,-2.05 0,-0.55 0.25,-1.1 0.6,-1.45 l 5.05,-5.05 -5.05,-5.05 c -0.35,-0.35 -0.6,-0.9 -0.6,-1.45 0,-1.15 0.95,-2.05 2.05,-2.05 0.55,0 1.1,0.25 1.45,0.6 l 5.05,5.05 5.05,-5.05 c 0.4,-0.35 0.9,-0.6 1.45,-0.6 1.15,0 2.05,0.95 2.05,2.05 0,0.55 -0.25,1.1 -0.6,1.45 l -5.05,5.05 z"\
     style="fill:#ff6040;fill-opacity:1;stroke:#ff6040;stroke-width:0.89999998;stroke-opacity:1" />\
  <text\
     x="3.1"\
     y="44.1"\
     style="font-size:18px;fill:%s;stroke:none;font-family:Sans"><tspan\
       x="3.8"\
       y="44.1"\
       style="font-size:18px;fill:%s;fill-opacity:1;stroke:none">%s</tspan></text>\
  <text\
     x="102.5"\
     y="44.1"\
     style="font-size:18px;fill:%s;stroke:none;font-family:Sans"><tspan\
       x="102.5"\
       y="44.1"\
       style="font-size:18px;fill:%s;fill-opacity:1;stroke:none">%s</tspan></text>\
' % (BLACK, BLACK, FROWN, BLACK, BLACK, FROWN)
    svg_string += svg._footer()
    return svg_string


def generate_frowny_number(scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_colors([BLACK, YELLOW])
    svg_string = svg._header()
    svg_string += '\
  <text\
     x="28.9"\
     y="46.2"\
     style="font-size:24px;fill:#000000;stroke:none;font-family:Sans"><tspan\
       x="28.9"\
       y="46.2"\
       style="font-size:24px;font-weight:bold;fill:%s;fill-opacity:1">1</tspan></text>\
  <text\
     x="53.6"\
     y="46.2"\
     style="font-size:24px;fill:#000000;fill-opacity:1;font-family:Sans"><tspan\
       x="53.6"\
       y="46.2"\
       style="font-size:24px;font-weight:bold;fill:%s;fill-opacity:1">1</tspan></text>\
  <text\
     x="78.9"\
     y="46.4"\
     style="font-size:11px;fill:#000000;fill-opacity:1;stroke:none;font-family:Sans"><tspan\
       x="78.9"\
       y="46.4"\
       style="font-size:24px;font-weight:bold;fill:%s;fill-opacity:1">2</tspan></text>\
  <text\
     x="3.1"\
     y="44.1"\
     style="font-size:18px;fill:%s;stroke:none;font-family:Sans"><tspan\
       x="3.8"\
       y="44.1"\
       style="font-size:18px;fill:%s;fill-opacity:1;stroke:none">%s</tspan></text>\
  <text\
     x="102.5"\
     y="44.1"\
     style="font-size:18px;fill:%s;stroke:none;font-family:Sans"><tspan\
       x="102.5"\
       y="44.1"\
       style="font-size:18px;fill:%s;fill-opacity:1;stroke:none">%s</tspan></text>\
' % (
        BLACK, BLACK, BLACK, BLACK, BLACK, FROWN, BLACK, BLACK, FROWN)
    svg_string += svg._footer()
    return svg_string


def generate_frowny_texture(scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_colors([BLACK, YELLOW])
    svg_string = svg._header()
    svg_string += '\
  <path\
     d="m 40.725683,37.5 5.05,5.05 c 0.4,0.4 0.6,0.9 0.6,1.45 0,1.15 -0.95,2.05 -2.05,2.05 -0.55,0 -1.1,-0.25 -1.45,-0.6 l -5.05,-5.05 -5.05,5.05 c -0.4,0.4 -0.9,0.6 -1.45,0.6 -1.15,0 -2.05,-0.95 -2.05,-2.05 0,-0.55 0.25,-1.1 0.6,-1.45 l 5.05,-5.05 -5.05,-5.05 c -0.35,-0.35 -0.6,-0.9 -0.6,-1.45 0,-1.15 0.95,-2.05 2.05,-2.05 0.55,0 1.1,0.25 1.45,0.6 l 5.05,5.05 5.05,-5.05 c 0.4,-0.35 0.9,-0.6 1.45,-0.6 1.15,0 2.05,0.95 2.05,2.05 0,0.55 -0.25,1.1 -0.6,1.45 l -5.05,5.05 z"\
     style="fill:%s;fill-opacity:1;stroke:%s;stroke-width:0.9;stroke-opacity:1" />\
  <path\
     d="m 90.100682,37.5 5.05,5.05 c 0.4,0.4 0.6,0.9 0.6,1.45 0,1.15 -0.95,2.05 -2.05,2.05 -0.55,0 -1.1,-0.25 -1.45,-0.6 l -5.05,-5.05 -5.05,5.05 c -0.4,0.4 -0.9,0.6 -1.45,0.6 -1.15,0 -2.05,-0.95 -2.05,-2.05 0,-0.55 0.25,-1.1 0.6,-1.45 l 5.05,-5.05 -5.05,-5.05 c -0.35,-0.35 -0.6,-0.9 -0.6,-1.45 0,-1.15 0.95,-2.05 2.05,-2.05 0.55,0 1.1,0.25 1.45,0.6 l 5.05,5.05 5.05,-5.05 c 0.4,-0.35 0.9,-0.6 1.45,-0.6 1.15,0 2.05,0.95 2.05,2.05 0,0.55 -0.25,1.1 -0.6,1.45 l -5.05,5.05 z"\
     style="fill:%s;fill-opacity:1;stroke:%s;stroke-width:0.9;stroke-opacity:1" />\
  <path\
     d="m 65.413182,37.5 5.05,5.05 c 0.4,0.4 0.6,0.9 0.6,1.45 0,1.15 -0.95,2.05 -2.05,2.05 -0.55,0 -1.1,-0.25 -1.45,-0.6 l -5.05,-5.05 -5.05,5.05 c -0.4,0.4 -0.9,0.6 -1.45,0.6 -1.15,0 -2.05,-0.95 -2.05,-2.05 0,-0.55 0.25,-1.1 0.6,-1.45 l 5.05,-5.05 -5.05,-5.05 c -0.35,-0.35 -0.6,-0.9 -0.6,-1.45 0,-1.15 0.95,-2.05 2.05,-2.05 0.55,0 1.1,0.25 1.45,0.6 l 5.05,5.05 5.05,-5.05 c 0.4,-0.35 0.9,-0.6 1.45,-0.6 1.15,0 2.05,0.95 2.05,2.05 0,0.55 -0.25,1.1 -0.6,1.45 l -5.05,5.05 z"\
     style="fill:%s;fill-opacity:1;stroke:%s;stroke-width:0.9;stroke-opacity:1" />\
  <text\
     x="3.1"\
     y="44.1"\
     style="font-size:18px;fill:%s;stroke:none;font-family:Sans"><tspan\
       x="3.8"\
       y="44.1"\
       style="font-size:18px;fill:%s;fill-opacity:1;stroke:none">%s</tspan></text>\
  <text\
     x="102.5"\
     y="44.1"\
     style="font-size:18px;fill:%s;stroke:none;font-family:Sans"><tspan\
       x="102.5"\
       y="44.1"\
       style="font-size:18px;fill:%s;fill-opacity:1;stroke:none">%s</tspan></text>\
' % (
        BLACK, BLACK, YELLOW, BLACK, BLACK, BLACK,
        BLACK, BLACK, FROWN, BLACK, BLACK, FROWN)
    svg_string += svg._footer()
    return svg_string


def generate_pattern_card(shape, color, number, fill, scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_stroke_width(0.5)
    svg._set_colors([BLACK, COLOR_PAIRS[color][1]])
    svg_string = svg._header()
    svg_string += svg._pattern_card(CARD_TYPES[shape], COLOR_PAIRS[color],
                                    number + 1, FILL_STYLES[fill])
    svg_string += svg._footer()
    return svg_string


def generate_number_card(shape, color, number, fill, number_types, scale):
    svg = SVG()
    stab = {0: 5, 1: 7, 2: 11}
    methodO = [svg._number_roman, svg._number_product, svg._number_chinese,
               svg._number_word, svg._number_mayan, svg._number_incan]
    methodC = [svg._dots_in_a_line, svg._dots_in_a_circle,
               svg._points_in_a_star, svg._number_hash, svg._dice]
    methodX = svg._number_arabic
    svg._set_scale(scale)
    svg._set_stroke_width(0.5)
    svg._set_colors([BLACK, COLOR_PAIRS[color][1]])
    svg_string = svg._header()
    svg_string += svg._number_card(shape, (number + 1) * stab[fill],
                                  COLOR_PAIRS[color][0],
                                  methodX, methodO[number_types[0]],
                                  methodC[number_types[1]])
    svg_string += svg._footer()
    return svg_string


def generate_word_card(shape, color, number, fill, scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_stroke_width(0.5)
    if number == 0:
        _stroke = DARK_COLOR[color]
    elif number == 1:
        _stroke = COLOR_PAIRS[color][1]
    else:
        _stroke = COLOR_PAIRS[color][0]
    if fill == 0:
        _fill = COLOR_PAIRS[color][1]
    elif fill == 1:
        _fill = COLOR_PAIRS[color][0]
    else:
        _fill = DARK_COLOR[color]
    svg._set_colors([_stroke, _fill])
    svg._set_stroke_width(3.0)
    svg_string = svg._header()
    svg_string += svg._footer()
    return svg_string


def generate_match_card(scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_stroke_width(6.0)
    svg._set_colors(["#A0A0A0", "#F0F0F0"])
    svg_string = svg._header()
    svg_string += svg._footer()
    return svg_string


def generate_selected_card(scale):
    svg = SVG()
    svg._set_scale(scale)
    svg._set_stroke_width(6.0)
    svg._set_colors([BLACK, "none"])
    svg_string = svg._header()
    svg_string += svg._footer()
    return svg_string

# Command line utilities used for testing purposed only


def open_file(datapath, filename):
    return file(os.path.join(datapath, filename), "w")


def close_file(f):
    f.close()


def generator(datapath, mO=MAYAN, mC=HASH):
    generate_pattern_cards(datapath)
    generate_number_cards(datapath, [mO, mC])
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
                    f.write(generate_pattern_card(t, c, n, s, 1))
                    close_file(f)
                    i += 1


def generate_number_cards(datapath, number_types):
    i = 0
    for t in range(3):
        for c in range(3):
            for n in range(3):
                for s in range(3):
                    filename = "number-%d.svg" % (i)
                    f = open_file(datapath, filename)
                    f.write(generate_number_card(t, c, n, s, number_types, 1))
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
                    f.write(generate_word_card(t, c, n, s, 1))
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
