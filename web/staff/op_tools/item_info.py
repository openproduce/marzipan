#!/usr/bin/env python3
# item_info.py
# Patrick McQuighan
# This file is meant to display all kinds of specific data about a given item
# Mostly designed to reduce clutter on some of the other pages, but will also
# have random information like from inventory_history etc.

import op_db_library as db
from make_javascript import *
import cgi, sys
import cgitb
cgitb.enable()

def print_headers(key_handlers,select_handlers,itemid=0):
    print('''Content-Type: text/html\n\n''')
    print('''<html><head>
    <title>Open Produce Item #%d Info</title>''' % itemid)
    print('''
    <link rel="stylesheet" type="text/css" href="../../common/tools.css" />
    <script type="text/javascript" src="../../common/jquery-1.3.2.min.js"></script>\n
    <script type="text/javascript"> ''')
    print('''var itemid = %d;''' % itemid)  # now itemid is a variable in the javascript space so we can just use that instead of passing things around

    # Now print out a function that can fill out dropdowns with units for the case units field (needed for when we add a distributor)
    print('''function setHandlers(){
        $('.count').keypress(function(e) {
                if (e.which == 13) {
                        var id = parseInt(this.id);
                        $('[id^='+id+'_count]').removeClass('default').removeClass('complete').addClass('submitting');
                        $('[id^='+id+'_count]').attr('disabled','true');

                        $.post('update_item.py', { action: 'count', id: id, count: $(this).val() },
                               function(data) {
                                        if (data != ''){
                                            data = data;
                                            $('[id^='+id+'_count]').val(data);
                                        }

                                        $('[id^='+id+'_count]').removeClass('default').removeClass('submitting').addClass('complete');
                                        $('[id^='+id+'_count]').removeAttr('disabled');
                                }, 'text');
                }
        });

    $('.op_price').keypress(handleOPPriceChange);
 ''')
    for k_h in key_handlers:
        key_handlers[k_h].print_ready()
    for s_h in select_handlers:
        select_handlers[s_h].print_ready()
    print('''}''')

    for k_h in key_handlers:
        key_handlers[k_h].print_function()
    for s_h in select_handlers:
        select_handlers[s_h].print_function()

    print('''
    function trim(str) {
       return str.replace(/^[\s]+/g,'').replace(/[\s]+$/g,'');
    }

  function updateAllMargins() {
    $('[id*=_dist_tr]').each(
       function() {
         updateMargin(parseInt(this.id));
       });
  }

  function updateMargin(ditem_id) {
    $.post('update_distributor_item.py', {action : 'query-margin', dist_item_id : ditem_id},
      function(data){
        if(data.indexOf('Error:')!=-1) { alert(data); }
        else {
          data = data.split(',');
          each = data[0];
          margin = trim(data[1]);
          $('#'+ditem_id+'_each').text('$'+each);
          $('#'+ditem_id+'_margin').text(margin+'%');
          if(margin <= 20){
              $('#'+ditem_id+'_margin').attr('class','bad');
          } else if(margin <= 30) {
              $('#'+ditem_id+'_margin').attr('class','mid');
          } else{
              $('#'+ditem_id+'_margin').attr('class','good');
          }
        }
    },'text');
   } ''')
    print('''
  function removeBarcode(bc_item_id) {
    $.post('update_barcode_item.py', {action : 'remove', bc_item_id : bc_item_id},
      function(data){
        if(data.indexOf('Error:')!=-1) { alert(data); }
        else {
          $('#'+bc_item_id+'_barcode_tr').remove();
        }
    },'text');
   }

   function addBarcode() {
     var selected = $('#new_barcode').val();

     $.post('update_barcode_item.py', {action : 'add', item_id : itemid, barcode: selected},
       function(data){
         if(data.indexOf('Error:') != -1) { alert(data); }
         else {
            var newid = parseInt(data);
            var newrow = '<tr id="'+newid+'_barcode_tr">';
            newrow += '<td><input type="text" class="%s" id="'+newid+'_bc" value="'+selected+'" size="16"/></td>'; ''' % (key_handlers['barcode'].element))
    print('''
            newrow += '<td><button input="button" onClick="removeBarcode('+newid+')">remove</button></td></tr>';
            $('#barcodes').append(newrow);
            $('#new_barcode').val('');
            setHandlers();
         }
       }, 'text');
    }

   function removeCategory(cat_item_id) {
     $.post('update_category_item.py', {action: 'remove', cat_item_id : cat_item_id},
       function(data){
          if(data.indexOf('Error:') != -1) { alert(data); }
          else{
             $('#'+cat_item_id+'_category_tr').remove();
          }
     }, 'text');
   }

   function addCategory() {
     var selected = $('#new_category').val();
     $.post('update_category_item.py', {action : 'add', item_id : itemid, cat_id : selected},
       function(data){
         if(data.indexOf('Error:') != -1) { alert(data); }
         else {
           // data contains the new category_item.id, link to the category page
             data = data.split(',');
             var newid = parseInt(data[0]);
             var link = data[1];
             newrow = '<tr id="'+newid+'_category_tr">';
             newrow += '<td> <a href="' +link+'">' + $('#new_category option:selected').text() + '</a> </td>';
             newrow += '<td><button type="button" onClick="removeCategory('+newid+')">remove</button></td>';
             newrow += '</tr>';

             $('#categories').append(newrow);
         }
       }, 'text');
   }

   function removeDistributor(dist_item_id) {
      if (!confirm("Are you sure you want to remove this distributor?")) { return;}
      $.post('update_distributor_item.py', {action:'remove_byid', dist_item_id : dist_item_id},
        function(data){
           if(data.indexOf('Error:') != -1) { alert(data); }
           else{
             $('#'+dist_item_id+'_dist_tr').remove();
           }
        }, 'text');
   }

   function updateItemString() {
      $.post('update_item.py', {action:'get-string', id : itemid},
      function(data){ $('#item_string').html('OP SKU '+itemid+': '+data);}, 'text');
   }

   function toggleHistory() {
      $('#history').toggle();
      if ($('#history_button').html().indexOf('Show') != -1){  $('#history_button').html('Hide History'); }
      else { $('#history_button').html('Show History');}
   }

   function toggleGraph() {
      $('#graph').toggle();
      if ($('#graph_button').html().indexOf('Show') != -1){  $('#graph_button').html('Hide Graph'); }
      else { $('#graph_button').html('Show Graph');}
   }

   function discontinueItem(ckbox){
     var itemid = parseInt(ckbox.id);
     $.post('update_item.py', { action: 'status', id: itemid, stocked: ckbox.checked},
         function(data){
         }, 'text');
   }

   function mergeItem() {
     var into_id = $('#merge').val();
     window.open('merge_confirmation.py?old='+itemid+'&into='+into_id);
   }

   function handleOPPriceChange(e) {
     if (e.which == 13) {
        var id = parseInt(this.id);
        var price = this.value;
        box = this;
        $box = $(box);
        $box.removeClass('default').removeClass('complete').addClass('submitting');
        $box.attr('disabled','true');
        $.post('update_prices.py', {action: 'item_price', item_id : id, price : price},
          function(data) {
            if(data.indexOf('Error:') != -1) { alert(data);}
            else if (data.indexOf('Warning:') != -1) {
              if (confirm(data)) {
                $.post('update_prices.py', {action: 'item_price', item_id : id, price : price, confirmed : true},
                  function(data) {
                    if(data.indexOf('Error:') != -1) { alert(data);}
                    else{ $box.removeClass('default').removeClass('submitting').addClass('complete'); updateAllMargins();}
                  },'text');

              }
            }
            else{ $box.removeClass('default').removeClass('submitting').addClass('complete'); updateAllMargins();}

           box.disabled = false;
           setTimeout(function($box) { $box.removeClass('submitting').removeClass('complete').addClass('default');}, 4000, $box);

          },'text');
     }
   }

   function updateNotes() {
     var n = $('#notes').val();
     $box = $('#notes');
     $box.removeClass('default').removeClass('complete').addClass('submitting');
     $.post('update_item.py', {action : 'update-notes', item_id: itemid, notes : n},
         function(data){
           if(data.indexOf('Error:') == -1) {
              $box.removeClass('default').removeClass('submitting').addClass('complete');
           }
           else {
              alert(data);
           }
         }, 'text');
    setTimeout(function($box) { $box.removeClass('submitting').removeClass('complete').addClass('default');}, 4000, $box);
   }

   function addDistributor(){
      var selected = $('#new_distributor').val();
      $.post('update_distributor_item.py', { action: 'add', distid : selected, item : itemid, item_info : true },
        function(data){
           if(data.indexOf('Error:') != -1) { alert(data); }
           else {
             // data contains the dist_item_id for the newly added distributor_item
             var newid = parseInt(data);
             newrow = '<tr id="'+newid+'_dist_tr">';
             newrow += '<td>' + $('#new_distributor option:selected').text() + '</td>'; ''')
    print(' '*13 + '''newrow += '<td> <input type="text" class="%s" id="'+newid+'_ditemid" value="0" size="16" /></td>'; ''' % key_handlers['ditemid'].element)
    print(' '*13 + '''newrow += '<td><input type="text" class="%s" id="'+newid+'_casesize" value="0.00" size="4" /></td>'; ''' % key_handlers['casesize'].element)
    print(' '*13 +  '''newrow += '<td><select class="%s" id="'+newid+'_caseunits">'; ''' % select_handlers['caseunit'].element)
    for u in db.get_units():
        print(' '*13 + '''newrow += '<option value="%d"> %s </option>' ''' % (u.get_id(), u))
    print(' '*13 + '''newrow += '</select></td>';  ''')
    print(' '*13 + '''newrow += '<td>$<input type="text" class="%s" id="'+newid+'_caseprice" value="0.00" size="5" /> </td>'; ''' % key_handlers['caseprice'].element)
    print('''
	      newrow += '<td width="80" id="'+newid+'_each"></td>';
              newrow += '<td width="80" id="'+newid+'_margin"></td>';
''')
    print(' '*13 + '''newrow += '<td><button type="button" onClick="removeDistributor('+newid+')">remove</button></td>';

             newrow += '</tr>';
             $('#distributors').append(newrow);
             setHandlers();
             updateMargin(newid);
           }
        }, 'text');
   }

   $(document).ready(function() {
       setHandlers();
     }); // end document.ready
    </script>
    ''')
    print('''</head>
    <body>''')

