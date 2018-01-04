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
    if 'name' in form:
        distname = form.getvalue('name')
        if db.is_distributor_byname(distname):
            raise Exception ('distributor already exists')
        else:
            db.add_distributor(distname)
            dist = db.get_distributor_byname(distname)
            print '%d,%s' % (dist.get_id(),distname)
    else:
        raise Exception ('no distributor name given')
elif action == 'remove':
    distid = int(form.getvalue('id'))
    if not db.is_distributor(distid):
        raise Exception ('distributor not in database')
    else:
        dist = db.get_distributor(distid)
        print dist.get_name()
        db.remove_distributor(dist)
        
elif action == 'query':
    dist_list = [dist.get_name() for dist in db.get_distributors()]
    print ','.join(dist_list)
elif action == 'query-name':
    dist_list = [str(dist.get_id())+','+dist.get_name() for dist in db.get_distributors()]
    print '\n'.join(dist_list);
else:
    raise Exception ('invalid action')
