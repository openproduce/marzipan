#!/usr/bin/env python
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