def print_unit_options(selected):
    for unit in db.get_units():
        if unit.get_id() == selected:
            print('<option value="%d" selected> %s </option>' % (unit.get_id(), unit.get_name()))
        else:
            print('<option value="%d"> %s </option>' % (unit.get_id(), unit.get_name()))

def print_distributor_items(item,key_handlers,select_handlers):
    print('''<table id="distributors">
                 <thead>
                 <th>Distributor</th>
                 <th>Dist Item ID</th>
                 <th>Case Size</th>
                 <th>Case Units</th>
                 <th>Case Price</th>
                 <th>Each Price</th>
                 <th>Margin</th>
                 <th>Remove</th>
                 </thead>''')
    for ditem in item.get_distributor_items():
        print('''<tr id="%d_dist_tr">''' % (ditem.get_id(),))
        dist = db.get_distributor(ditem.get_dist_id())
        print('''<td> %s</td><td> <input type="text" class="%s" id="%d_ditemid" value="%s" size="16" /></td>''' % (dist,key_handlers['ditemid'].element,ditem.get_id(),ditem.get_dist_item_id()))
        print('''<td><input type="text" class="%s" id="%d_casesize" value="%.2f" size="4" /> </td>''' % (key_handlers['casesize'].element,ditem.get_id(), ditem.get_case_size()))
        print('''<td><select class="%s" id="%d_caseunits">''' % (select_handlers['caseunit'].element,ditem.get_id()))
        print_unit_options(ditem.get_case_unit_id())
        print('''</select></td>''')
        print('''<td>$<input type="text" class="%s" id="%d_caseprice" value="%.2f" size="5" /></td>''' % (key_handlers['caseprice'].element,ditem.get_id(), ditem.get_wholesale_price()))

        each_cost = ditem.get_each_cost()
        op_price = item.get_price()
        tax = item.get_tax_value()

        if op_price - tax > 0:
            margin = (1.0 - each_cost/(op_price - tax)) * 100
        else:
            margin = 100

        print('''<td width="80" id="%d_each">$%.2f </td>''' % (ditem.get_id(),each_cost))
        if margin <= 20:
            print('''<td width="80" class="bad" id="%d_margin"> %.0f%% &nbsp;</td>''' % (ditem.get_id(), margin))
        elif margin <= 30:
            print('''<td width="80" class="mid" id="%d_margin"> %.0f%% &nbsp; </td>''' % (ditem.get_id(), margin))
        else:
            print('''<td width="80" class="good" id="%d_margin"> %.0f%% &nbsp; </td>''' % (ditem.get_id(), margin))

        print('''<td><button type="button" onClick="removeDistributor(%d)">remove</button></td>''' % (ditem.get_id(),))

        print('</tr>')
    print('</table>')
    print('''<select id="new_distributor">''')
    for dist in db.get_distributors():
        print('''<option value="%d"> %s </option>''' % (dist.get_id(), dist))
    print('''</select>''')
    print('''<button type="button" onClick="addDistributor()"> Add Distributor</button>''')

