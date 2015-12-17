#!/usr/bin/env python
# Patrick McQuighan
# update_prices.py
# last mod: 1/28/2011

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

form = cgi.FieldStorage()
print 'Content-type: text/plain\n'

action = form.getvalue("action")
if action == 'price':
    if "price_id" in form and "price" in form:
        price = db.get_price(int(form.getvalue("price_id")))
        db.set_price(price, float(form.getvalue("price")))
    else:
        raise Exception ('invalid arguments. need price_id and price.  given %s' % form.keys())
elif action == 'group':
    if "price_id" in form and "item_id" in form:
        newid = form.getvalue('price_id')
        itemid = form.getvalue('item_id')
        if newid.isdigit() and itemid.isdigit():
            newid = int(newid)
            itemid = int(itemid)
            if db.is_price(newid):
                item = db.get_item(itemid)
                old = item.get_price_id()
                db.set_item_price(item,newid)
                price = db.get_price(newid)
                sale_unit = db.get_unit(price.get_sale_unit_id())
                print '%d,%d,%.2f,%d,%s' % (old,db.price_item_count(old),price.get_unit_cost(), price.get_id(),sale_unit) 
            else:
                raise Exception ('price_id %d not currently in database' % (newid))
        else:
            raise Exception ('invalid price_id or item_id')
    else:
        raise Exception ('invalid arguments. need price_id and item_id. given %s' % (form.keys()))
elif action == 'query':
    # returns a string containing information about all (item,distributor) pairs with the given price_id
    # prints the string as info about one item per line (separated with '\n')
    # prints out the following for each item: "id,dist_id,each_cost,margin"
    if "price_id" in form:
        price_id = int(form.getvalue("price_id"))
        for item,dist in db.get_items_by_price(price_id):
            dist_item = db.get_distributor_item(item, dist)

            each_cost = dist_item.get_each_cost()
            op_price = item.get_price()
            tax = item.get_tax_value()
            if op_price - tax > 0:
                margin = (1.0 - each_cost/(op_price - tax)) * 100
            else:
                margin = 100
            real_profit = op_price - each_cost - tax
            print '%d,%d,%.2f,%.0f' % (item.get_id(), dist.get_id(), each_cost, margin)
    else:
        raise Exception ('invalid arguments. given %s' % (form.keys()))
elif action == 'split':
    if "item_id" in form:
        itemid = form.getvalue("item_id")
        if itemid.isdigit():
            itemid = int(itemid)
            item = db.get_item(itemid)
            old = item.get_price_id()
            oldprice = db.get_price(old)
            newprice = db.add_new_price(oldprice)
            db.set_item_price(item,newprice.get_id())
            sale_unit = db.get_unit(newprice.get_sale_unit_id())
            print '%d,%d,%.2f,%d,%s' % (old,db.price_item_count(old),newprice.get_unit_cost(), newprice.get_id(),sale_unit) 
        else:
            raise Exception ('invalid item_id')
    else:
        raise Exception ('invalid arguments. given %s' % (form.keys()))
elif action == 'item_price':
    if 'item_id' in form and 'price' in form:
        itemid = form.getvalue('item_id')
        if itemid.isdigit():
            item = db.get_item(int(itemid))
            price_items = db.get_items_with_price_id(item.get_price_id())
            if 'confirmed' in form or len(price_items) == 1:
                price = db.get_price(item.get_price_id())
                db.set_price(price, float(form.getvalue("price")))
            else:
                print 'Warning: changing this price will affect the following items:'
                for i in price_items:
                    print '%s. SKU %d' % (i, i.get_id())
        else:
            raise Exception('invalid item_id')
    else:
        raise Exception ('invalid arguments. given %s' % (form.keys()))
elif action == 'sale_unit':
    if "price_id" in form and "unit_name":
        priceid = form.getvalue("price_id")
        price = db.get_price(int(priceid))
        unitname = form.getvalue("unit_name").strip()
        unitid = db.get_unit_byname(unitname).get_id()
        db.set_price_sale_unit_id(price,unitid)
    else:
        raise Exception ('invalid arguments. given %s' % (form.keys()))
else:
    raise Exception ('invalid action')
