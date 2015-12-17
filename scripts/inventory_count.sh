#!/bin/bash

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

echo -n "Happy new month!  As of `date` here is the wholesale value of inventory: "

echo 'select sum( if(i.count>0,  i.count*(di.wholesale_price/di.case_size),0)) from items as i, distributor_items as di where di.item_id = i.id limit 30;' | mysql -u root inventory

echo;

echo -n "Beer: "

echo 'select sum( if(i.count>0,  i.count*(di.wholesale_price/di.case_size),0)) from items as i, distributor_items as di, categories as c, category_items as ci where di.item_id = i.id and ci.cat_id = c.id and ci.item_id = i.id and (c.name = "beer");' | mysql -u root inventory

echo;

echo -n "Wine: "

echo 'select sum( if(i.count>0,  i.count*(di.wholesale_price/di.case_size),0)) from items as i, distributor_items as di, categories as c, category_items as ci where di.item_id = i.id and ci.cat_id = c.id and ci.item_id = i.id and (c.name = "wine");' | mysql -u root inventory

echo;

echo -n "And the retail value is: "

echo 'select sum( if(i.count>0,  i.count*p.unit_cost,0)) from items as i, prices as p where i.price_id = p.id limit 30;' | mysql -u root inventory

echo;

echo -n "Tab balances: "

echo 'select sum(balance) from customers where id <> 151;' | mysql -u root register_tape