def print_tax_category_options(selected):
    for taxcat in db.get_tax_categories():
        if taxcat == selected:
            print('<option value="%d" selected> %s </option>' % (taxcat.get_id(), taxcat))
        else:
            print('<option value="%d"> %s </option>' % (taxcat.get_id(), taxcat))

def print_tax_categories(item,select_handlers):
    print('<select class="%s">' % (select_handlers['taxcat'].element))
    print_tax_category_options(item.get_tax_category())
    print('</select>')

def print_categories(item):
    print('<table id="categories">')
    print('''<thead>
          <th>Category</th>
          <th>Remove</th>
          </thead>''')
    for category_item in item.get_category_items():
        category = db.get_category(category_item.get_cat_id())
        print('''<tr id="%d_category_tr"><td><a href="%s">%s</a></td><td><button type="button" onClick="removeCategory(%d)"> remove </button> </td>''' % (category_item.get_id(),db.get_category_info_page_link(category.get_id()),category.get_name(),category_item.get_id()))
    print('''</table>''')
    print('<select id="new_category">')
    for cat in db.get_categories():
        print('''<option value="%d"> %s </option>''' % (cat.get_id(), cat))
    print('</select>')
    print('''<button type="button" onClick="addCategory()"> Add Category </button>''')
    print('<br />'*2)

