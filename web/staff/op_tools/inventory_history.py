#!/usr/bin/env python3
# inventory_history.py
# Patrick McQuighan
# Does some basic reporting about a particular item id

import op_db_library as db
import cgi
import cgitb
cgitb.enable()

def print_headers():
    print('''Content-Type: text/html\n\n''')
    print('''<html><head>
    <title>Open Produce Item History</title>
    <style type="text/css">
    td,tr { line-height: 14px; height: 14px; border-bottom: 1px solid #bbb; border-left: 1px solid #bbb;}\n
    tr:nth-child(even) { background-color: #E0E0E0; };
    </style>
    </head>
    ''')

def main():
    print_headers()
    print('''<body>''')
    print('''<form name="item" action="inventory_history.py" method="get">''')
    print('''Input an item SKU:''')
    print('''<input type="text" name="itemid" size="4" /> <input type="submit" value="Display" />''')
    print('''</form>''')
    form = cgi.FieldStorage()
    if "itemid" in form:
        itemid = int(form.getvalue("itemid"))
        item = db.get_item(itemid)
        print('''<br /> <b>30 day history for item %d (%s) </b><br />''' % (itemid, item))
        total_sales,total_deliveries,total_slush,history = db.get_item_history(itemid,30)
        print('<b>Total sales: %d <br />' % (total_sales,))
        print('Total deliveries: %d <br />' % (total_deliveries,))
        print('Total slushfunded: %d <br /></b>' % (total_slush,))
        print('''<table><thead><th>Date</th><th>+/-</th><th>Type</th></thead>''')
        for ttp in history:
            print('''<tr><td>%s</td><td>%.2f</td><td>%s</td></tr>''' % ttp)
        print('''</table>''')
    print('''</body></html>''')

if __name__ == "__main__":
    main()
