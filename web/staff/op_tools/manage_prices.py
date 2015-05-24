#!/usr/bin/env python
# manage_prices.py
# Patrick McQuighan

import op_db_library as db
import item_display_form as idf
import cgi,sys, datetime
import cgitb
cgitb.enable()

colspan = 13   # number of columns for a given item's row, i.e. doesn't include PriceID or OP Price fields
# NOTE  this value is hardcoded into add_items_js.py
def print_headers():
    print '''Content-Type: text/html\n\n'''
    print '''<html><head>
    <title>Open Produce Price Manager</title>

    <link rel="stylesheet" type="text/css" href="../../tools.css" />
    <script type="text/javascript" src="../../jquery-1.3.2.min.js"></script>\n
    <script type="text/javascript" src="../../sorttable.js"></script>\n
    <script type="text/javascript" src="../../fix_table_headers.js"></script>
<script type="text/javascript">'''
    # The following is just to remove whitespace and &nbsp's from stuff
    print '''
    function trim(str) {
       return str.replace(/^[\s]+/g,'').replace(/[\s]+$/g,'');
    }'''
    # The following array is needed so that the when an item is split it will have the dropdown to change sale units
    print '''units = new Array();'''
    for i,unit in enumerate(db.get_units()):
        print '''units[%d] = '%s';''' % (i, str(unit))

    print '''
    function handlePriceChange(e){
		if (e.which == 13) {
                     var p_id = parseInt(this.id);
                     price_box = this;
                     price_box.disabled = true;
                    $(price_box).removeClass('default').removeClass('complete').addClass('submitting');
                        $.post('update_prices.py', {action: 'price', price_id: p_id, price: this.value},
                           function(data){
                              price_box.disabled = false;
                              if(data.indexOf('Error:') != -1){
                                  alert(data);
                              }
                              else{
                                 updateMargins(p_id);
                                 $(price_box).removeClass('default').removeClass('submitting').addClass('complete');
                              }
                           }, 'text');
		}
        }

   function discontinueItem(ckbox){
      var itemid = parseInt(ckbox.id);
      $.post('update_item.py', { action: 'status', id: itemid, stocked: ckbox.checked},
         function(data){
         }, 'text');
   }
  
    function handleGroupChange(e){
                if (e.which == 13) {
                   var item = parseInt(this.id);
                   var newid = parseInt(this.value);
                   $.post('update_prices.py', {action : 'group', item_id : item, price_id : this.value},
                     function(data){
                       if(data.indexOf('Error:') == -1){
                       // data contains old_price_id, [1] is the number of items with a given price
                         data = data.split(',');    
                         updateRows(item,data,newid);
                       }
                       else{
                         alert(data);
                       }
                       $('#'+item+'_group').val('');
                     }, 'text');
                }

    }

    function handleAmtChange(e){
		if (e.which == 13) {
			var id = parseInt(this.name);
                        $('#'+id+'_in').attr('disabled', 'true');
                        $('#'+id+'_in').removeClass('default').removeClass('complete').addClass('submitting');
                        var delivery_amt = $(this).val();
      		        $('#'+id+'_in').val('');
			$.post('update_item.py', { action: 'delivery', id: id, amt: delivery_amt, dist: $('#'+id+'_dist_in').val() },
			       function(data) {
                                   $('#'+id+'_in').removeAttr('disabled');
                                   if (data.indexOf('Error:') != -1){alert(data);}
                                   else{
                                        $('#'+id+'_in').removeClass('default').removeClass('submitting').addClass('complete');
                                        if (data != ''){
					    $('#'+id+'_amt').html(data);
                                        }
                                        day14 = parseFloat($('#tr_'+id).attr('title'))
                                         
                                    }
				}, 'text');
                         
		}
    }

    function handleDItemChange(e){
        if (e.which == 13) {
           var ids = this.id.split('_');
           var item = parseInt(ids[0]);
           var dist = parseInt(ids[1]);
           var newvalue = this.value;
           ditem_box = this;
           ditem_box.disabled = true;
           $(ditem_box).removeClass('default').removeClass('complete').addClass('submitting');

           $.post('update_distributor_item.py', {action:'update', item : item, distid : dist, distitemid : newvalue},
             function(data){
                 ditem_box.disabled = false;
                 if(data.indexOf('Error:') == -1) {
                    $(ditem_box).removeClass('default').removeClass('submitting').addClass('complete');
                 }
                 else { alert(data);}
             }, 'text');
          }
    }

    function handleCaseSizeChange(e){
                if (e.which == 13) {
                   var ids = this.id.split('_');
                   var item = parseInt(ids[0]);
                   var dist = parseInt(ids[1]);
                   var price = parseInt(ids[2]);
                   var newvalue = parseFloat(this.value);
                   ditem_box = this;
                   ditem_box.disabled = true;
                   $(ditem_box).removeClass('default').removeClass('complete').addClass('submitting');

                   $.post('update_distributor_item.py', {action:'update', item : item, distid : dist, casesize : newvalue},
                      function(data){
                         ditem_box.disabled = false;
                         if(data.indexOf('Error:') == -1) {
                            $(ditem_box).removeClass('default').removeClass('submitting').addClass('complete');
                            updateMargins(price);
                         }
                         else { alert(data);}
                      }, 'text');
            } 
    }

    function handleCaseCostChange(e){
                if (e.which == 13) {
                   var ids = this.id.split('_');
                   var item = parseInt(ids[0]);
                   var dist = parseInt(ids[1]);
                   var price = parseFloat(ids[2]);
                   var newvalue = parseFloat(this.value);
                   ditem_box = this;
                   ditem_box.disabled = true;
                   $(ditem_box).removeClass('default').removeClass('complete').addClass('submitting');

                   $.post('update_distributor_item.py', {action:'update', item : item, distid : dist, price : newvalue},
                      function(data){
                         ditem_box.disabled = false;
                         if(data.indexOf('Error:') == -1) {
                             $(ditem_box).removeClass('default').removeClass('submitting').addClass('complete'); 
                             updateMargins(price);
                         }
                         else { alert(data);}
                      }, 'text');
            }
    }

    // This takes the data list returned from update_prices.py and the new price id
    function updateRows(item, data, newid) {
        if ($('#'+newid+'_table').length == 0){   // price_id row is not currently displayed so make it
           var newrow = '<tr id="'+newid+'_price"><td class="td">'+newid+'</td>';
           newrow += '<td class="td">$<input type="text" class="price" id="'+newid+'_price_input" size="3" value="'+trim(data[2])+'"></input></td>';
           newrow += '<td><select class="saleunit" id="'+newid+'_sale_unit" onChange="setPriceSaleUnit('+newid+')">';
           for (var i=0; i<units.length; i++){
             newrow += '<option value="'+units[i]+'"';
             if (units[i] == trim(data[4])){
                newrow += 'selected';
             }
             newrow+= '>' +units[i] +'</option>';
           }
           newrow += '</select></td>';

           newrow += '<td ''',
    print '''colspan="%d" class="td"> <table id="'+newid+'_table" cellspacing=0 cellpadding=0></table></td></tr>' ''' % (colspan)
    print '''
           $('#main').append(newrow);
           $('.price').keypress(handlePriceChange);
         }
         $('#'+newid+'_table').append($('.'+item+'_tr'));
                        
        updateMargins(newid);

        if (parseInt(data[1]) == 0){
            $('#'+data[0]+'_price').remove();
        }
    }

    function setPriceSaleUnit(priceid){
          var selected = $('#'+priceid+'_sale_unit :selected').text();
          $.post('update_prices.py', {action:'sale_unit', price_id:priceid, unit_name : selected},
            function(data){
               if(data.indexOf('Error:') == -1) {
               }
               else { alert(data);}
            }, 'text');
    }
 
    function updateMargins(price){
        $.post('update_prices.py', {action: 'query', price_id: price},
            function(data){                                 
               if(data.indexOf('Error:') != -1){
                   alert(data);
               }
               else{
                  var rows = data.split("\\n");
                  for(var i=0; i<rows.length; i++){
                      var cols = rows[i].split(',');
                      var tagPrefix = "#" + cols[0] + '_' + cols[1] +'_';
                      $(tagPrefix+'each').text('$'+cols[2]);
                      $(tagPrefix+'margin').text(cols[3]+'%');
                      var margin = parseInt(cols[3]);
                      if(margin <= 20){
                         $(tagPrefix+'margin').attr('class','bad');
                      } else if(margin <= 30) {
                         $(tagPrefix+'margin').attr('class','mid');
                      } else{
                         $(tagPrefix+'margin').attr('class','good');                 
                      }
                   }
               }
            }, 'text');

    }

    function split(item) {
        if (!confirm("Are you sure you want to split item "+item+" from its current price group?")) { return;}
        $.post('update_prices.py', {action : 'split', item_id: item},
          function(data){
            if(data.indexOf('Error:') == -1){
               // data contains old_price_id, [1] is the number of items with a given price
               data = data.split(',');    
               newid = parseInt(data[3]);
               updateRows(item, data, newid);
            }
            else{
              alert(data);
            }
           }, 'text');
    }


    $(document).ready(function() {
        $('.th').each(
          function(idx, th) {
            var width = 0;
            if (idx < 3) {
              width = $('#item-stats').children(':first').children().eq(idx).css('width');
            }
            else {
              // Since we have a table within the first table (at idx 3) we need to get a child from that table 
              width = $('.inner_table:first').children(':first').children().eq(idx-3).css('width');
            }
            $(th).css('width',width);
          }
        );

        $('.ditemid').keypress(handleDItemChange);
        $('.casesize').keypress(handleCaseSizeChange);
        $('.casecost').keypress(handleCaseCostChange);
        $('.group').keypress(handleGroupChange);
	$('.price').keypress(handlePriceChange);
	$('.amt').keypress(handleAmtChange);
 });


</script>
'''
    idf.print_javascript()
    print '''
    </head>'''

