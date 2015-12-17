#!/usr/local/bin/python
#
# Tab history since last zeroed.
#
# 10 Aug 2010

# This file is part of Marzipan, an open source point-of-sale system.
# Copyright (C) 2010 Open Produce LLC
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

import cgi
import cStringIO
import sys
import cgitb; cgitb.enable()

sys.path.insert(0, "/home/luitien/marzipan")
from tabutil import *

_session = get_session()

def name_or_id(x):
    """Given a string of either the customer's name or ID, return the integer ID (in a list).  If there's multiple matches, return a list of IDs.
    
    Uses SQL's LIKE operator for matching."""
    try:
        return [ int(x) ]
    except ValueError:
        L = _session.query(Customer).filter(Customer.name.like(x)).all()
        return [ c.id  for c in L ]

def html_tab_history(c_id):
    """HTML version of tabutil.show_tab_history."""
    ret = cStringIO.StringIO()
    tab_activity = _session.query(TabLog).filter_by(customer_id = c_id).all()
    idx = tab_last_zeroed(tab_activity)
    latest_run = tab_activity[(idx+1):]
    print >>ret, "<ul>"
    for tc in latest_run:
        print >>ret, "<li>%s" % format_tablog(tc)
        if tc.is_payment() is False:
            print >>ret, "<br>\n<table>"
            for si in tab_charged_items(tc):
                try:
                    si_item_name = si.item.name
                except AttributeError:
                    si_item_name = "<unknown item>"
                print >>ret, "<tr><td>$%5.2f</td><td>%s</td></tr>" % (si.total, si_item_name)
            print >>ret, "</table>"
        print >>ret, "</li>"
    print >>ret, "</ul>"
    return ret.getvalue()

def main():
    print """Content-Type: text/html\n\n"""
    form = cgi.FieldStorage()
    print """<html>
<head>
<title>Tab History</title>
</head>
<body>"""
    print """<form>
Customer name or ID:<br>
<input type="text" name="input">
</form><br><hr>"""
    input = form.getfirst("input")
    if input is not None:
        ids = name_or_id(input)
        n_found = len(ids)
        if n_found == 1:
            c_id = ids[0]
            print "Customer %d (%s)<br><br>" % (c_id, find_customer_by_id(c_id).name)
            print html_tab_history(c_id)
        elif n_found == 0:
            print """No customers found matching "%s"<br>""" % input
        elif n_found >= 2:
            print "Multiple names matched:<br>"
            print """<table>
<tr>
<th>ID</th>
<th>Name</th>
</tr>"""
            for id in ids:
                print """<tr>\n<td>%4d</td>\n<td>%s</td>\n</tr>""" % (id, find_customer_by_id(id).name)
            print "</table>"
    print """</body></html>"""
    return 0

if __name__ == '__main__':
    sys.exit(main())