def print_item_history(item):
    print('''<br /> <b>30 day history for item %d (%s) </b><br />''' % (item.get_id(), item))
    total_sales,total_deliveries,total_slush,history = db.get_item_history(item.get_id(),30)
    print('<b>Total sales: %d <br />' % (total_sales,))
    print('Total deliveries: %d <br />' % (total_deliveries,))
    print('Total slushfunded: %d <br /></b>' % (total_slush,))
    print('''<table><thead><th>Date</th><th>+/-</th><th>Type</th></thead>''')
    for ttp in history:
        print('''<tr><td>%s</td><td>%.2f</td><td>%s</td></tr>''' % ttp)
    print('''</table>''')
    print('''<br /> <b>365 day history for item %d (%s) </b><br />''' % (item.get_id(), item)) 
    total_sales,total_deliveries,total_slush,history = db.get_item_history(item.get_id(),365)
    print('<b>Total sales: %d <br />' % (total_sales,)) 
    print('Total deliveries: %d <br />' % (total_deliveries,)) 
    print('Total slushfunded: %d <br /></b>' % (total_slush,))
    print('''<table><thead><th>Date</th><th>+/-</th><th>Type</th></thead>''') 
    for ttp in history:
        print( '''<tr><td>%s</td><td>%.2f</td><td>%s</td></tr>''' % ttp)
    print('''</table>''') 


