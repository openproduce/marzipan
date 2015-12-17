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

"""color scheme"""
import curses

TEXT_ENTRY_COLOR = 1
LABEL_COLOR = 2
ACTIVE_SEL_COLOR = 3
INACTIVE_SEL_COLOR = 4
BUTTON_COLOR = 5
FRAME_BG = 6
ALERT_COLOR = 7
HELP_COLOR = 8

def init():
    curses.init_pair(TEXT_ENTRY_COLOR, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(LABEL_COLOR, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(ACTIVE_SEL_COLOR, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(INACTIVE_SEL_COLOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(BUTTON_COLOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(FRAME_BG, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(ALERT_COLOR, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(HELP_COLOR, curses.COLOR_WHITE, curses.COLOR_RED)


