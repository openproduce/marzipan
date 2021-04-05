#!/usr/bin/env python
# catalog.py
# Patrick McQuighan
# Replacement for catalog.pl written in Python and using the new database as of 11/2010
# Option: use setTimeout to reset textboxes to have the default border after some time (used in item_info.py implemented in make_javascript)

import op_db_library as db

import item_display_form as idf
import cgi
import datetime
import cgitb
cgitb.enable()

spec_date_format = "%A %m/%d/%y"

def print_headers():
    print '''Content-Type: text/html\n\n'''
    print '''<html><head>
    <title>Open Produce Catalog</title>

    <link rel="stylesheet" type="text/css" href="../../common/tools.css" />
    <script type="text/javascript" src="../../common/jquery-1.3.2.min.js"></script>\n
    <script type="text/javascript" src="../../common/sorttable.js"></script>\n
    <script type="text/javascript" src="../../common/fix_table_headers.js"></script>
<script type="text/javascript">
function discontinueItem(ckbox){
   var itemid = parseInt(ckbox.id);
   $.post('update_item.py', { action: 'status', id: itemid, stocked: ckbox.checked},
       function(data){
       }, 'text');
}

$(document).ready(function() {
	$('.count').keypress(function(e) {
		if (e.which == 13) {
 			var id = parseInt(this.id);
                        $('[id^='+id+'_count_]').removeClass('default').removeClass('complete').addClass('submitting');
                        $('[id^='+id+'_count_]').attr('disabled','true');

			$.post('update_item.py', { action: 'count', id: id, count: $(this).val(), exp_date: $('#exp_date').val() },
			       function(data) {
                                        if (data != ''){
                                            data = data.split(',');
					    $('[id^='+id+'_amt_]').html(data[1]);
                                            $('[id^='+id+'_spec_]').html(data[0]);
                                        }
					$('[id^='+id+'_count_]').val('');
                                        day14 = parseFloat($('#tr_'+id).attr('title'))  // using just one is fine here

					if (parseFloat(data[1]) < -10) {
						$('[id^=tr_'+id+'_]').attr('class','na');
					} else if (parseFloat(data[1]) < 0) {
						$('[id^=tr_'+id+'_]').attr('class','bad');
					} else if (parseFloat(data[1]) < 1) {
						$('[id^=tr_'+id+'_]').attr('class','out');
					} else if (parseFloat(data[1]) < day14){
						$('[id^=tr_'+id+'_]').attr('class','low');
					} else {
						$('[id^=tr_'+id+'_]').attr('class','');
                                        }

                                        $('[id^='+id+'_count_]').removeClass('default').removeClass('submitting').addClass('complete');
                                        $('[id^='+id+'_count_]').removeAttr('disabled');
				}, 'text');
		}
	});

        $('.th').each(
          function(idx, th) {
            var width = $('#item-stats').children(':first').children().eq(idx).css('width');
            $(th).css('width',width);
          }
        );
});

</script>
'''
    idf.print_javascript()
    print '''
    </head>'''

def print_dates(days,selected_date):
    today = datetime.datetime.now()
    print '''<select id="exp_date" name="exp_date">'''

    for i in range(days):
        day = today + datetime.timedelta(days=i)
        if day.strftime(spec_date_format) == selected_date.strftime(spec_date_format):
            selected = "selected"
        else:
            selected = ""
        d_string = day.strftime(spec_date_format)
        print '''<option value='%s' %s> %s </option>''' % (d_string, selected, d_string)
    print '''</select>'''

