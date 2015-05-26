#!/usr/bin/env python
# manage_items.py
# Patrick McQuighan
# Tool for changing item names and stocked status and adding/removing distributors/categories/tax categories.

import op_db_library as db
import item_display_form as idf
import cgi
import cgitb
cgitb.enable() 

def print_headers():
    print '''Content-Type: text/html\n\n'''
    print '''<html><head>
    <title>Open Produce Item Manager</title>

    <link rel="stylesheet" type="text/css" href="../../common/tools.css" />
    <script type="text/javascript" src="../../common/jquery-1.3.2.min.js"></script>
    <script type="text/javascript" src="../../common/sorttable.js"></script>
    <script type="text/javascript" src="../../common/fix_table_headers.js"></script>
<script type="text/javascript">
function uncheckAllMulti(){
    $('.multi').each(function (){
         this.checked = false;
    });
}

function multiAddDist(){
   var selectedDist = $('#multi_dist').val();
   $('.multi:checked').each(function (){
       var id = this.id;
       $.post('update_distributor_item.py', {action: 'add', item: id, distid : selectedDist},
           function(data){
              if(data.indexOf('Error:') == -1){   // update text
                $.post('update_distributor_item.py', { action: 'query', item: id},
                  function(data){ 
                     $('#'+id+'_dist').html(data + ' &nbsp; ');
                   }, 'text');
               }
              else { alert(data); }
          },'text');
    });
}

function multiRemoveDist(){
   var selectedDist = $('#multi_dist').val();
   $('.multi:checked').each(function (){
       var id = this.id;
       $.post('update_distributor_item.py', {action: 'remove', item: id, distid : selectedDist},
           function(data){
              if(data.indexOf('Error:') == -1){   // update text
                $.post('update_distributor_item.py', { action: 'query', item: id},
                  function(data){  
                    $('#'+id+'_dist').html(data + ' &nbsp; ');
                  }, 'text');
               }
              else { alert(data); }
          },'text');
    });

}

function multiAddCategory(){
   var selectedCat = $('#multi_category').val();
   $('.multi:checked').each(function (){
      var itemid = this.id;
      $.post('update_category_item.py', {action : 'add', item_id: itemid, cat_id : selectedCat},
           function(data){
              if(data.indexOf('Error:') == -1){  // update text
                 $.post('update_category_item.py', { action: 'query', item: itemid},
                   function(data){
                     if (data.indexOf('Error:') == -1){
                       $('#'+itemid+'_cat').html(data + ' &nbsp; ');
                     }
                     else{
                        alert(data);
                     }
                  }, 'text');
             }   // end if no error returned by update_category_item - add
            else{ alert(data);}
           }, 'text');
   });
}

function multiRemoveCategory(){
   var selectedCat = $('#multi_category').val();
   $('.multi:checked').each(function (){
      var itemid = this.id;
      $.post('update_category_item.py', {action : 'remove_item_cat', item: itemid, catid : selectedCat},
           function(data){
              if(data.indexOf('Error:') == -1){  // update text
                 $.post('update_category_item.py', { action: 'query', item: itemid},
                   function(data){
                     if (data.indexOf('Error:') == -1){
                       $('#'+itemid+'_cat').html(data + ' &nbsp; ');
                     }
                     else{
                        alert(data);
                     }
                  }, 'text');
             }   // end if no error returned by update_category_item - add
            else{ alert(data);}
           }, 'text');
   });
}

function multiSetTaxCategory(){
   var selectedTaxCat = $('#multi_tax_category').val();
   $('.multi:checked').each(function (){
      var itemid = this.id;
   $.post('update_tax_categories.py', {action: 'set-item', item_id: itemid, taxcatid: selectedTaxCat},
        function(data){
           if(data.indexOf('Error:') == -1) {   // set text
             $.post('update_tax_categories.py', {action: 'query-item', item_id: itemid},
               function(data){
                  $('#'+itemid+'_tax').html(data + ' &nbsp; ');
               }, 'text');
           }
           else{
               alert(data);
           }
        }, 'text');
   });
}

function updateDistributorItemInfo(itemid, d_id){
   cu = $('#'+itemid+'_'+d_id+'_caseUnits').val();
   cs = $('#'+itemid+'_'+d_id+'_caseSize').val();
   p = $('#'+itemid+'_'+d_id+'_price').val();
   di = $('#'+itemid+'_'+d_id+'_distItemId').val();
   
   $.post('update_distributor_item.py', { action: 'update', item: itemid, distid: d_id, distitemid: di, price: p, casesize: cs, caseunit: cu },
       function () {alert('Update succesful');}, 'text');

}

function updateTaxCategory(id) {
   var selectedTaxCat = $('#'+id+'_taxSelect').val();
   $.post('update_tax_categories.py', {action: 'set-item', item_id: id, taxcatid: selectedTaxCat},
        function(data){
           if(data.indexOf('Error:') == -1) {
               alert('Succesfully updated');
           }
           else{
               alert(data);
           }
        }, 'text');
}

function discontinueItem(ckbox){
   var itemid = parseInt(ckbox.id);
   $.post('update_item.py', { action: 'status', id: itemid, stocked: ckbox.checked},
       function(data){
       }, 'text');
}

$(document).ready(function() {
   $('.th').each(
      function(idx, th) {
        var width = $('#item-stats').children(':first').children().eq(idx).css('width');
        $(th).css('width',width);
      }
   );


   $('.itemname').keypress(function(e) {
       if (e.which == 13) {
            var itemid = parseInt(this.id);
            var newname = this.value;
            name_box = this;
            name_box.disabled = true;
            $(name_box).removeClass('default').removeClass('complete').addClass('submitting');

            $.post('update_item.py', {action:'name', id : itemid, name : newname},
               function(data){
                  name_box.disabled = false;
                  if(data.indexOf('Error:') == -1) {
                     $(name_box).removeClass('default').removeClass('submitting').addClass('complete');      
                  }
                  else { alert(data);}
               }, 'text');

       }
   });

   $('.itembarcode').keypress(function(e) {
       if (e.which == 13) {
            var ids = this.id.split("_");
            var itemid = parseInt(ids[0]);
            var oldbc = ids[1];
            var newbc = this.value;

            bc_box = this;
            bc_box.disabled = true;
            $(bc_box).removeClass('default').removeClass('complete').addClass('submitting');
            $.post('update_item.py', {action:'barcode', id : itemid, newbarcode : newbc, oldbarcode : oldbc},
               function(data){
                  bc_box.disabled = false;
                  if(data.indexOf('Error:') == -1) {
                      bc_box.id = itemid + "_" + newbc + "_" + "bc";                      
                      $(bc_box).removeClass('default').removeClass('submitting').addClass('complete');
                  }
                  else { alert(data);}
               }, 'text');

       }
   });

});
</script>
'''
    idf.print_javascript()
    print '''</head>'''

