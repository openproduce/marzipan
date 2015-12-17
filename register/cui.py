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
