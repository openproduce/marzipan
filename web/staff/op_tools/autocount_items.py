#!/usr/bin/env python
# autocount_items.py
# Patrick McQuighan
# This script should be run periodically when the store is not open to perform an auto-update of the last_count and last_count_timestamp
# fields of the database.  It loops over all items in the database and updates the last_count field with the current value of get_count
# This will improve performance of the catalog page (or any page displaying item counts)

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

for item in db.get_items():
    newcount = item.get_count()
    item.auto_count(newcount)
