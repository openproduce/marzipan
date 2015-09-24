#!/usr/bin/env python
# item_search.py
# Patrick McQuighan
# Searches database for any matching item names and displays their name and gives a link to the item info page

import op_db_library as db
import cgi

def print_headers():
    print 'Content-type: text/html\n'
    print '''<html>
<head><title>Item Search</title>
    <link rel="stylesheet" type="text/css" href="../../tools.css" />
</head>
<body>
'''

def main():
    print_headers()
    form = cgi.FieldStorage()
    if 'search' in form:
        search = form.getvalue('search')
    else:
        search = None

    print '''<form name="item_search" action="item_search.py" method="get">'''
    print '''Enter all or part of an item name to search for:'''
    if search == None:
        print '''<input type="text" id="search" name="search" />'''
    else:
        print '''<input type="text" id="search" name="search" value="%s" />''' % (search)
    print '''<input type="submit" value="Search" />'''
    print '''</form>'''
        
    if search != None:
        results = db.search_for_item(search)
        print '<table><thead><tr><th>SKU</th><th>Name</th></tr></thead>'
        print '<tbody>'
        for item in results:
            itemid = item.get_id()
            print '<tr><td>',itemid,'</td>'
            print '<td><a href="%s" target="_blank"> %s </a></td>' % (db.get_item_info_page_link(itemid), item)
            print '</tr>'
        print '</tbody></table>'
    print '</body></html>'

if __name__ == "__main__":
    main()
