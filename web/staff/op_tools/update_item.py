#!/usr/bin/env python3
# Patrick McQuighan
# update_item_count.py
# this is a simple cgi interface that takes in an item id and a number and increases
#  the item's count by that amount
# did it this way so that javascript can just post to this file which then calls the appropriate function

import cgi,sys
import op_db_library as db
import datetime
def log_exception(*args):
    print('Error: %s' % (args[1],))

sys.excepthook = log_exception

form = cgi.FieldStorage()
print('Content-type: text/plain\n')

action = form.getvalue("action")
if action == "count":
    if "id" in form and "count" in form:
        item = db.get_item(int(form.getvalue("id")))
        item.set_count(int(form.getvalue("count")))
        if "exp_date" in form:
            speculate_date = datetime.datetime.strptime(form.getvalue("exp_date"), "%A %m/%d/%y")
            days_to_speculate = (speculate_date - datetime.datetime.now()).days
            count = item.get_count()
            day14 = db.get_sales_in_range(int(form.getvalue("id")), 14)
            speculated = count - day14/14*days_to_speculate   # days_to_speculate determined outside of loop
            print('%d,%d' % (speculated, count))
        else:
            print(item.get_count())
elif action == "status":
    if "id" in form and "stocked" in form:
        item = db.get_item(int(form.getvalue("id")))
        if form.getvalue("stocked") == 'true':
            db.set_item_discontinued(item, 0)
        else:
            db.set_item_discontinued(item, 1)
elif action == "delivery":
    if "id" in form and "amt" in form and "dist" in form:
        itemid = int(form.getvalue("id"))
        db.add_delivery(itemid, int(form.getvalue("amt")), form.getvalue("dist"))
        item = db.get_item(itemid)
        print("%d" % item.get_count())
    else:
        raise Exception('invalid arguments')
elif action == "name":
    if "id" in form and "name" in form:
        itemid = int(form.getvalue("id"))
        item = db.get_item(itemid)
        db.set_item_name(item, form.getvalue("name"))
    else:
        raise Exception ('incorrect arguments. need id and name.  given %s' % (form.keys()))
elif action == "display_name":
    if "id" in form and "display_name" in form:
        itemid = int(form.getvalue("id"))
        item = db.get_item(itemid)
        db.set_item_display_name(item, form.getvalue("display_name"))
    else:
        raise Exception ('incorrect arguments. need id and name.  given %s' % (form.keys()))
elif action == "description":
    if "id" in form and "description" in form:
        itemid = int(form.getvalue("id"))
        item = db.get_item(itemid)
        db.set_item_description(item, form.getvalue("description"))
    else:
        raise Exception ('incorrect arguments. need id and description.  given %s' % (form.keys()))
elif action == "weight":
    if "id" in form and "weight" in form:
        itemid = int(form.getvalue("id"))
        item = db.get_item(itemid)
        db.set_item_weight(item, form.getvalue("weight"))
    else:
        raise Exception ('incorrect arguments. need id and weight.  given %s' % (form.keys()))
elif action == "barcode_byid":  # hack to get around barcode
    if "barcode_id" in form and "new_barcode" in form:
        bc_id = int(form.getvalue("barcode_id"))
        db.set_barcode_item_byid(bc_id, form.getvalue("new_barcode"))
    else:
        raise Exception ('incorrect arguments. need barcode_id and new_barcode. given %s' % (form.keys()))
elif action == "barcode":
    if "id" in form and "newbarcode" in form and "oldbarcode" in form:
        itemid = int(form.getvalue("id"))
        if form.getvalue("oldbarcode") != 'None':
            item = db.get_item(itemid)
            db.set_item_barcode(item, form.getvalue("oldbarcode"),form.getvalue("newbarcode"))
        else:
            db.add_barcode_item(itemid,form.getvalue("newbarcode"))
    else:
        raise Exception ('incorrect arguments. need id, newbarcode, and  oldbarcode. given %s' % (form.keys()))
elif action == "size":
    if "id" in form and "size" in form:
        itemid = int(form.getvalue("id"))
        size = float(form.getvalue("size"))
        item = db.get_item(itemid)
        db.set_item_size(item, size)
    else:
        raise Exception ('incorrect arguments. need id, size. given %s' % (form.keys()))
elif action == "sizeunit":
    if "id" in form and "sizeunit" in form:
        size_unit = form.getvalue("sizeunit").strip()
        s_u = db.get_unit_byname(size_unit).get_id()
        item = db.get_item(int(form.getvalue("id")))
        db.set_item_size_unit(item, s_u)
