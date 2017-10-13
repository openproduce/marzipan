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

import sys
import os
import signal
import config
import time
import curses
import curses.wrapper
import ui.colors
import ui.dialogs
import register_logging


def main(stdscr):
    ui.colors.init()
    ui.layout.init(stdscr)
    stdscr.notimeout(1)
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    signal.signal(signal.SIGTTIN, signal.SIG_IGN)
    signal.signal(signal.SIGTTOU, signal.SIG_IGN)
    curses.curs_set(0) # hw cursor is too finicky to bother with
    sale_editor = ui.dialogs.SaleDialog()
    updater = ui.dialogs.SaleAsyncUpdater(sale_editor)
    updater.daemon = True
    updater.start()
    while True:
        import _curses
        try:
            sale_editor.main()
        except KeyboardInterrupt:
            stdscr.redrawwin()
            stdscr.refresh()
        except _curses.error:
            curses.curs_set(1)
            curses.endwin()
            print 'Your terminal is probably too small.'
            print 'Please make it at least 80x25 and try again.'
            sys.exit(1)
        except:
            curses.curs_set(1)
            curses.endwin()
            out=file('error', 'w')
            import traceback
            traceback.print_exc(file=out)
            out.close()
            raise

def start():
    curses.wrapper(main)

if __name__ == "__main__":
    config.parse_cmdline(sys.argv[1:])
    os.environ['ESCDELAY'] = '0'
    start()

