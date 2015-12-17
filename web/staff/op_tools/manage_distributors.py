#!/usr/bin/env python
# manage_distributors.py
# This page lets the user add new distributors as well as modify information about old ones

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

print '''Content-Type: text/html\n\n'''
print '''<html><head>
    <title>Open Produce Distributor Manager</title>
    <style type="text/css">
    * { font-family: sans-serif; font-size: 12px;}
    </style>
    <script type="text/javascript" src="../../common/jquery-1.3.2.min.js"></script>
    <script type="text/javascript">

    function trim(str) {
       return str.replace(/^[\s]+/g,'').replace(/[\s]+$/g,'');
    }

    function removeDistributor(distid) {
      $.post('update_distributors.py', {id: distid, action: 'remove'},
         function(data){
           if (data.indexOf('Error:') == -1){
                  $('.'+distid+'_dist_tr').remove();
                  $('.'+distid+'_dist_tr', window.parent.main.document).remove();  
                  $('.'+distid+'_dist_option', window.parent.main.document).remove();
                 // there might be a better way to do this but I'm not sure
                  $('td:contains('+trim(data)+')', window.parent.main.document).each( function(){
                     if (this.id != '') {  // skip over things from the item display form
                       var itemid = parseInt(this.id);
                       var thistd = this;
                       $.post('update_distributor_item.py', {action:'query', item:itemid},
                         function(data){
                           if (data.indexOf('Error:') != -1) { alert(data); }
                           else {
                             $(thistd).html(data+' &nbsp;');
                           }
                      
                       },'text');
                     }
                  });
        
           }
           else{
              alert(data);
           }
          }, 'text');
     } 

     function addDistributor() {
        var distname = $('#newDistName').val();
        distname = trim(distname);
        $.post('update_distributors.py', {name: distname, action: 'add'},
          function(data){
              if (data.indexOf("Error:") == -1){
                 var newHTML = '';
                 data = data.split(',');
                 newHTML += '<tr class="'+data[0]+'_dist_tr" id="' + data[0]+'_tr"><td>'+data[1]+'</td>';
                 newHTML += '<td><input type="button" onClick="removeDistributor('+data[0]+')" value="remove" /></td></tr>'
                 $('#distributors').append(newHTML);
                 $('#newDistName').val('');
                 selectStatement = '<option class="'+data[0]+'_dist_option" value="'+data[0]+'">' +distname +'</option>';
                 $('.addDist', window.parent.main.document).append(selectStatement);
                 multiselectStatement = '<option class="'+data[0]+'_dist_option" value="'+data[1]+'">' +distname +'</option>';
                 $('.multi_dist', window.parent.main.document).append(multiselectStatement);

              }
              else{
                 alert(data);
              }

          }, 'text');
     }

    </script>
    </head>
    '''

print '''<body>
<table border=0  cellspacing=2 cellpadding=0>
<thead><tr>
<th>Distributor</th>
<th>Remove</th>
</thead>
<tbody id="distributors">
'''

for dist in db.get_distributors():
    print '''<tr class="%d_dist_tr" id="%d_tr"><td>%s</td>''' % (dist.get_id(),dist.get_id(),dist.get_name())
    print '''<td><input type="button" onClick="removeDistributor(%d)" value="remove" /></td>''' % (dist.get_id())
    print '''</tr>'''
print '''</tbody></table>'''

print '''<br /><div id="new"><tr><td><input id='newDistName' type="text" size="10" value="" /></td><td><input type="button" onClick="addDistributor()" value="add new" /></td>'''
print '''</div>'''

print '''</body></html>'''
