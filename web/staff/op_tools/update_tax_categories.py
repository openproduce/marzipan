#!/usr/bin/env python

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
if action == 'add':
    if 'taxcatname' in form and 'rate' in form:
        taxcatname = form.getvalue('taxcatname')
        rate = float(form.getvalue('rate')) / 100.0
        if db.is_tax_category_byname(taxcatname):
            raise Exception ('tax category already exits')
        else:
            db.add_tax_category(taxcatname, rate)
            taxcat = db.get_tax_category_byname(taxcatname)
            print '%d,%s' % (taxcat.get_id(),taxcatname)
    else:
                raise Exception ('invalid arguments. given %s' % (form.keys()))
elif action == 'remove':
    taxcatid = int(form.getvalue('taxcatid'))
    if not db.is_tax_category(taxcatid):
        raise Exception ('tax category not in database')
    else:
        taxcat = db.get_tax_category(taxcatid)
        db.remove_tax_category(taxcat)
        print ''
elif action == 'update':
    taxcatid = int(form.getvalue('taxcatid'))
    rate = float(form.getvalue('rate'))/ 100.0
    if not db.is_tax_category(taxcatid):
        raise Exception ('tax category not in database')
    else:
        taxcat = db.get_tax_category(taxcatid)
        db.update_tax_category(taxcat, rate)
        print '%s' % str(taxcat)
elif action == 'query':
    taxcat_list = [str(taxcat.get_id()) +','+str(taxcat) for taxcat in db.get_tax_categories()]
    print ';'.join(taxcat_list)
elif action == 'query-item':
    itemid = int(form.getvalue('item_id'))
    item = db.get_item(itemid)
    print item.get_tax_category()
elif action == 'set-item':
    itemid = int(form.getvalue('item_id'))
    taxcatid = int(form.getvalue('taxcatid'))

    item = db.get_item(itemid)
    taxcat = db.get_tax_category(taxcatid)
    db.update_item_tax_category(item, taxcat)

