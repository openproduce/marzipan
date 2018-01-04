#!/usr/bin/env python
# Computes the following for a given range of dates:
# [Note: There was no further commented text following the above
# comment, as of 17 Dec 2015 when this the copyright notice header
# below was added, but perhaps the above was referring to what gets
# printed by the code.]

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
import datetime


print '''Content-type: text/html\n
<html>
<head>
<style type="text/css">
    * { font-family: sans-serif; font-size: 14px; }
    div.key span {padding: 4px;}
</style>
<title>OP Sales Tax Report</title>
</head>
<body>'''

def print_the_stuff(start_date, end_date):

	normal_report,soft_drink_report = db.get_sales_tax_report(start_date, end_date)
	
	format = '%m/%d/%y'
	
        print '''<hr/>'''
	print '''<h2>Results are for sales between %s and %s</h2> <p />''' % (start_date.strftime(format), end_date.strftime(format))
	
	print '''<b>Normal Sales Tax (ST-1): </b> <br />'''
	print '''Line 1: Total receipts <u>$%.2f</u><br />''' % (normal_report['total'])
	print '''Line 2: Deductions <u>$%.2f</u><br />''' % (normal_report['deductions'])
	print '''&nbsp; 1: General retail tax <u>$%.2f</u><br />''' % (normal_report['general_tax'])
	print '''&nbsp; 2: food retail tax <u>$%.2f</u><br />''' % (normal_report['food_tax'] + normal_report['orphan_tax']) #assume unknown items are food rate
	print '''&nbsp; 9: LINK <u>$%.2f</u><br />''' % (normal_report['link'])
	print '''&nbsp; 15: refunds + transit cards $%.2f + $%.2f = <u>$%.2f</u><br />''' % (normal_report['refunds'], normal_report['transit'], normal_report['refunds'] + normal_report['transit'])
	print '''Line 3 = 1 - 2 = <u>$%.2f</u> <br />''' % (round(normal_report['total'])-round(normal_report['deductions']))
	print '''Line 4a: general sales <u>$%.2f</u><br />''' % (normal_report['general_sales'])
	print '''Line 5a: food sales <u>$%.2f</u><br />''' % (normal_report['food_sales'] + normal_report['orphan_sales'])
	print '''Line 8a: other  <u>$%.2f</u><br />''' % (normal_report['other_sales'])
	line3 = round(normal_report['total'])-round(normal_report['deductions'])
	four_to_eight = round(normal_report['general_sales'])+round(normal_report['other_sales'])+round(normal_report['food_sales'] + round(normal_report['orphan_sales']))
	print '''Line 3 = 4a + 5a + 8a --> %.2f == %.2f? %s<br />'''  % ( line3, four_to_eight, int(line3) == int(four_to_eight))
	
	print '''<p>'''
	print '''<b>Chicago Soft Drink tax:</b><br />'''
	print '''Line 1: Total Chicago soft drinks receipts <u>$%.2f</u><br />''' % (soft_drink_report['total'])
	print '''Line 2: Deductions <u>$%.2f</u><br />''' % (soft_drink_report['deductions'])
	print '''Line 3: Taxable receipts <u>$%.2f</u><br />''' % (soft_drink_report['taxable'])
	print '''Line 4: Tax due <u>$%.2f</u><br />''' % (soft_drink_report['taxdue'])
	print '''Line 5: Discount <u>$%.2f</u><br />''' % (soft_drink_report['discount'])
	print '''Line 6: Payment <u>$%.2f</u> <br />''' % (soft_drink_report['payment'])
	print '''</body>\n</html>'''

print_the_stuff(datetime.datetime (2016,1,1), datetime.datetime (2016,2,1))
print_the_stuff(datetime.datetime (2016,2,1), datetime.datetime (2016,3,1))
print_the_stuff(datetime.datetime (2016,3,1), datetime.datetime (2016,4,1))
print_the_stuff(datetime.datetime (2016,4,1), datetime.datetime (2016,5,1))
print_the_stuff(datetime.datetime (2016,5,1), datetime.datetime (2016,6,1))
print_the_stuff(datetime.datetime (2016,6,1), datetime.datetime (2016,7,1))
print_the_stuff(datetime.datetime (2016,7,1), datetime.datetime (2016,8,1))
print_the_stuff(datetime.datetime (2016,8,1), datetime.datetime (2016,9,1))
print_the_stuff(datetime.datetime (2016,9,1), datetime.datetime (2016,10,1))
print_the_stuff(datetime.datetime (2016,10,1), datetime.datetime (2016,11,1))
print_the_stuff(datetime.datetime (2016,11,1), datetime.datetime (2016,12,1))
print_the_stuff(datetime.datetime (2016,12,1), datetime.datetime (2017,1,1))

print_the_stuff(datetime.datetime (2017,1,1), datetime.datetime (2017,2,1))
print_the_stuff(datetime.datetime (2017,2,1), datetime.datetime (2017,3,1))
print_the_stuff(datetime.datetime (2017,3,1), datetime.datetime (2017,4,1))
print_the_stuff(datetime.datetime (2017,4,1), datetime.datetime (2017,5,1))
print_the_stuff(datetime.datetime (2017,5,1), datetime.datetime (2017,6,1))
print_the_stuff(datetime.datetime (2017,6,1), datetime.datetime (2017,7,1))
print_the_stuff(datetime.datetime (2017,7,1), datetime.datetime (2017,8,1))
print_the_stuff(datetime.datetime (2017,8,1), datetime.datetime (2017,9,1))
print_the_stuff(datetime.datetime (2017,9,1), datetime.datetime (2017,10,1))
print_the_stuff(datetime.datetime (2017,10,1), datetime.datetime (2017,11,1))
print_the_stuff(datetime.datetime (2017,11,1), datetime.datetime (2017,12,1))
print_the_stuff(datetime.datetime (2017,12,1), datetime.datetime (2018,1,1))