def main():
    form = cgi.FieldStorage()
    idf.init(form,discontinued=True,distributors=True,categories=True)
    print_headers()
    print '''
<body>'''
    print '''
         <div>Click table headers to sort</div>
         <div>To change a price, enter the new price in the text field and hit ENTER </div>
         <div>To change an item's price group, enter the new group and hit ENTER </div>
         <div>To split an item from the given group click the 'split' button. It will be given a new price_id </div>
         <div>To log a delivery select the appropriate distributor from the dropdown, type in the number delievered (positive or negative integer) and press ENTER </div>
         <div style="clear: both; height: 15px;"> </div>'''
    print '''<form name="options" action="manage_prices.py" method="get">'''
    options = idf.print_form()
    print '''<input type="submit" value="Change options" /> </form>'''
    print '''<br><br>'''
    print '''<table border=0 id="main" class="sortable" cellspacing=0 cellpadding=0>
             <thead class="col-header">
             <th class="th">Price ID </th>
             <th class="th">OP Price</th>
             <th class="th">SaleUnit</th>
             <th class="th">Name</th>
             <th class="th">SKU</th>
             <th class="th">Count</th>
             <th class="th">Deliv</th>
             <th class="th">Distributor</th>
             <th class="th">D ItemID </th>
             <th class="th">Case Cost</th>
             <th class="th">Case Size</th>
             <th class="th">Case Units</th>
             <th class="th">Each Cost</th>
             <th class="th">Margin</th>
             <th class="th">Change P_ID</th>
             <th class="th">Split</th>
             <th class="th">Stocked</th>
             </thead><tbody id="item-stats">\n'''
    
    cur_price = -1
    cur_item = -1

    units = [(u.get_id(), u.get_name()) for u in db.get_units()]

    for price,item,dist,dist_item in db.get_distributor_items(**options):
        item_id = item.get_id()
        price_id = price.get_id()
        if cur_price != price_id:
            if cur_price != -1:
                # end previous row
                print '</tbody>'
                print '</table></td></tr>'
            print '<tr class="color-row" id="%d_price"><td class="td">%d</td><td class="td">$<input type="text" class="price" id="%d_price_input" size="3" value="%.2f"></input></td>'  % (price_id, price_id, price_id, price.get_unit_cost())
        
            print '''<td class="td"> <select class="saleunit" id="%d_sale_unit" onChange="setPriceSaleUnit(%d)">''' % (price_id,price_id)
            for unit in units:
                print '''<option value="%d"''' % (unit[0],)
                if unit[0] == price.get_sale_unit_id():
                    print ''' selected>'''
                else:
                    print '''>'''
                print unit[1], ''' </option>'''

            print '''</select></td>'''

            print'<td colspan="%d" class="td"><table id="%d_table" cellspacing=0 cellpadding=0>' % (colspan,price_id)
            print '<tbody class="inner_table">'
            cur_price = price_id
        print '<tr class="%d_tr">' % (item_id,)
        
        if cur_item != item_id:
            item_dist_count = item.get_distributor_count()
            print '''<td rowspan='%s' id='%d_td' width='400' style='padding-left: 1em;'> %s </td>''' %  (item_dist_count, item_id, str(item))
            print '''<td rowspan='%s' width='80'> <a href='%s' onclick="window.open(this.href,'_blank'); return false;">%d</a> </td>''' % (item_dist_count,db.get_item_info_page_link(item_id),item_id)
            print '''<td rowspan='%s' width='80' id="%d_amt"> %d </td>''' % (item_dist_count,item_id,item.get_count())
            print '''<td rowspan="%d" width='100'><input class="amt" id="%d_in" name="%d_in" size="2"/>''' % (item_dist_count,item_id, item_id)
            print '''<select id="%d_dist_in" name="%d_dist_in">''' % (item_id, item_id)
            for d in item.get_distributors():
                print '''<option value="%s"> %s </option>''' % (d.get_dist_id(),d.get_distributor())
            print '''</select>'''
            print '''</td>\n'''
        
        print '''<td width="100"> %s </td>''' % (dist,)
        print '''<td width="100"> <input class="ditemid" size="10" value="%s" id="%d_%d_ditemid" /> </td>''' % (dist_item.get_dist_item_id(),item.get_id(), dist.get_id())

        each_cost = dist_item.get_each_cost()
        op_price = item.get_price()
        tax = item.get_tax_value()

        if op_price - tax > 0:
            margin = (1.0 - each_cost/(op_price - tax)) * 100
        else:
            margin = 100

	print '''<td width="100">$<input class="casecost" size="6" value="%.2f" id="%d_%d_%d_casecost" /></td>''' % (dist_item.get_wholesale_price(), item.get_id(), dist.get_id(), price_id)
        print '''<td width="80" ><input class="casesize" size="5" value="%.2f" id="%d_%d_%d_casesize"/> </td>''' % (dist_item.get_case_size(), item.get_id(), dist.get_id(), price_id)
        print '''<td width="80">%s </td>''' % (dist_item.get_case_unit(),)

	print '''<td width="80" id="%d_%d_each">$%.2f </td>''' % (item_id,dist.get_id(),each_cost)
        if margin <= 20:
            print '''<td width="80" class="bad" id="%d_%d_margin"> %.0f%% &nbsp;</td>''' % (item_id,dist.get_id(), margin)
        elif margin <= 30:
            print '''<td width="80" class="mid" id="%d_%d_margin"> %.0f%% &nbsp; </td>''' % (item_id,dist.get_id(), margin)
        else:
            print '''<td width="80" class="good" id="%d_%d_margin"> %.0f%% &nbsp; </td>''' % (item_id,dist.get_id(), margin)

        if cur_item != item_id:
            print '''<td rowspan='%s' width="100"><input class="group" id="%d_group" type="text" size="3"></input></td>''' % (item_dist_count,item_id)
            print '''<td rowspan='%s' width="80"><div onClick="split(%d)">split</div></td>''' % (item_dist_count,item_id)
            if not item.get_is_discontinued():
                print '''<td><input type="checkbox" id="%d_isStocked" onClick="discontinueItem(this)" checked /> </td>''' % (item_id,)
            else:
                print '''<td><input type="checkbox" id="%d_isStocked"  onClick="discontinueItem(this)"/> </td>''' % (item_id,)                                             
            cur_item = item_id
        print '''</tr>\n'''

    print '</table></td></tr>'
    print '''</tbody></table>\n'''
    print '''</body></html>'''


if __name__ == "__main__":
    main()
