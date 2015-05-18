#!/usr/bin/env/python
import sys
import os
import signal
import config
import time
import curses
import curses.wrapper
import ui.colors
import ui.dialogs


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

