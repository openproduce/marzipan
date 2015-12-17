#!/usr/bin/env python
# get_distributor_item.py
# Returns a comma separated string containing Distributor item id, wholesale price, case size and case units for a given item/distributor pair

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

import cgi
import op_db_library as db

form = cgi.FieldStorage()
print 'Content-type: text/plain\n'

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
    print '%s,%d,%s,%.2f,%.2f,%s' % (dist.get_name(), dist.get_id(),dist_item.get_dist_item_id(), dist_item.get_wholesale_price(), dist_item.get_case_size(), dist_item.get_case_unit())

