#!/usr/bin/env python3
# item_search.py
# Patrick McQuighan
# Searches database for any matching item names and displays their name and gives a link to the item info page

import op_db_library as db
import cgi

def print_headers():
    print('Content-type: text/html\n')
    print('''<html>
<head><title>Item Search</title>
    <link rel="stylesheet" type="text/css" href="../../tools.css" />
</head>
<body>
''')

def main():
    print_headers()
    form = cgi.FieldStorage()
    if 'search' in form:
        search = form.getvalue('search')
    else:
        search = None

    print('''<form name="item_search" action="item_search.py" method="get">''')
    print('''Enter all or part of an item name to search for:''')
    if search == None:
        print('''<input type="text" id="search" name="search" />''')
    else:
        print('''<input type="text" id="search" name="search" value="%s" />''' % (search))
    print('''<input type="submit" value="Search" />''')
    print('''</form>''')

    if search != None:
        results = db.search_for_item(search)
        print('<table border="1"><thead><tr><th>SKU</th><th>Name</th><th>Price</th><th>Count</th><th>Active</th></tr></thead>')
        print('<tbody>')
        for item in results:
            itemid = item.get_id()
            price_str = item.get_price_str()
            count = item.get_count()  # current number in stock
            is_active = "Yes" if not item.get_is_discontinued() else "No"
            print('<tr><td>',itemid,'</td>')
            print('<td><a href="%s" target="_blank"> %s </a></td>' % (db.get_item_info_page_link(itemid), item))
            print('<td>', price_str, '</td>')
            print('<td style="text-align:right">', count, '</td>')
            print('<td style="text-align:right">', is_active, '</td>')
            print('</tr>')
        print('</tbody></table>')
    print('</body></html>')

if __name__ == "__main__":
    main()
