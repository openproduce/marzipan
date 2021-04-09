#!/usr/bin/env python3
# autocount_items.py
# Patrick McQuighan
# This script should be run periodically when the store is not open to perform an auto-update of the last_count and last_count_timestamp
# fields of the database.  It loops over all items in the database and updates the last_count field with the current value of get_count
# This will improve performance of the catalog page (or any page displaying item counts)

import op_db_library as db

for item in db.get_items():
    newcount = item.get_count()
    item.auto_count(newcount)
