#!/bin/bash

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
