#!/usr/bin/env python
# category_info.py
# Patrick McQuighan
# 2/10/2011
# This tool allows the user to see all items that are from a given category as well as general information
# about the category such as:
#   TBD
# We allow for categoryid as a form input so that we can link from the item_info page. 
#  do this with ids since unlike the names they won't contain ', ,etc so I don't have to worry about escaping category names
# in javascript and in python when generating the links.

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

import op_db_library as db
import cgi

def print_headers(catid=0,catname=''):
    print '''Content-Type: text/html\n\n'''
    if catid != 0:
        catname = db.get_category(catid).get_name()
    elif catname == '':
        catname = ''
    print '''<html><head>
    <title>Open Produce Category '%s' Info</title>''' % catname
    print '''    <style type="text/css">
    table thead { background-color:#ddd; color:#333; font-weight: bold; cursor: default; }\n
    tr:nth-child(even) { background-color: #E0E0E0; };
    </style>
    '''
    print '''</head><body>'''

def main():
    form = cgi.FieldStorage()

    if 'categoryid' in form:
        print_headers(int(form.getvalue('categoryid')))
    elif 'categoryname' in form:
        print_headers(catname=form.getvalue('categoryname'))
    else:
        print_headers()
    
    print '''<form name="category" action="category_info.py" method="get">'''
    print '''Input a category name'''
    print '''<input type="text" name="categoryname" size="4" /> <input type="submit" value="Display" />'''
    print '''</form>'''

    category = None

    if "categoryid" in form:   
        categoryid = int(form.getvalue("categoryid"))
        category = db.get_category(categoryid)
    elif "categoryname" in form:
        try:
            category = db.get_category_byname(form.getvalue("categoryname"))
        except Exception:
            print '''Error: category '%s' not found''' % form.getvalue("categoryname")
    
    if category != None:
        print '''<b>Info for category %s:</b><br />''' % category
        
        print '''<b>Items in this category </b><br/><table>
                   <thead>
                   <th>ItemID</th>
                   <th>Name</th>
                   </thead>'''
        for item in db.get_items(show_categories=[category.get_name()], hide_categoryless=True):
            print '''<tr><td><a href="%s">%d</a></td><td>%s</td></tr>''' % (db.get_item_info_page_link(item.get_id()),item.get_id(), item.get_name())
        print '''</table>'''

if __name__ == "__main__":
    main()

