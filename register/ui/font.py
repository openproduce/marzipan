#!/usr/bin/env python
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

