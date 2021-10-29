#!/usr/bin/env python3
# add_items.py
# Patrick McQuighan
# quick thing enabling adding items to the database

import op_db_library as db
import cgi

import cgitb
cgitb.enable()

print('''Content-Type: text/html\n\n''')
print('''<html><head>
    <title>Open Produce Add Items Page</title>
    <style type="text/css">
    * { font-size: 12px; }\n
    </style>
    </head>
    <body>''')
form = cgi.FieldStorage()
if "name" in form  and "taxcat" in form and ("price" in form and "price_unit" in form or "price_id" in form) and "count" in form and "itemsize" in form and "size_unit" in form:
    name = form.getvalue('name')
    taxcatname = form.getvalue('taxcat').split(' ')[0]  # string representation of taxcat includes a (%.2f%%)
    not_valid = False
    if "price_id" not in form:
        price = float(form.getvalue('price'))
        price_unit = form.getvalue('price_unit')
    else:
        p_id = int(form.getvalue('price_id'))
        if not db.is_price(p_id):
            not_valid = True
        else:
            price = p_id
            price_unit = None

    if not_valid:
        print('<br /> Invalid price_id')
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
                print('<br />Included distributor info')
            else:
                print('<br />No valid distributor name entered, distributor info ignored')

        print('<br />Successfully added "%s" as item id %d' % (name, itemid))
else:
    print('''<p>Not all required fields were filled out </p>''')


print('''<form name="newitem" action="add_items.py" method="get">''')
print('''item name*: <input type="text" name="name" />''')
print('''item size*: <input type="text" name="itemsize" size="5" /> size unit*: <select name="size_unit">''')
for unit in db.get_units():
    print('''<option> %s </option> ''' % unit)
print('''</select>''')
print('''barcode: <input type="text" name="barcode" size="10" />''')
print('''PLU : <input type="text" name="plu" size="10" />''')
print('''count*: <input type="text" name="count" size="3" /> <br />''')
print('''price: $<input type="text" name="price" size="5"/>''')
print('''price unit: <select name="price_unit">''')
for unit in db.get_units():
    print('''<option> %s </option> ''' % unit)
print('''</select>''')
print('''price id: <input type="text" name="price_id" size="4" />''')
print('''tax category*: <select name="taxcat">''')
for taxcat in db.get_tax_categories():
    print('''<option> %s </option> ''' % taxcat)
print('''</select> <br />''')

print('''distributor: <select name="distributor" /> ''')
print('''<option></option>''')
for dist in db.get_distributors():
    print('''<option> %s </option> ''' % dist)
print('''</select>''')
print('''distributor item id: <input type="text" name="dist_item_id" size=10" /> ''')
print('''case price: <input type="text" name="wholesale_price" size="5" /> ''')
print('''case size: <input type="text" name="case_size" size=5" /> ''')
print('''case unit: <select name="case_unit"> ''')
for unit in db.get_units():
    print('''<option> %s </option> ''' % unit)
print('''</select> <br />''')

print(''' <input type="submit" value="Add Item" /> </form>''')
print('''Starred fields are required <br />''')
print('''Input either a price AND a price unit OR a price id''')
print('''</body></html>''')
