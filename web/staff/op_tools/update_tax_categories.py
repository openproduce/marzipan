#!/usr/bin/env python

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

