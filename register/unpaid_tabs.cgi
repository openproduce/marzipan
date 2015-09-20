#!/usr/local/bin/python
#
# Unpaid tabs
#
# 10 Aug 2010

import cgi
import cStringIO
import sys
import cgitb; cgitb.enable()

sys.path.insert(0, "/home/luitien/marzipan")
from tabutil import *

_session = get_session()

this_script = sys.argv[0]

print "Content-Type: text/html"
print
print """<html>
<head>
<title>Unpaid Tabs</title>
</head>
<body>"""

print """<form>
Show tabs that:<br>
have not been updated in at least
<input type="text" name="staleness"> (default 30) days<br>
and owe at least
<input type="text" name="min_balance"> (default 3) dollars<br>
</form>"""

print """<table border=1>
<tr>
<th><a href="%s?sortby=date">Last Change</a></th>
<th><a href="%s?sortby=balance">Balance</a></th>
<th><a href="%s?sortby=customer">Name</a></th>
</tr>""" % (this_script, this_script, this_script)

form = cgi.FieldStorage()
n_days = form.getfirst("staleness") or 30    # days
staleness = datetime.timedelta(int(n_days))
min_balance = form.getfirst("min_balance") or 3 # dollars
c_ids = [ c.id  for c in _session.query(Customer).all() ]
L = list( find_unpaid_tabs(c_ids, staleness = staleness, threshold = int(min_balance)) )
sortby = form.getfirst("sortby")
if sortby == "date":
    # using 1 Jan 2008 as ``before everything else''
    L.sort( reverse=True, key = lambda (c,t): t or datetime.datetime(2008,1,1) )
elif sortby == "balance":
    L.sort( reverse=True, key = lambda (c,t): c.balance )
elif sortby == "customer":
    L.sort( key = lambda (c,t): c.name )

for (c,t) in L:
    print "<tr>"
    print """<td>%s</td>""" % t
    print """<td>$%6.2f</td>""" % c.balance
    print """<td><a href="tab-history.cgi?input=%d">%s</a></td>""" % (c.id, c.name)
    print "</tr>"

print "</table>"
print "</body></html>"
