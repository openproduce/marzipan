#!/usr/bin/env python
# merge_confirmation.py
# Patrick McQuighan
# This is the confirmation page displaying all information about the two items to be merged
# to ensure that a user cannot accidentally merge two items.

import op_db_library as db
import cgi, sys
import cgitb
cgitb.enable()

def print_headers():
    print '''Content-Type: text/html

<html>
 <head>
  <title>Open Produce Item Merger </title>
  <link rel="stylesheet" type="text/css" href="../../tools.css" /> 
  <script type="text/javascript" src="../../jquery-1.3.2.min.js"></script>\n
  <script type="text/javascript">
    function merge(old_item, into_item) {
      $.post("merge_items.py", {old : old_item, into : into_item, barcodes : $('#m_barcodes').attr('checked'), 
                                deliveries : $('#m_deliveries').attr('checked'), dist_items : $('#m_dist_items').attr('checked'), sales : $('#m_sales').attr('checked')}, 
        function(data){
          if (data.indexOf('Error:') != -1) {
            alert(data); 
          }
          else {
            alert("Successfully merged "+old_item+" into "+into_item+".\\nWill redirect to the new item's info page when you click ok.");
            location.replace("item_info.py?itemid="+into_item);
          }
        }, 'text');
    }
  </script>
 </head>
 <body>'''

def print_tables (name1,list1,name2,list2):
    print '''
<table>
  <thead>
   <tr>
     <th class="td_rborder">Merging</th><th>Into</th>
   </tr>
  </thead>
   <tr>
   <td class="td_rborder">%s</td><td>%s</td>
   </tr>
  ''' % (name1, name2)
    len1 = len(list1)
    len2 = len(list2)
    max_val = max(len1, len2)
    
    for i in range(max_val):
        print '<tr>'
        if i < len1:
            print '<td class="td_rborder">%s</td>' % (list1[i])
        else:
            print '<td class="td_rborder">&nbsp;</td>'

        if i < len2:
            print '<td>%s</td>' % (list2[i])
        else:
            print '<td>&nbsp;</td>'

        print '</tr>'
    print '''</table> '''

def main():
    print_headers()
    form = cgi.FieldStorage()
    if 'old' not in form or 'into' not in form:
        print 'Error: You need to include the OLD item id and the item id it is being merged INTO'
        print '''Use the interface on <a href='item_info.py'>item_info.py</a> to do this'''
    else:
        old_item_id = int(form.getvalue('old'))
        into_item_id = int(form.getvalue('into'))
        if not db.is_item(old_item_id):
            print 'Item %d not found.' % (old_item_id)
            sys.exit(0)
        if not db.is_item(into_item_id):
            print 'Item %d not found.' % (into_item_id)
            sys.exit(0)
        old_item = db.get_item(old_item_id)
        into_item = db.get_item(into_item_id)
        old_name = old_item.get_name()
        into_name = into_item.get_name()
        print '''<b>%s</b> (SKU: %d) will be REMOVED from the database.<br />''' % (old_item,old_item_id)
        print '''It will be merged INTO <b>%s</b> (SKU: %d).<br />''' % (into_item, into_item_id)
        print '''Note: There is currently no way to undo the merge operation.<br />'''
        print '''Additonally, if the merge results in the item having multiple entries for a given distributor the display in catalog.py will be wonky.  This will be corrected soon. Everything will display correctly in the item's item_info.py page so use that instead.<br /><br />'''

        print '''<u>Current Barcodes:</u>'''
        print_tables(old_name, old_item.get_barcodes(), into_name, into_item.get_barcodes())
        print '<br />'
        print '''<u>Current Distributor Item Info:</u>'''
        print_tables(old_name, old_item.get_distributor_items(), into_name, into_item.get_distributor_items())
        print '<br />'

        print '''The following options control whether certain data about <b>%s</b> will be ADDED to <b>%s</b> <br />''' % (old_name, into_name)

        print '''Merge barcodes: <input type="checkbox" id="m_barcodes" /> <br />'''
        print '''Merge delivery records: <input type="checkbox" id="m_deliveries" checked /><br />'''
        print '''Merge distributor item info: <input type="checkbox" id="m_dist_items" checked /><br />'''
        print '''Merge sales data (Only Steven should change this option!): <input type="checkbox" id="m_sales" checked /><br />'''
        print '''<br />'''
        print '''The count and last_manual_count for the old item will disappear and not affect the count/last_manual_count of the item it is being merged into.  However, the count of the merged item may change due to the sales/deliveries from the old item.'''
        print '''<br />'''
        print '''<button type="button" onClick="merge(%d,%d)">Merge</button> ''' % (old_item_id, into_item_id)
    print '''
 </body>
</html>'''

if __name__ == "__main__":
    main()
