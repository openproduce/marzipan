#!/usr/bin/env python
"""customer-facing display. read updates over named pipe, """
import sys
import curses
import config

def banner(win):
    win.addstr(0,0,'Open Produce')

def main(stdscr):
    banner(stdscr)
    f = file(config.get('cui-pipe-path'), 'r')
    line = f.readline()
    while line != "":
        stdscr.addstr(1,0,line)
        line = f.readline()

if __name__ == '__main__':
    config.parse_cmdline(sys.argv[1:])
    sys.argv[1:]
    curses.wrapper(main)