def print_barcodes(item,key_handlers):
    print('''<table id="barcodes">
             <thead>
             <th>Barcode</th>
             <th>Remove</th>
             </thead>''')

    for bc in item.get_barcodes():
            print('''<tr id="%d_barcode_tr"><td><input type="text" class="%s" id="%d_bc" value="%s" size="16"/></td>''' % (bc.get_id(),key_handlers['barcode'].element,bc.get_id(), bc.get_barcode()))
            print('''<td><button input="button" onClick="removeBarcode(%d)">remove</button></td></tr>''' % (bc.get_id()))
    print('''</table>''')
    print('''<input type="text" id="new_barcode" value="" size="16"/>''')
    print('''<button type="button" onClick="addBarcode()"> Add Barcode </button>''')
    print('''<br /><br />''')

def main():
    form = cgi.FieldStorage()
    if "itemid" in form:
        itemid = int(form.getvalue("itemid"))
    else:
        itemid = 0
    # The index ito this dict is used in other parts of the python code for when we print out html elements,
    # we index into the key_handlers list to add the appropriate key handler to that object
    key_handlers = {'ditemid' : KeyHandler('handleDistItemIdChange','changes the distributor_item.dist_item_id field',ENTER_KEY,
                                           'update_distributor_item.py',{'action':'update_byid','dist_item_id':TEXTBOX_ID,'distitemid':TEXTBOX_VALUE},'','ditemid'),

                    'casesize' : KeyHandler('handleCaseSizeChange','changes the case size of a distributor_item',ENTER_KEY,
                                            'update_distributor_item.py',{'action':'update_byid','dist_item_id':TEXTBOX_ID,'casesize':TEXTBOX_VALUE},
                                            'updateMargin(id)','casesize'),

                    'caseprice' : KeyHandler('handleCasePriceChange','changes the wholesale_price of a distributor_item',ENTER_KEY,
                                             'update_distributor_item.py',{'action':'update_byid','dist_item_id':TEXTBOX_ID,'caseprice':TEXTBOX_VALUE},
                                             'updateMargin(id)','caseprice'),
                    'name' : KeyHandler('handleItemNameChange','changes the name of a given item', ENTER_KEY,
                                        'update_item.py',{'action':'name','id' : str(itemid), 'name':TEXTBOX_VALUE},
                                        'updateItemString();', 'item_name'),
                    'itemsize' : KeyHandler('handleItemSizeChange','changes the size of a given item', ENTER_KEY,
                                            'update_item.py',{'action':'size','id':str(itemid),'size':TEXTBOX_VALUE},
                                            'updateItemString();', 'item_string'),

                    'saleunit' : KeyHandler('handleItemSaleUnit','changes the sold by size of a given item', ENTER_KEY,
                                            'update_item.py',{'action':'saleunit','id':str(itemid),'size':TEXTBOX_VALUE},
                                            'updateItemString();', 'item_string'),

                    'barcode' : KeyHandler('handleBarcodeChange','changes the barcode of an item', ENTER_KEY,
                                           'update_item.py',{'action':'barcode_byid', 'barcode_id':TEXTBOX_ID, 'new_barcode':TEXTBOX_VALUE}, '','barcode'),


                    }
    select_handlers = {'taxcat' : SelectHandler('setTaxCategory','changes the tax category of the item','update_tax_categories.py',
                                                {'action':'set-item','item_id':str(itemid),'taxcatid':SELECT_VALUE}, '','tax_category'),

                       'itemsize' : SelectHandler('setItemSizeUnit','changes the size of the item','update_item.py',
                                                  {'action':'sizeunit_byid','id':str(itemid), 'sizeunit':SELECT_VALUE}, 'updateItemString();','item_size_unit'),

                       'saleunit' : SelectHandler('setItemSaleUnit','changes the size of the item price','update_item.py',
                                                  {'action':'saleunit','id':str(itemid), 'saleunit':SELECT_VALUE}, 'updateItemString();','item_sale_unit'),


                       'caseunit' : SelectHandler('setCaseUnits','changes the units of the distributor_item', 'update_distributor_item.py',
                                                  {'action':'update_byid', 'dist_item_id' : SELECT_ID , 'caseunit':SELECT_VALUE},
                                                  '', 'dist_item_id')
                       }

    print_headers(key_handlers,select_handlers,itemid)

    print('''<form name="item" action="item_info.py" method="get">''')
    print('''Input an item SKU''')
    print('''<input type="text" name="itemid" size="4" /> <input type="submit" value="Display" />''')
    print('''</form>''')

    if "itemid" in form:
        itemid = int(form.getvalue("itemid"))
        if not db.is_item(itemid):
            print('''Item %d not found''' % itemid)
            sys.exit(0)
        item = db.get_item(itemid)
        print('''<b><div id="item_string">OP SKU  %d: %s</div></b><br />''' % (itemid, item))
        print('''Name: <input type="text" size="40" class="%s" value="%s" /> <br />''' % (key_handlers['name'].element, item.get_name()))
        print('''Item size: <input type="text" size="5" class="%s" value="%.2f" /> &nbsp;''' % (key_handlers['itemsize'].element, item.get_unit_size()))
        print(''' <select class="%s">''' % (select_handlers['itemsize'].element))
        print_unit_options(item.get_size_unit_id())
        print('''</select> <br />''')
        print('''Tax category:''')
        print_tax_categories(item,select_handlers)
        print('''<br />''')
        print('''OP Price: $<input type="text" size="5" class="op_price" value="%.2f" id="%d_op_price" />''' % (item.get_price(),item.get_id()))
        # priced by
        print(''' <select class="%s">''' % (select_handlers['saleunit'].element))
        print_unit_options(item.get_sale_unit_id())
        print('''</select> <br />''')
        print('''<br />''')