def main():
    form = cgi.FieldStorage()
    idf.init(form,discontinued=True,distributors=True,categories=True)
    print_headers()
    print '''
<body>
<div class="key">
         Key:
	      <span class="na"> very negative (produce, etc.) </span>
	      <span class="bad"> slightly negative (counting error?) </span>
	      <span class="out"> out (0 in stock) </span>
              <span class="low"> &lt;14 day supply in stock </span>
         </div>
         <div>Click table headers to sort</div>
         <div>Click distributor to change</div>
         <div>Type and hit ENTER to change item number or to adjust quantity</div>
         <div>Boxes will be grayed out until the update happens to the database.  If a box doesn't become normal after a few seconds, then likely something is wrong with the database or the server</div>
         <div>The Out in column estimates the number of days of stock left in store.  It uses the average # units sold per day for the last 14 days to get its estimate</div>
         <div>The Spec column shows the estimated stock count for 'Speculate stock for date:' day.  Speculation is based on average # units sold per day for the last 14 days. The default date is for the next Thursday</div>
         <div>The New count field is meant to change an item's count after doing a manual count.  Deliveries should be logged under manage_prices.  Type a new count and press ENTER </div>
         <div style="clear: both; height: 15px;"> </div>'''

    print '''<form name="options" action="catalog.py" method="get">'''
    options = idf.print_form()    # prints out all of the options for item displaying

    print '''Speculate stock for date'''
    if "exp_date" in form:
        speculate_date = datetime.datetime.strptime(form.getvalue("exp_date"), spec_date_format)
        days_to_speculate = (speculate_date - datetime.datetime.now()).days
        print_dates(14, speculate_date)
    else:
        today = datetime.datetime.now()
        days_to_speculate = (6 - today.weekday() + 4) % 7  # weekday goes Monday=0, Sunday=6 so: 6-today = days to next sunday
        print_dates(14, today+datetime.timedelta(days=days_to_speculate))
    print ''' <br /><input type="submit" value="Change options" /> </form>'''
    print '''<br /><br />'''
    print '''<table border=0 class="sortable" cellspacing=2 cellpadding=0>
             <thead class="col-header"><tr>
             <th class="th">dist (case size/units/price)</th>
             <th class="th">d item id</th>
             <th class="th">name</th>
             <th class="th">size</th>
             <th class="th">price</th>
             <th class="th">7d</th>
             <th class="th">14d</th>
             <th class="th">30d</th>
             <th class="th" class="sorttable_numeric">Out in</th>
             <th class="th">Spec</th>
             <th class="th">#stocked</th>
             <th class="th">New count</th>
             <th class="th">OP SKU</th>
             <th class="th">barcodes</th>
             <th class="th">Stocked</th>
             </thead><tbody id="item-stats">\n'''

    distributors = dict([(d.get_id(), d) for d in db.get_distributors()])
    # Selected distributors
    dist_selected = [d.get_id() for d in options['show_distributors']]
    for item in db.get_items(**options):
        # Need to make these floats b/c comparison b/t Decimal and float work strangely
        count = float(item.get_count())
        item_id = item.get_id()
        day7, day14, day30 = db.get_sales_in_multi_range(item_id,7,14,30)
        stock_strings = ['%.2f'%day7,'%.2f'%day14,'%.2f'%day30]
        dist_list = item.get_distributors()
        if options['hide_additional_distributors']:
            dist_list = [d for d in dist_list if d.get_distributor().get_id() in dist_selected]
        dist_count = len(dist_list)

        for i in range(max(1,dist_count)):   # need the max in case the item has no distributors
            row_color = ""
            if count < -10.0:
                row_color = "na"
            elif count < 0.0:
                row_color = "bad"
            elif count < 1.0:
                row_color = "out"
            elif count < day14:
                row_color = "low"
            print '<tr id="tr_%d_%.2f" class="%s">' % (item_id, day14,row_color)

            print '<div class="div_%d">' % (item_id)

            if dist_count == 0:  # don't have any distributors so we just print blanks in first two spots
                print '''<td> - &nbsp; </td> <td> - &nbsp; </td>'''
            else:
                d_i = dist_list[i]
                dist = distributors[d_i.get_dist_id()]
                case_str = '''%.2f''' % d_i.get_case_size()
                price_str = '''$%.2f''' % d_i.get_wholesale_price()
                print '''<td>''',str(dist),'(',case_str,' ',d_i.get_case_unit(),' ',price_str,') </td> <td>',d_i.get_dist_item_id(),' </td>'''

            print '''<td style='padding-left: 1em;'>''',str(item),'</td>'''
            print '''<td>''',item.get_size_str(),'''</td>'''
            print '''<td>''',item.get_price_str(),'''</td>'''
            print '<td>',stock_strings[0],'</td><td>',stock_strings[1],'</td><td>',stock_strings[2],'</td>'
            if count > 0:
                if float(day14) > 0:
                    days_of_stock = float(count) *14.0/ float(day14)
                    print '<td>','%.0f'%days_of_stock,' days</td>'
                else:
                    print '''<td>No sales</td>'''
            else:
                print '''<td>0 days</td>'''

            speculated = count - day14/14*days_to_speculate   # days_to_speculate determined outside of loop
            print '''<td id="%d_spec_%d" class="spec">''' % (item_id,i)
            print '%d'%speculated,'''</td>'''
            print '''<td id="%d_amt_%d" style="border-left: 1px solid #999; padding-left: 1em;">''' % (item_id, i)
            print int(count),'''</td>'''
            print '''<td><input class="count default" id="%d_count_%d" size="3" /></td>''' % (item_id,i)
            print '''<td style='text-align: center;'> <a href="''',db.get_item_info_page_link(item_id),'''" target="_blank">''',str(item_id),'''</a> </td>'''
            print '''<td>''',item.get_barcodes_str(),'''&nbsp;</td>'''
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
