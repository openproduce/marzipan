#!/usr/bin/env python
# Patrick McQuighan
# inventory_stats.py 
# This page provides stats on the inventory such as "top 10 slowest-selling items" etc

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
