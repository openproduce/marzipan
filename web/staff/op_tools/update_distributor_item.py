#!/usr/bin/env python
# updates the distributors for a given item.
# is passed in an itemid, distributor name and an action which is either 'add' or 'remove'
# it prints out either 'Error: ....' or a comma separated string of the items updated distributors
# eg if and item had no distributors and you added Kehe, then this prints out 'Kehe'

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

action = form.getvalue('action')
if action == 'update_byid':    # temporary hack until things get sorted out with item_info (should only need this)
    if "dist_item_id" in form:
        dist_item = db.get_distributor_item_byid(int(form.getvalue('dist_item_id')))
        dist_item_id = dist_item.get_dist_item_id()
        wholesale_price = dist_item.get_wholesale_price()
        case_size = dist_item.get_case_size()
        case_unit_id = dist_item.get_case_unit_id()

        if 'distitemid' in form:
            dist_item_id = form.getvalue('distitemid')
        if 'caseprice' in form:
            wholesale_price = float(form.getvalue('caseprice'))
        if 'casesize' in form:
            case_size = float(form.getvalue('casesize'))
        if 'caseunit' in form:
            case_unit_id = int(form.getvalue('caseunit'))

        db.update_distributor_item(dist_item, dist_item_id, wholesale_price, case_size, case_unit_id)        
    else:
        raise Exception ('no distributor_item id given')
elif action == 'remove_byid':  # temporary hack until things get sorted out with item_info (should only need this)
    if "dist_item_id" in form:
        db.remove_distributor_item_byid(int(form.getvalue('dist_item_id')))
    else:
        raise Exception ('no distributor_item id given')
elif action == 'query-margin':  # temporary hack until things get sorted out with item_info (should only need this)
    if "dist_item_id" in form:
        dist_item = db.get_distributor_item_byid(int(form.getvalue('dist_item_id')))
        each_cost = dist_item.get_each_cost()
        item = db.get_item(dist_item.get_item_id())
        dist = db.get_distributor(dist_item.get_dist_id())
        margin = db.get_distributor_item_margin(item,dist,dist_item)
        print '%.2f, %d' % (each_cost, margin)
    else:
        raise Exception ('no distributor_item id given')
elif 'item' in form:
    itemid = int(form.getvalue('item'))
    if action == 'query':                       # get a list of all distributors for a given item
        item = db.get_item(itemid)
        print item.get_distributors_str()
    elif action == 'query-id':    # get a string of all distributor ids for a given item
        item = db.get_item(itemid)
        print item.get_distributor_ids_str()
    else:
        if 'distname' not in form and 'distid' not in form:
            raise Exception ('no distributor given')
        else:
            if 'distname' in form:
                distname = form.getvalue('distname')
                dist = db.get_distributor_byname(distname)
            if 'distid' in form:
                distid = int(form.getvalue('distid'))
                dist = db.get_distributor(distid)
            if dist == None: 
                raise Exception ('distributor not found in the database')
            else:
                item = db.get_item(itemid)        
                if action == 'add':                        # add a new distributor item with the given distributor and item
                    added = db.add_distributor_item(item,dist)
                    if 'item_info' in form:   # temporary hack until things get totally sorted out with 'item_info' (should only need this)
                        print added.get_id()
                    else:
                        print item.get_distributors_str()
                elif action == 'remove':                        # delete distributor item with given distributor name and item name
                    if not db.is_distributor_item(item,dist):
                        raise Exception ('%s is not currently a distributor for %s' % (dist, item))
                    else:
                        db.remove_distributor_item(item,dist)
                        print item.get_distributors_str()
                elif action == 'update':                              # update information (case size/units etc) for a distributor item
                    dist_item = db.get_distributor_item(item,dist)
                    dist_item_id = dist_item.get_dist_item_id()
                    wholesale_price = dist_item.get_wholesale_price()
                    case_size = dist_item.get_case_size()
                    case_unit_id = dist_item.get_case_unit_id()

                    if 'distitemid' in form:
                        dist_item_id = form.getvalue('distitemid')
                    if 'price' in form:
                        wholesale_price = float(form.getvalue('price'))
                    if 'casesize' in form:
                        case_size = float(form.getvalue('casesize'))
                    if 'caseunit' in form:
                        case_unit = form.getvalue('caseunit')            
                        case_unit_id = db.get_unit_byname(case_unit).get_id()

                    db.update_distributor_item(dist_item, dist_item_id, wholesale_price, case_size, case_unit_id)
else:
    raise Exception ('invalid action')
