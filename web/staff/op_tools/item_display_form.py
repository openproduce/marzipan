# item_display_form.py
# Patrick McQuighan
#
# This is meant to encapsulate making the form options so that multiple tools can reuse the same form stuff.
# It allows the other file to set which options it wants displayed (hide/show discontinued, hide/show categories, hide/show distributors), and returns a dictionary which can get passed to get_items()
# To use: a module must first call idf.init(...)
#  Then in the headers must call idf.print_javascript()
#  Then, print out the <form > tag then idf.print_form() then <input button=submit> </form>
#  Done this way so that the form can have other stuff that is unique to the other page instead of having everything in here

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

def init(form, discontinued=False, categories=False, distributors=False):
    global input_form, discontinued_option, categories_option, distributors_option
    input_form = form
    discontinued_option = discontinued
    categories_option = categories
    distributors_option = distributors

def print_javascript():
    if categories_option:
        print '''
         <script type="text/javascript">
         function allCategories(allbox){
            checked = allbox.checked;
            $('.categorybox').each(function(){
                this.checked = allbox.checked;
              });
         }
         </script>
         '''
    if distributors_option:
        print '''
         <script type="text/javascript">
         function allDistributors(allbox){
            checked = allbox.checked;
            $('.distributorbox').each(function(){
                this.checked = allbox.checked;
              });
         }
         </script>
         '''

def print_categories():
    print '''<br /> Select Categories to display:'''
    if "allCats" in input_form:
        print '''<input name="allCats" type="checkbox" onClick="allCategories(this)" value="True" checked>All </input> <br />'''
    else:
        print '''<input name="allCats" type="checkbox" onClick="allCategories(this)" value="True">All </input> <br />'''
    print'''
<table cellspacing=0 cellpadding=2 style="border-top: 1px solid #999; border-left: 1px solid #999;">'''
    hide_categories = []   # switching to displaying categories
#    hide_categories = db.get_categories()
    for i,cat in enumerate(db.get_categories()):
        if i % 5 == 0:
            if i> 0:
                print '''</tr>'''
            print '''<tr>'''

        test_str = "cat_%s" % str(cat)
        if test_str in input_form:
            print '''<td>%s</td><td style="border-right: 1px solid #999"><input class="categorybox" type="checkbox" name="cat_%s" value="True" checked/></td>''' % (cat,cat)
            hide_categories.append(cat)
        else:
            print '''<td>%s</td><td style="border-right: 1px solid #999"><input  class="categorybox" type="checkbox" name="cat_%s" value="True" /></td>''' % (cat, cat)
    if (i+1) % 5 == 0:
        print '''</tr><tr>'''
    if "cat_No Category" in input_form:
        print '''<td>%s</td> <td style="border-right: 1px solid #999"><input class="categorybox" type="checkbox" name="cat_%s" value="True" checked/></td>''' % ("No Category", "No Category")
        hide_categoryless = False
    else:
        print '''<td>%s</td> <td style="border-right: 1px solid #999"><input class="categorybox"  type="checkbox" name="cat_%s" value="True"/></td>''' % ("No Category", "No Category")
        hide_categoryless = True

    print '''</tr></table>'''
    return hide_categories,hide_categoryless

def print_distributors():
    print '''<br/><br/>Select distributors to display:'''
    if "allDists" in input_form:
        print '''<input name="allDists" type="checkbox" onClick="allDistributors(this)" value="True" checked>All </input><br/>'''
    else:
        print '''<input name="allDists" type="checkbox" onClick="allDistributors(this)" value="True">All </input><br/>'''
    dists = []

    print '''<table cellspacing=0 cellpadding=2 style="border-top: 1px solid #999; border-left: 1px solid #999;">'''
    
    for i,dist in enumerate(db.get_distributors()):
        if i % 5 == 0:
            if i> 0:
                print '''</tr>'''
            print '''<tr>'''
        test_str = "dist_%s" % str(dist)
        if test_str in input_form:
            dists.append(dist)
            print '''<td>%s</td> <td style="border-right: 1px solid #999"><input class="distributorbox" type="checkbox" name="dist_%s" value="True" checked/></td>''' % (dist,dist)
        else:
            print '''<td>%s</td><td  style="border-right: 1px solid #999"> <input class="distributorbox" type="checkbox" name="dist_%s" value="True"/> </td>''' % (dist,dist)

    if (i+1) % 5 == 0:
        print '''</tr><tr>'''
    test_str = "dist_No Distributor"
    if test_str in input_form:
        print '''<td>%s</td> <td style="border-right: 1px solid #999"><input class="distributorbox" type="checkbox" name="dist_%s" value="True" checked/></td>''' % ("No Distributor", "No Distributor")
        hide_distributorless = False
    else:
        print '''<td>%s</td> <td style="border-right: 1px solid #999"><input class="distributorbox" type="checkbox" name="dist_%s" value="True"/></td>''' % ("No Distributor", "No Distributor")
        hide_distributorless = True
    print '</tr></table><br />'
    
    return dists, hide_distributorless

def print_discontinued():
    if "hide_discontinued" in input_form:
        h_discontinued = input_form.getvalue("hide_discontinued")
    else:
        h_discontinued = False

    if h_discontinued:
        print '''Hide discontinued items?<input type="checkbox" name="hide_discontinued" value="True" checked/><br />'''
    else:
        print '''Hide discontinued items?<input type="checkbox" name="hide_discontinued" value="True"/><br />'''

    if "move_discontinued" in input_form:
        m_discontinued = input_form.getvalue("move_discontinued")
    else:
        m_discontinued = False
    
    if m_discontinued:
        print '''Move discontinued items to bottom of page?<input type="checkbox" name="move_discontinued" value="True" checked/><br/>'''
    else:
        print '''Move discontinued items to bottom of page?<input type="checkbox" name="move_discontinued" value="True" /><br/>'''

    return h_discontinued,m_discontinued
    
def print_form():
    discont = False
    move = False
    hide_categories = []
    hide_distributors=[]
    hide_distributorless = False
    hide_categoryless = False

    if discontinued_option:
        discont,move = print_discontinued()

    if categories_option:
        show_categories,hide_categoryless = print_categories()
    
    if distributors_option:
        show_distributors, hide_distributorless = print_distributors()
    return {'hide_discontinued' : discont, 'show_categories' : show_categories, 'show_distributors' : show_distributors, 'hide_distributorless' : hide_distributorless, 'hide_categoryless' : hide_categoryless, 'move_discontinued':move}