elif action == "saleunit":
    if "id" in form and "saleunit" in form:
        sale_unit = form.getvalue("saleunit")
        item = db.get_item(int(form.getvalue("id")))
        db.set_price_sale_unit_id(db.get_price(item.price_id), int(sale_unit))
    else:
        raise Exception ('incorrect arguments. need id, sizeunit. given %s' % (form.keys()))
elif action == "sizeunit_byid":
    if "id" in form and "sizeunit" in form:
        item = db.get_item(int(form.getvalue("id")))
        db.set_item_size_unit(item,int(form.getvalue("sizeunit")))
    else:
        raise Exception ('incorrect arguments. need id, sizeunit. given %s' % (form.keys()))
elif action == "add":
    if "name" in form  and "taxcat" in form and ("price" in form and "price_unit" in form or "price_id" in form) and "count" in form and "itemsize" in form and "size_unit" in form and "distributor" in form:
        name = form.getvalue('name')
        taxcatname = form.getvalue('taxcat').split(' ')[0]  # string representation of taxcat includes a (%.2f%%)
        not_valid = False
        p_id = int(form.getvalue('price_id'))
        if p_id == 0:
            price = float(form.getvalue('price'))
            price_unit = form.getvalue('price_unit')
        else:
            if not db.is_price(p_id):
                not_valid = True
            else:
                price = p_id
                price_unit = None

        if not_valid:
            print('Error: invalid price')
        else:
            count = int(form.getvalue('count'))
            plu = None
            itemsize = float(form.getvalue('itemsize'))
            sizeunit = form.getvalue('size_unit')
            if 'plu' in form:
                plu = form.getvalue('plu')
            itemid = db.add_item(name,itemsize, sizeunit, plu, count, price, taxcatname,price_unit)
            if 'barcode' in form:
                db.add_barcode_item(itemid, form.getvalue('barcode'))

            if 'distributor' in form:
                distname = form.getvalue('distributor')
                if db.is_distributor_byname(distname):
                    item = db.get_item(itemid)
                    dist = db.get_distributor_byname(distname)
                    db.add_distributor_item(item, dist)
                    d_i = db.get_distributor_item(item, dist)

                    ditemid = 0
                    wholesale_price = 0
                    case_size = 0
                    case_unit = 'each'
                    if 'dist_item_id' in form:
                        ditemid = form.getvalue('dist_item_id')
                    if 'wholesale_price' in form:
                        wholesale_price = float(form.getvalue('wholesale_price'))
                    if 'case_size' in form:
                        case_size = float(form.getvalue('case_size'))
                    if 'case_unit' in form:
                        case_unit = form.getvalue('case_unit')
                        case_unitid = db.get_unit_byname(case_unit).get_id()
                    db.update_distributor_item(d_i,ditemid, wholesale_price, case_size, case_unitid)
                item = db.get_item(itemid)
                each_cost = d_i.get_each_cost()
                op_price = item.get_price()
                tax = item.get_tax_value()
                if (op_price -tax) != 0:
                    margin = (1.0 - each_cost/(op_price - tax)) * 100
                else:
                    margin = 100
                item_price = db.get_price(item.get_price_id())
                cost = item_price.get_unit_cost()
                if 'categories' in form:
                    cat_ids_list = form.getvalue('categories')
                    cat_ids = filter(lambda x: x.isdigit(), cat_ids_list.split(','))  # only get valid digits
                    for c_id in cat_ids:
                        cat = db.get_category(c_id)
                        db.add_category_item(item, cat)
                print('%d,%d,%d,%.2f,%.2f,%.2f,%d,%.2f,%s,%s' % (itemid,item.get_price_id(), dist.get_id(), d_i.get_wholesale_price(),d_i.get_case_size(),each_cost,margin,cost,db.get_unit(item_price.get_sale_unit_id()), db.get_item_info_page_link(itemid)))

    else:
        raise Exception ('incorrect arguments. given %s' % (form.keys()))
elif action == 'get-string':
    if 'id' in form:
        item = db.get_item(int(form.getvalue("id")))
        print(item)
    else:
        raise Exception ('incorrect arguments. need id. given %s' % (form.keys()))
elif action == 'get-margin':
    if 'item_id' in form and 'dist_id' in form:
        item = db.get_item(int(form.getvalue("item_id")))
        distributor = db.get_distributor(int(form.getvalue("dist_id")))
        margin = db.get_distributor_item_margin(item, distributor)
        print(margin)
    else:
        raise Exception ('invlaid arguments. need item_id, distid. given %s' % (form.keys()))
elif action == 'update-notes':
    if 'item_id' in form and 'notes' in form:
        item = db.get_item(int(form.getvalue("item_id")))
        item.set_notes(form.getvalue('notes'))
    else:
        raise Exception ('invalid arguments. need item_id, notes. given %s' % (form.keys()))
else:
    raise Exception ('invalid action')
