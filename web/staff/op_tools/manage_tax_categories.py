#!/usr/bin/env python3
# manage_tax_categories.py
# This page lets the user add new tax categories as well as modify information about old ones

import op_db_library as db

print('''Content-Type: text/html\n\n''')
print('''<html><head>
    <title>Open Produce Tax Category Manager</title>
    <style type="text/css">
      * { font-family: sans-serif; font-size: 12px;}
    </style>
    <script type="text/javascript" src="../../common/jquery-1.3.2.min.js"></script>
    <script type="text/javascript">

    function trim(str) {
       return str.replace(/^[\s]+/g,'').replace(/[\s]+$/g,'');
    }

    function removeTaxCategory(id, name) {
      $.post('update_tax_categories.py', {taxcatid: id, action: 'remove'},
         function(data){
           $('.'+id+'_taxcat_tr').remove();
           $('.'+id+'_taxcat_tr', window.parent.main.document).remove();
           $('.'+id+'_taxcat_option', window.parent.main.document).remove();
           // there might be a better way to do this but I'm not sure
           $('td[onClick*=editTaxCategory]:contains('+name+')', window.parent.main.document).html('None');
         }, 'text');
    }
    function updateTaxCategory(id,taxcatname) {
      var taxrate = $('#'+id+'_tax_rate').val();
      $.post('update_tax_categories.py', {taxcatid: id, action: 'update', rate: taxrate},
         function(data){
            if(data.indexOf("Error:") == -1){
                $('td[onClick*=editTaxCategory]:contains('+taxcatname+')', window.parent.main.document).html(data);
                $('.'+id+'_taxcat_option', window.parent.main.document).text(data);
                alert('Updated '+taxcatname);
            }
            else{
                 alert(data);
            }
         }, 'text');
    }
    function addTaxCategory() {
       var name = $('#newTaxCatName').val();
       var taxrate = $('#newTaxCatRate').val();
       $.post('update_tax_categories.py', {taxcatname: name, action: 'add', rate: taxrate},
         function(data){
           if(data.indexOf('Error:') == -1){
             data = trim(data);
             data = data.split(',');
             var newHTML = '';

             newHTML += '<tr class="'+data[0]+'_taxcat_tr" id="' + data[0]+'_taxcat_tr"><td>'+data[1]+' &nbsp; </td>';
             newHTML += '<td><input type="text" id="'+data[0]+'_tax_rate" value="'+taxrate+'" size=5>';
             newHTML +='<td><input type="button" onClick="updateTaxCategory(' + data[0] + ",'"+data[1]+"'"+')" value="update" /></td>';

             newHTML += '<td><input type="button" onClick="removeTaxCategory('+ data[0] + ",'"+data[1]+"'"+ ')" value="remove" /></td></tr>';

             $('#taxcategories').append(newHTML);
             $('#newTaxCatName').val('');
             $('#newTaxCatRate').val('');
             var selectStatement = '<option class="'+data[0]+'_taxcat_option" value="'+data[0]+'">' +name +' ('+taxrate+'%) </option>';
             $('.addTaxCat', window.parent.main.document).append(selectStatement);
           }
           else{
             alert(data);
           }
         }, 'text');
    }


   </script>
    </head>
    ''')

print('''<body>
<table border=0  cellspacing=2 cellpadding=0>
<thead><tr>
<th>Tax Category</th>
<th>Rate (%)</th>
<th>Update</th>
<th>Remove</th>
</thead>
<tbody id="taxcategories">
''')

for tax in db.get_tax_categories():
    print('''<tr class="%d_taxcat_tr" id="%d_taxcat_tr"><td>%s</td>''' % (tax.get_id(), tax.get_id(),tax.get_name()))
    print('''<td><input type="text" id="%d_tax_rate" value="%.2f" size=5>''' % (tax.get_id(), tax.get_rate()*100))
    print('''<td><input type="button" onClick="updateTaxCategory(%d,'%s')" value="update" /></td>''' % (tax.get_id(),tax.get_name()))
    print('''<td><input type="button" onClick="removeTaxCategory(%d,'%s')" value="remove" /></td>''' % (tax.get_id(),tax.get_name()))
    print('''</tr>''')
print('''</tbody></table>''')

print('''<br /><div id="new"><tr><td><input id='newTaxCatName' type="text" size="10" value="" /></td>
<td><input type="text" id="newTaxCatRate" size=5>
<td><input type="button" onClick="addTaxCategory()" value="add new" /></td>''')
print('''</div>''')

print('''</body></html>''')
