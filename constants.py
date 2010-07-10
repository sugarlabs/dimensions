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

from gettext import gettext as _
MATCH_POSITION = 10
SHAPES = 3
COLORS = 3
NUMBER = 3
FILLS = 3
DECKSIZE = SHAPES * COLORS * NUMBER * FILLS
DEAL = 12
EXTRAS = 3
SELECTMASK = -1
MATCHMASK = -2
CARD_WIDTH = 125
CARD_HEIGHT = 75
ROW = 5
COL = 3
KEYMAP = ['1', '2', '3', 'q', 'w', 'e', 'a', 's', 'd', 'z', 'x', 'c', '8',
          '9', '0']
ROMAN = 0
PRODUCT = 1
CHINESE = 2
WORD = 3
MAYAN = 4
LINES = 0
DOTS = 1
STAR = 2
HASH = 3
DICE = 4
LOW = 'low'
MEDIUM = 'medium'
HIGH = 'high'
RED_STROKE = "#FF6040"
RED_FILL = "#FFC4B8"
BLUE_STROKE = "#0060C8"
BLUE_FILL = "#ACC8E4"
GREEN_STROKE = "#00B418"
GREEN_FILL = "#AFE8A8"
BLACK = "#000000"
WHITE = "#FFFFFF"
COLOR_PAIRS = ([RED_STROKE, RED_FILL],
               [GREEN_STROKE, GREEN_FILL],
               [BLUE_STROKE, BLUE_FILL])
FILL_STYLES = ["solid", "none", "gradient"]
CARD_TYPES = ["X", "O", "C"]
ROMAN_NUMERALS = {5: 'V', 7: 'VII', 10: 'X', 11: 'XI', 14: 'XIV', 15: 'XV',
                  21: 'XXI', 22: 'XXII', 33: 'XXXIII'}
NUMBER_NAMES = {5: _('five'), 7: _('seven'), 11: _('eleven'), 10: _('ten'),
                14: _('fourteen'), 15: _('fifteen'), 22: _('twenty two'),
                21: _('twenty one'), 33: _('thirty three')}
NUMBER_PRODUCTS = {5: '1×5', 7: '1×7', 11: '1×11', 10: '2×5',
                   14: '2×7', 15: '3×5', 22: '2×11',
                   21: '3×7', 33: '3×11'}
CHINESE_NUMERALS = {5: '五', 7: '七', 10: '十', 11: '十一', 14: '十四',
                    15: '十五', 21: '廿一', 22: '廿二', 33: '卅三'}
WORD_STYLES = ["font-weight: bold", "", "font-style: italic"]
WORD_CARD_INDICIES = [1, 4, 7, 37, 40, 43, 73, 76, 79, None, None, None, None,
                      None, None]
WORD_CARD_MAP = {1: (0, 0), 4: (0, 1), 7: (0, 2), 37: (1, 0), 40: (1, 1),
                 43: (1, 2), 73: (2, 0), 76: (2, 1), 79: (2, 2)}

# 'dead key' Unicode dictionaries
DEAD_KEYS = ['grave', 'acute', 'circumflex', 'tilde', 'diaeresis', 'abovering']
DEAD_DICTS = [{'A': 192, 'E': 200, 'I': 204, 'O': 210, 'U': 217, 'a': 224,
               'e': 232, 'i': 236, 'o': 242, 'u': 249},
              {'A': 193, 'E': 201, 'I': 205, 'O': 211, 'U': 218, 'a': 225,
               'e': 233, 'i': 237, 'o': 243, 'u': 250},
              {'A': 194, 'E': 202, 'I': 206, 'O': 212, 'U': 219, 'a': 226,
               'e': 234, 'i': 238, 'o': 244, 'u': 251},
              {'A': 195, 'O': 211, 'N': 209, 'U': 360, 'a': 227, 'o': 245,
               'n': 241, 'u': 361},
              {'A': 196, 'E': 203, 'I': 207, 'O': 211, 'U': 218, 'a': 228,
               'e': 235, 'i': 239, 'o': 245, 'u': 252},
              {'A': 197, 'a': 229}]
NOISE_KEYS = ['Shift_L', 'Shift_R', 'Control_L', 'Caps_Lock', 'Pause',
              'Alt_L', 'Alt_R', 'KP_Enter', 'ISO_Level3_Shift', 'KP_Divide',
              'Escape', 'Return', 'KP_Page_Up', 'Up', 'Down', 'Menu',
              'Left', 'Right', 'KP_Home', 'KP_End', 'KP_Up', 'Super_L',
              'KP_Down', 'KP_Left', 'KP_Right', 'KP_Page_Down', 'Scroll_Lock',
              'Page_Down', 'Page_Up']
WHITE_SPACE = ['space', 'Tab']
