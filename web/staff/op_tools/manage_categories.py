#!/usr/bin/env python
# manage_categories.py
# This page lets the user add new categories as well as modify information about old ones

import op_db_library as db

print '''Content-Type: text/html\n\n'''
print '''<html><head>
    <title>Open Produce Category Manager</title>
    <style type="text/css">
      * { font-family: sans-serif; font-size: 12px;}
    </style>
    <script type="text/javascript" src="../../common/jquery-1.3.2.min.js"></script>
    <script type="text/javascript">

    function trim(str) {
       return str.replace(/^[\s]+/g,'').replace(/[\s]+$/g,'');
    }

    function removeCategory(id, catname) {
      $.post('update_categories.py', {action: 'remove', catid: id},
         function(data){
           if(data.indexOf("Error:") != -1) { alert(data);}
           else {
             $('.'+id+'_cat_tr').remove();
             $('.'+id+'_cat_tr', window.parent.main.document).remove();
             $('.'+id+'_cat_option', window.parent.main.document).remove();
             // there might be a better way to do this but I'm not sure
             $('td[onClick*=editCategory]:contains('+catname+')', window.parent.main.document).html($('td[onClick*=editCategory]:contains('+catname+')', window.parent.main.document).html().replace(catname+',',''));
             $('td[onClick*=editCategory]:contains('+catname+')', window.parent.main.document).html($('td[onClick*=editCategory]:contains('+catname+')', window.parent.main.document).html().replace(catname,''));
           }
         }, 'text');
    } 
    function addCategory() {
       var catname = $('#newCatName').val();
       if (catname != ''){
         $.post('update_categories.py', {cat: catname, action: 'add'},
           function(data){
               data = trim(data).split(',');
               var newHTML = '';
               newHTML += '<tr class="'+data[0]+'_cat_tr" id="' + data[0]+'_cat_tr"><td>'+data[1]+' &nbsp; </td>';
               newHTML += '<td><input type="button" onClick="removeCategory('+ data[0]+",'" + data[1] + "'" + ')" value="remove" /></td></tr>';
               $('#categories').append(newHTML);
               $('#newCatName').val('');
               var selectStatement = '<option class="'+data[0]+'_cat_option" value="'+data[0]+'">' +data[1] +'</option>';
               $('.addCat', window.parent.main.document).append(selectStatement);
               var multiselectStatement = '<option class="'+data[0]+'_cat_option" value="'+data[1]+'">' +data[1] +'</option>';
               $('.multi_category', window.parent.main.document).append(multiselectStatement);

           }, 'text');

       }
       else{
          alert('Error: no name provided');
       }
    }


   </script>
    </head>
    '''

print '''<body>
<table border=0  cellspacing=2 cellpadding=0>
<thead><tr>
<th>Category</th>
<th>Remove</th>
</thead>
<tbody id="categories">
'''

for cat in db.get_categories():
    print '''<tr class="%d_cat_tr" id="%d_cat_tr"><td>%s</td>''' % (cat.get_id(), cat.get_id(),cat.get_name())
    print '''<td><input type="button" onClick="removeCategory(%d,'%s')" value="remove" /></td>''' % (cat.get_id(),cat.get_name())
    print '''</tr>'''
print '''</tbody></table>'''

print '''<br /><div id="new"><tr><td><input id='newCatName' type="text" size="10" value="" /></td><td><input type="button" onClick="addCategory()" value="add new" /></td>'''
print '''</div>'''

print '''</body></html>'''
