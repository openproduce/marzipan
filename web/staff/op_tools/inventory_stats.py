#!/usr/bin/env python
# Patrick McQuighan
# inventory_stats.py 
# This page provides stats on the inventory such as "top 10 slowest-selling items" etc

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

import op_db_library as db
import cgi

def print_headers():
    print '''Content-Type: text/html\n\n'''
    print '''<html><head>
    <title>Open Produce Inventory Stats</title>
    </head>
    <body>'''

print_headers()
print '''<h3>Top 10 items with most sales in the last 30 days</h3>'''
print '''<table>
         <th>Rank</th>
         <th>OP Item ID</th>
         <th>Item name</th>
         <th>Sales</th>
      '''
for i,(itemid,sales) in enumerate(db.most_sold_items(10,30)):
    item = db.get_item(itemid)
    print '''<tr><td>%d</td><td>%d</td><td>%s</td><td>%d</td></tr>''' % (i+1,itemid,item,sales)
print '''</table>'''

print '''<h3>Top 10 items with most sales in $ (not inc. tax) in the last 30 days </h3>'''
print '''<table>
         <th>Rank</th>
         <th>OP Item ID</th>
         <th>Item name</th>
         <th>Sales</th>
      '''
for i,(itemid,sales) in enumerate(db.most_dollar_items(10,30)):
    item = db.get_item(itemid)
    print '''<tr><td>%d</td><td>%d</td><td>%s</td><td>$%.2f</td></tr>''' % (i+1,itemid,item,sales)
print '''</table>'''

print '''</body></html>'''
