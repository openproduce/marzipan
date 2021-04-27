#!/usr/bin/env python3
# get_distributor_item.py
# Returns a comma separated string containing Distributor item id, wholesale price, case size and case units for a given item/distributor pair

import cgi
import op_db_library as db

form = cgi.FieldStorage()
print('Content-type: text/plain\n')

itemid = int(form.getvalue('item'))
item = db.get_item(itemid)
dist = None
if 'distname' in form:
    distname = form.getvalue('distname')
    if db.is_distributor_byname(distname):
        dist = db.get_distributor_byname(distname)
elif 'distid' in form:
    distid = int(form.getvalue('distid'))
    if db.is_distributor(distid):
        dist = db.get_distributor(distid)

if dist != None:
    dist_item = db.get_distributor_item(item,dist)
    print('%s,%d,%s,%.2f,%.2f,%s' % (dist.get_name(), dist.get_id(),dist_item.get_dist_item_id(), dist_item.get_wholesale_price(), dist_item.get_case_size(), dist_item.get_case_unit()))
