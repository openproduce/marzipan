#!/usr/bin/env python
# catalog.py
# Patrick McQuighan
# An update script that takes distributor item ids from Kehe items and appends them to the item's notes section.
# then it takes item barcodes and copies that into the distributor item id.

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

kehe = db.get_distributor_byname('Kehe')
kehe_items = db.get_distributor_items(show_distributors=[kehe])
for p,item,d,dist_item in kehe_items:  # p and d are unused
    if d.name != 'Kehe':
	    continue
    note = item.get_notes()
    d_id = dist_item.get_dist_item_id()
    note += '\nold kehe id:' + str(d_id)
    item.set_notes(note)

    barcodes = item.get_barcodes()
    if len(barcodes) == 0 :
        dist_item.set_dist_item_id('')
    if len(barcodes) == 1:
        dist_item.set_dist_item_id(barcodes[0])
    else:
        print 'Item %s has more than 1 barcode --> ambiguity, no action taken.' % (item)
    
    
