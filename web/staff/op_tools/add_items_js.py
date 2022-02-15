#!/usr/bin/env python3
# add_items_js.py
# Patrick McQuighan
# edited add_items.py to be at the top of manage_prices
# uses javascript to add new <tr>s

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
    <script type="text/javascript" src="../../common/jquery-1.3.2.min.js"></script>
    <script type="text/javascript">
''')
# The following array is needed so that the when an item is split it will have the dropdown to change sale units
print('''units = new Array();''')
for i,unit in enumerate(db.get_units()):
    print('''units[%d] = '%s';''' % (i, str(unit)))
# The following is just to remove whitespace and &nbsp's from stuff
print('''
    function trim(str) {
       return str.replace(/^[\s]+/g,'').replace(/[\s]+$/g,'');
    }''')

print('''
    function addItem(){
       name = $('#name').val();
       size = $('#itemsize').val();
       s_unit = $('#size_unit').val();
       bcode = $('#barcode').val();
       plu = $('#plu').val();
       count = $('#count').val();
       distributor = $('#distributor').val();
       case_unit = $('#case_unit').val();
       dist_item_id = $('#dist_item_id').val();
       p_id = $('#price_id').val();
display_name = $('#display_name').val();
description = $('#description').val();

       var categories = '';
       catselect = $('#categories option:selected').each(function() {
                categories += $(this).val();
                categories += ',';
       });

       if(p_id == ''){  p_id = 0;}   // pass in 0 for p_id if it isn't selected

       $.post('update_item.py', {action: 'add', name : name, itemsize : size, size_unit : s_unit, barcode : bcode, plu : plu, count : count, price : $('#price').val(), price_unit : $('#price_unit').val(), price_id : p_id, taxcat : $('#taxcat').val(), distributor : distributor, dist_item_id : $('#dist_item_id').val(), wholesale_price : $('#wholesale_price').val(), case_size : $('#case_size').val(), case_unit : $('#case_unit').val(), categories : categories, description: description, display_name: display_name},
        function(data){
            if(data.indexOf('Error:') == -1){

                data = data.split(',');
                item_id = parseInt(data[0]);
                price_id = parseInt(data[1]);
                dist_id = parseInt(data[2]);
                case_price = parseFloat(data[3]);
                case_size = parseFloat(data[4]);
                each_cost = parseFloat(data[5]);
                margin = parseInt(data[6]);
                price = parseFloat(data[7]);
                price_sale_unit = data[8];
                link = data[9];

                newrow = '<tr class="'+item_id+'_tr">';
                newrow += '<td rowspan="1" id="'+item_id+'_td" width="400" style="padding-left: 1em;">'+ name +' ['+ size+' '+s_unit+']</td>';
                newrow += '<td rowspan="1" width="80"> <a href="'+link+'">'+item_id+'</a></td>';
                newrow += '<td rowspan="1" width="80" id="'+item_id+'_amt">'+count+' </td>';
                newrow += '<td rowspan="1" width="100"><input class="amt" id="'+item_id+'_in" name="'+item_id+'_in" size="2"/>';
                newrow += '<select id="'+item_id+'_dist_in" name="'+item_id+'_dist_in">';
                newrow += '<option value="'+distributor+'"> '+distributor+'</option></select></td>';
                newrow += '<td width="100"> '+ distributor+'</td>';
                newrow += '<td width="100"> <input class="ditemid" size="10" value="'+dist_item_id+'" id="'+item_id+'_'+dist_id+'_ditemid" /> </td>';
                newrow += '<td width="100">$<input class="casecost" size="6" value="'+case_price+'" id="'+item_id+'_'+dist_id+'_'+price_id+'_casecost" /></td>';
                newrow += '<td width="80" ><input class="casesize" size="5" value="'+case_size+'" id="'+item_id+'_'+dist_id+'_'+price_id+'_casesize" /></td>';
                newrow += '<td width="80">'+case_unit+'</td>';
                newrow += '<td width="80" id="'+item_id+'_'+dist_id+'_each">$'+each_cost+' </td>';
                newrow += '<td width="80" class="bad" id="'+item_id+'_'+dist_id+'_margin">'+margin+'% &nbsp;</td>';
                newrow += '<td rowspan="1" width="100"><input class="group" id="'+item_id+'_group" type="text" size="3"></input></td>';
                newrow += '<td rowspan="1" width="80"><div onClick="split('+item_id+')">split</div></td>';
                newrow += '</tr>';

                table = $('#' + price_id  + '_table', document);
                if(table.length != 0){
                   table.append(newrow);
                }
                else{  // make a new row in main table
                  var newpricerow = '<tr id="'+price_id+'_price"><td class="td">'+price_id+'</td>';
                  newpricerow += '<td class="td">$<input type="text" class="price" id="'+price_id+'_price_input" size="3" value="'+price+'"></input></td>';
                  newpricerow += '<td><select class="saleunit" id="'+price_id+'_sale_unit" onChange="setPriceSaleUnit('+price_id+')">';

                  for (var i=0; i<units.length; i++){
                     newpricerow += '<option value="'+units[i]+'"';
                     if (units[i] == trim(price_sale_unit)){
                        newpricerow += 'selected';
                     }
                     newpricerow+= '>' +units[i] +'</option>';
                   }
                   newpricerow += '</select></td>';

                  newpricerow += '<td colspan="13" class="td"> <table id="'+price_id+'_table" cellspacing=0 cellpadding=0></table></td></tr>';
                  $('#main', document).append(newpricerow);
                  $('#'+price_id+'_table',document).append(newrow);
               }
               // $('.price',document).keypress(parent.main.handlePriceChange);
               // $('.ditemid', document).keypress(parent.main.handleDItemChange);
               // $('.casesize', document).keypress(parent.main.handleCaseSizeChange);
               // $('.casecost', document).keypress(parent.main.handleCaseCostChange);
               // $('.group', document).keypress(parent.main.handleGroupChange);
               // $('.amt', document).keypress(parent.main.handleAmtChange);
// commented out bc idk what is happening -CR 10/29/21

$('#msg').text('Item ' + item_id + ' added.');

               $('#name').val('');
               $('#itemsize').val('');
               $('#barcode').val('');
               $('#plu').val('');
               $('#count').val('');
               $('#dist_item_id').val('');
               $('#price_id').val('');
               $('#wholesale_price').val('');
               $('#case_size').val('');
               $('#price').val('');
$('#description').val('');
$('#display_name').val('');


//                parent.main.updateMargins(price_id);
            }
            else{
               alert(data);
            }
      }, 'text')
};
    </script>
    </head>
    <body>''')



print('''<div id="msg"></div>''')    
print('''item name*: <input type="text" id="name" />''')
print('''item size*: <input type="text" id="itemsize" size="5" /> size unit*: <select id="size_unit">''')
for unit in db.get_units():
    print('''<option> %s </option> ''' % unit)
print('''</select>''')
print('''display name: <input type="text" name="display_name" id="display_name"  />''')
print('''description: <textarea name="description" id="description"></textarea>''')

print('''barcode: <input type="text" id="barcode" size="10" />''')
print('''PLU : <input type="text" id="plu" size="10" />''')
print('''count*: <input type="text" id="count" size="3" /> <br />''')
print('''price: $<input type="text" id="price" size="5"/>''')
print('''price unit: <select id="price_unit">''')
for unit in db.get_units():
    print('''<option> %s </option> ''' % unit)
print('''</select>''')
print('''price id: <input type="text" id="price_id" size="4" />''')
print('''tax category*: <select id="taxcat">''')
for taxcat in db.get_tax_categories():
    isdefault = ''
    if taxcat.get_name() == 'food':
        isdefault = 'selected'
    print('''<option %s> %s </option> ''' % (isdefault,taxcat))
print('''</select> <br />''')

print('''distributor*: <select id="distributor" /> ''')
print('''<option></option>''')
for dist in db.get_distributors():
    print('''<option> %s </option> ''' % dist)
print('''</select>''')

print('''distributor item id: <input type="text" id="dist_item_id" size=10" /> ''')
print('''case price: <input type="text" id="wholesale_price" size="5" /> ''')
print('''case size: <input type="text" id="case_size" size=5" /> ''')

print('''case unit: <select id="case_unit"> ''')
for unit in db.get_units():
    print('''<option> %s </option> ''' % unit)
print('''</select> <br />''')

print('''categories: <select multiple size=5 id="categories">''')
for cat in db.get_categories():
    print('''<option value="%d"> %s </option>''' % (cat.get_id(),cat))
print('''</select> <br />''')

print(''' <input type="button" value="Add Item" onClick="addItem()"/>''')
print('''Starred fields are required <br />''')
print('''Input either a price AND a price unit OR a price id''')
print('''</body></html>''')
