#!/usr/bin/env python
# update_barcode_item.py
# Starting using exceptions so that any error will be caught.  Eg
# if there is some undetected error in the database, the user will
# be alerted, although probably in a way that is not meaningful for them
# but at least the bug is displayed

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

import cgi,sys
import op_db_library as db

def log_exception(*args):
    print 'Error: %s' % (args[1],)

sys.excepthook = log_exception

print 'Content-Type: text/plain\n'
form = cgi.FieldStorage()
action = form.getvalue("action")
if action == 'add':
    if 'item_id' in form and 'barcode' in form:
        itemid = int(form.getvalue("item_id"))
        item = db.get_item(itemid)
        barcode = form.getvalue("barcode")
        db.add_barcode_item(itemid, barcode)
        new_bcitem = db.get_barcode_item(item, barcode)
        print new_bcitem.get_id()
    else:
        raise Exception ('missing either item_id or barcode. given:%s' % (form.keys()))
elif action == 'remove':
    if 'bc_item_id' in form:
        db.remove_barcode_item_byid(int(form.getvalue("bc_item_id")))
    else:
        raise Exception ('bc_item_id not given')
else:
    raise Exception('invalid action')



