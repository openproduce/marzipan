#!/usr/bin/env python

# This file is part of Marzipan, an open source point-of-sale system.
# Copyright (C) 2015 Open Produce LLC
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""font for big characters."""

class ASCIIFont:
    """ascii bitmap fonts."""

    def __init__(self, width, height, kern, bitmaps = {}):
        self.width = width
        self.height = height
        self.kern = kern
        self.bitmaps = bitmaps

    def get_row(self, char, i):
        return self.bitmaps[char][i]


big34 = ASCIIFont(3, 4, 1, {
    '-': ['   ',
          ' --',
          '   ',
          '   '],
    '0': [' _ ',
          '/ \\',
          '\\_/',
          '   '],
    '1': ['   ',
          '/| ',
          ' | ',
          '   '],
    '2': ['__ ',
          ' _)',
          '/__',
          '   '],
    '3': ['__ ',
          ' _)',
          '__)',
          '   '],
    '4': ['   ',
          '|_|',
          '  |',
          '   '],
    '5': [' __',
          '|_ ',
          '__)',
          '   '],
    '6': [' _ ',
          '/_ ',
          '\\_)',
          '   '],
    '7': ['___',
          '  /',
          ' / ',
          '   '],
    '8': [' _ ',
          '(_)',
          '(_)',
          '   '],
    '9': [' _ ',
          '(_\\',
          ' _/',
          '   '],
    '.': ['   ',
          '   ',
          ' o ',
          '   '],
    ' ': ['   ',
          '   ',
          '   ',
          '   '],
    })