#        print('''OP in store count: %d''' % (item.get_count()))
        print('''OP in store count: <input type="text" size="5" class="count" value="%d" id="%d_count" />''' % (item.get_count(),item.get_id()))
        print('''<br />''')
        print('''Stocked:''')
        if not item.get_is_discontinued():
            print('''<input type="checkbox" id="%d_isStocked" onClick="discontinueItem(this)" checked />''' % (itemid,))
        else:
            print('''<input type="checkbox" id="%d_isStocked"  onClick="discontinueItem(this)"/>''' % (itemid,))

        print('''<br />'''*2)
        print_barcodes(item,key_handlers)
        print_categories(item)
        print_distributor_items(item,key_handlers,select_handlers)
        print('''<br /> <br />''')
        #print('''Merge this item into item with OP SKU:''')
        #print('''<input type="text" id="merge" size="4" />''')
        #print('''<button type="button" id="merge_btn" onClick="mergeItem()"> Merge </button><br /><br />''')
        print('''Notes: <br /><textarea id="notes" cols="40" rows="4">%s</textarea><br />''' % (item.get_notes()))
        print('''<button type="button" onClick="updateNotes()">Update Notes</button><br />''')
        print('''<br /> <br /><button type="button" id="history_button" onClick="toggleHistory()"> Show History </button>''')
        print('''<br />''')
        print('''<div id="history" style="display: none">''')
        print_item_history(item)
        print('''</div>''')
        print('''<br /><button type="button" id="graph_button" onClick="toggleGraph()"> Show Graph </button>''')
        print('''<div id="graph" style="display: none">''')
        print('''<img src="item_graphs.py?itemid=%d&graph=sales" alt="%d_sales">''' % (itemid,itemid))
        print('''<img src="item_graphs.py?itemid=%d&graph=prices" alt=%d_prices">''' % (itemid, itemid))
        print('''</div>''')

    print('''</body></html>''')

if __name__ == "__main__":
    main()
