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

import os
import signal
import curses
import curses.panel
from . import widgets
from .widgets import *

class TerminalTooSmallError(Exception):
    """terminal too small to display ui without curses barfing"""
    def __init__(self, columns, lines):
        self.columns = columns
        self.lines = lines
    def __str__(self):
        return "terminal too small at %dx%d, please make your window bigger."%(
                self.columns, self.lines)


class Layout:
    """rules for spacing frames inside window."""
    def __init__(self):
        self.fill = True
        self.window = None
        self.panel = None
        self.width = None
        self.height = None

    def make_window(self):
        self.fill = True
        self.window = curses.newwin(int(self.height), int(self.width), int(self.y), int(self.x))
        self.window.keypad(1)
        self.panel = curses.panel.new_panel(self.window)
        self.panel.top()
        curses.panel.update_panels()

    def set_base_size(self, width, height):
        self.width = width
        self.height = height

    def pack(self):
        pass

    def grow(self, frame):
        pass


class Fixed(Layout):
    """static screen position."""
    def __init__(self, x, y):
        Layout.__init__(self)
        self.x = x
        self.y = y

    def pack(self):
        if self.x + self.width > columns:
            self.x = columns - self.width
        if self.y + self.height > lines:
            self.y = lines - self.height
        if self.x < 0 or self.y < 0:
            raise TerminalTooSmallError(columns, lines)
        self.make_window()


class Center(Layout):
    """center on screen."""
    def __init__(self):
        Layout.__init__(self)

    def pack(self):
        self.x = columns/2 - self.width/2
        self.y = lines/2 - self.height/2
        self.make_window()


class BottomEdge(Layout):
    """align bottom edge to bottom of screen."""
    def __init__(self, x, margin=0):
        Layout.__init__(self)
        self.x = x
        self.margin = margin

    def pack(self):
        self.y = lines - self.height - self.margin
        self.make_window()


class FillRightDown(Layout):
    """fill out space to edge of screen."""
    def __init__(self, x, y, fill_to_bottom=False):
        self.x = x
        self.y = y
        self.extra_width = 0
        self.extra_height = 0
        self.fill_to_bottom = fill_to_bottom

    def pack(self):
        base_width = self.width
        base_height = self.height
        if self.fill_to_bottom:
            self.height = lines - self.y - 2
        self.width = columns - self.x - 2
        self.extra_width = self.width - base_width
        self.extra_height = self.height - base_height
        self.make_window()

    def grow(self, frame):
        for widget in frame.focus_order:
            widget.grow(self.extra_width, self.extra_height)


_frames = []
def add_frame(frame):
    global _frames
    _frames.append(frame)

def del_frame(frame):
    global _frames
    try:
        _frames.remove(frame)
    except:
        pass

_stdscr = None
lines = 25
columns = 80
def resize():
    global lines
    global columns
    (lines, columns) = _stdscr.getmaxyx()
    for f in _frames:
        f.layout.pack()
        f.layout.grow(f)

def init(stdscr):
    global _stdscr
    _stdscr = stdscr
    resize()


