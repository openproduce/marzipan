#!/usr/bin/env python3

import cgi,sys
import op_db_library as db

def log_exception(*args):
    print('Error: %s' % (args[1],))

sys.excepthook = log_exception

form = cgi.FieldStorage()
print('Content-type: text/plain\n')
action = form.getvalue('action')
if action == 'add':
    if 'item_id' in form and 'cat_id' in form:
        itemid = int(form.getvalue('item_id'))
        item = db.get_item(itemid)
        catid = int(form.getvalue('cat_id'))
        cat = db.get_category(catid)
        if db.is_category_item(item,cat):
            raise Exception ('%s is already a category for %s' % (cat, item))
        else:
            db.add_category_item(item,cat)
            new_cat_item_id = db.get_category_item(item.get_id(),cat.get_id()).get_id()
            print('%d,%s,%s' % (new_cat_item_id, db.get_category_info_page_link(catid),cat))
    else:
        raise Exception ('need item_id and cat_id, given: %s ' % form.keys())
elif action == 'remove':
    if 'cat_item_id' in form:
        catitemid = int(form.getvalue('cat_item_id'))
        db.remove_category_item_byid(catitemid)
    elif 'item_id' in form and 'cat_id' in form:
        itemid = int(form.getvalue('item_id'))
        item = db.get_item(itemid)
        catid = int(form.getvalue('cat_id'))
        cat = db.get_category(catid)
        db.remove_category_item(item,cat)
    else:
        raise Exception ('no cat_item_id given')
elif action != None:
    itemid = int(form.getvalue('item'))
    if action == 'query':                       # get a list of all category for a given item
        item = db.get_item(itemid)
        print(item.get_categories_str())
    elif 'catid' in form or 'catname' in form:
        if 'catid' in form:
            catid = int(form.getvalue('catid'))
            cat = db.get_category(catid)
        else:
            catname = form.getvalue('catname')
            cat = db.get_category_byname(catname)
        item = db.get_item(itemid)
        if action == 'remove_item_cat':                        # delete category item
            if not db.is_category_item(item,cat):
                raise Exception ('%s is not currently a category for %s' % (cat, item))
            else:
                db.remove_category_item(item,cat)
                print(item.get_distributors_str())
    else:
        raise Exception ('need a catid or catname')
else:
    raise Exception ('invalid action')
