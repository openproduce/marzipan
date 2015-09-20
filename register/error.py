#!/usr/bin/env python
import curses
import config

# TODO replace with something smarter
def report(s):
    curses.endwin()
    print "error: %s"%(s)
    sys.exit(2)
