#!/usr/bin/env python

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
    
