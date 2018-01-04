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

import cgi, sys
import op_db_library as db

def log_exception(*args):
    print 'Error: %s' % (args[1],)

sys.excepthook = log_exception

form = cgi.FieldStorage()
print 'Content-type: text/plain\n'
action = form.getvalue('action')
if action == 'add':
    if 'cat' in form:
        catname = form.getvalue('cat').strip()
        if db.is_category_byname(catname):
            raise Exception('category already exists')
        else:
            db.add_category(catname)
            cat = db.get_category_byname(catname)
            print '%d,%s' % (cat.get_id(), cat.get_name())
    else:
        raise Exception('no name given to add')
elif action == 'remove':
    catid = form.getvalue('catid')
    if not db.is_category(catid):
        raise Exception ('category not in database')
    else:
        cat = db.get_category(catid)
        db.remove_category(cat)
        print ''
elif action == 'query':
    cat_list = [cat.get_name() for cat in db.get_categories()]
    print ','.join(cat_list)
elif action == 'query-name':
    cat_list = [str(cat.get_id())+','+cat.get_name() for cat in db.get_categories()]
    print '\n'.join(cat_list)
elif action == 'query-cat-id':
    if 'catname' in form:
        catname = form.getvalue('catname').strip()
        cat = db.get_category_byname(catname)
        print '%d,%s' % (cat.get_id(), cat.get_name())
else:
    raise Exception ('invalid action')
    