def print_multi_add():
    print '''<div class="fixed">'''

    print '''<select class="multi_dist" id="multi_dist">'''
    for dist in db.get_distributors():
        print '''<option class="%d_dist_option" value="%d"> %s </option>''' % (dist.get_id(),dist.get_id(),dist)
    print '''</select>'''
    print '''<button type="button" onClick="multiAddDist()">Add Dist</button>'''
    print '''<button type="button" onClick="multiRemoveDist()">Remove Dist</button>'''

    print '''<select class="multi_category" id="multi_category">'''
    for cat in db.get_categories():
        print '''<option class="%d_cat_option" value="%d"> %s </option>''' % (cat.get_id(),cat.get_id(),cat)
    print '''</select>'''
    print '''<button type="button" onClick="multiAddCategory()">Add Category</button>'''
    print '''<button type="button" onClick="multiRemoveCategory()">Remove Category</button>'''
    
    print '''<select class="addTaxCat" id="multi_tax_category">'''
    for taxcat in db.get_tax_categories():
        print '''<option class="%d_taxcat_option" value="%d"> %s </option>''' % (taxcat.get_id(),taxcat.get_id(),taxcat)
    print '''</select>'''
    print '''<button type="button" onClick="multiSetTaxCategory()">Set TaxCat</button>'''

    print '''<button type="button" onClick="uncheckAllMulti()">Uncheck All Items </button>'''
    print '''</div>'''

