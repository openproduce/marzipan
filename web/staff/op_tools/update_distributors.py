#!/usr/bin/env python3

import cgi, sys
import op_db_library as db

def log_exception(*args):
    print('Error: %s' % (args[1],))

sys.excepthook = log_exception

form = cgi.FieldStorage()
print('Content-type: text/plain\n')
action = form.getvalue('action')
if action == 'add':
    if 'name' in form:
        distname = form.getvalue('name')
        if db.is_distributor_byname(distname):
            raise Exception ('distributor already exists')
        else:
            db.add_distributor(distname)
            dist = db.get_distributor_byname(distname)
            print('%d,%s' % (dist.get_id(),distname))
    else:
        raise Exception ('no distributor name given')
elif action == 'remove':
    distid = int(form.getvalue('id'))
    if not db.is_distributor(distid):
        raise Exception ('distributor not in database')
    else:
        dist = db.get_distributor(distid)
        print(dist.get_name())
        db.remove_distributor(dist)

elif action == 'query':
    dist_list = [dist.get_name() for dist in db.get_distributors()]
    print(','.join(dist_list))
elif action == 'query-name':
    dist_list = [str(dist.get_id())+','+dist.get_name() for dist in db.get_distributors()]
    print('\n'.join(dist_list));
else:
    raise Exception ('invalid action')