def main():
    form = cgi.FieldStorage()
    idf.init(form,discontinued=True,distributors=True,categories=True)
    print_headers()

    print '''

<body>'''
    print '''
<div class="key">
         Key:
	      <span class="na"> very negative (produce, etc.) </span>
	      <span class="bad"> slightly negative (counting error?) </span>
	      <span class="out"> out (0 in stock) </span>
              <span class="low"> &lt;14 day supply in stock </span>
         </div>
         <div>Click table headers to sort</div>
         <div>Click distributor to change info there. + or - signs add or remove the distributor respectively.  To change any of the other columns make your modifications and click the word update at the end of the row.</div>
         <div>Note that this currently only supports SINGLE barcodes, and needs to be redone (probably in a similar manner to categories etc) to support multiple </div>
         <div>The M-Edit checkbox allows you to add/remove things to multiple items at once </div>
         <div style="clear: both; height: 15px;"> </div>'''
    print '''</body></html>'''
    
    print_multi_add()
    print '''<form name="options" action="manage_items.py" method="get">'''
    options = idf.print_form()
    print '''<input type="submit" value="Change options" /> </form>'''
    print '''<br> <br>'''
    print '''<table border=0 id="main" class="sortable" cellspacing=0 cellpadding=0>
             <thead class="col-header">
             <th class="th">M-Edit</th>
             <th class="th">Name</th>
             <th class="th">Dist Info</th>
             <th class="th">OP SKU</th>
             <th class="th">Barcodes</th>
             <th class="th">Category</th>
             <th class="th">Tax Category</th>
             <th class="th">Stocked</th>
             </thead><tbody id=\"item-stats\">\n'''
    
    for i,item in enumerate(db.get_items(**options)):
        count = item.get_count()
        item_id = item.get_id()
        day14 = db.get_sales_in_range(item_id,14)

        if count < -10.0:
            print '''<tr id="tr_%d" class="na" title="%d">''' % (item_id,day14)
        elif count < 0.0:
            print '''<tr id="tr_%d" class="bad" title="%d">''' % (item_id,day14)
        elif count < 1.0:
            print '''<tr id="tr_%d" class="out" title="%d">''' % (item_id,day14)
        elif count < day14:
            print '''<tr id="tr_%d" class="low" title="%d">''' % (item_id,day14)
        else:
            print '<tr id="tr_%d" title="%d">' % (item_id,day14)
        
        print '''<div class='div_%d'>''' % (item_id)
        print '''<td> <input class="multi" type="checkbox" id="%d" /></td>''' % (item_id,)
	print '''<td><input type="text" class="itemname" id="%d_name" value="%s" />[%s]''' % (item.get_id(), item.get_name(),item.get_size_str())
        print '''<td id="%d_dist" style='border-left: 1px solid #999; border-right: 1px solid #999; padding-left: 1em;'> %s &nbsp;</td>''' % (item_id, item.get_distributors_str())

	print '''<td style='text-align: center;'> <a href="%s" onclick="window.open(this.href,'_blank'); return false;">%d </a></td>''' % (db.get_item_info_page_link(item_id),item_id)
        barcode = item.get_first_barcode()
        if barcode != None:
            print '''<td> <input size="16" type="text" class="itembarcode" id="%d_%s_bc" value="%s" /> &nbsp;</td>''' % (item_id,barcode.get_barcode(), barcode.get_barcode())
        else:
            print '''<td> <input size="16" type="text" class="itembarcode" id="%d_%s_bc" value="%s" /> &nbsp;</td>''' % (item_id, 'None', 'None')
        print '''<td style='border-left: 1px solid #999; border-right: 1px solid #999;' id='%d_cat'> %s &nbsp;</td>''' % (item_id, item.get_categories_str(), )
        print '''<td style='border-right: 1px solid #999;' id='%d_tax'> %s &nbsp;</td>''' % (item_id, str(item.get_tax_category()), )
        if not item.get_is_discontinued():
            print '''<td><input type="checkbox" id="%d_isStocked" onClick="discontinueItem(this)" checked /> </td>''' % (item_id,)
        else:
            print '''<td><input type="checkbox" id="%d_isStocked"  onClick="discontinueItem(this)"/> </td>''' % (item_id,)                                                                             
        print '''</div>'''
        print '''</tr>\n'''

    print '''</tbody></table>\n'''
    print '''</body></html>'''


if __name__ == "__main__":
    main()
