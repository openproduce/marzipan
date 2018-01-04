#!/usr/bin/env python
# hours.py
# Patrick McQuighan
# Replacement for hours.pl

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
import cgi, datetime

def print_headers():
    print '''Content-type: text/html\n\n
    <!doctype html>
    <html>
    <head>
    <title>Dash board</title>
    <style type="text/css">
        .check { width: 400px; height: 200px; }
        body {font-size: 14px; font-family: verdana;}
        	td,th {border-bottom: 1px solid #999; padding-right: 1em;}
	        .right {text-align: right}
        	.bar {background-color: #9e9;}
        	.total td {border-top: 7px solid #fff; border-bottom: none; background-color: #f99;}
        	.tiny {font-size: 9px; line-height: 9px; padding-left: 1px; padding-right: 1px;}
        	/*.gray {background-color: #ddd;}*/

    </style>
    </head>
    <body>
    '''

def main():
    print_headers()
    print '''Note: this values may be slightly inflated as they are the sum of sales including $ from taxes, however LINK transactions are not charged taxes, but this does not take that into consideration.  Use sales_tax.py if you need precise values eg for reporting sales taxes <br /> <br />'''
    form = cgi.FieldStorage()
    today = datetime.datetime.now()
    
    if 'days' in form:
        days = int(form.getvalue('days'))
        if days == -1:
            start_date = db.FIRST_SALES
        else:
            start_date = today - datetime.timedelta(days=days)
    else:
        start_date = today - datetime.timedelta(days=7)
    start_date += datetime.timedelta(hours=(-start_date.hour+db.DAY_START_HOUR))  # subtract current hour so reporting starts at midnight DAYS days ago.  add db.DAY_START_HOUR because this is the hour we want reporting to start.
    print '''<form name="dates" action="hours.py" method="get">'''
    print '''Show data for:'''
    print '''<select name="days">'''
    print '''<option value="7">Last 7 days</option>'''
    print '''<option value="30">Last 30 days</option>'''
    print '''<option value="-1">Since store open</option>'''
    print '''</select>'''

    print '''<input type="submit" value="Change date range" />'''
    print '''<br /><br />'''
    print "<table border='0' cellspacing='0'>\n"
    print "<tr><th>Date</th><th>Dayname</th><th>Customers</th><th>$/ring</th><th>Gross</th>\n"
    
    hours = [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3]    
    for i in hours:
        print "<th style='padding-left: 1px; padding-right: 1px;' class=''>%d</th>" % (i,)
    print "</tr>\n"
    
    day_infos = db.get_daily_sales(start_date,today)
    for i,key in enumerate(sorted(day_infos.keys())):
        day_info = day_infos[key]
        print '<tr>'
        print '<td>%s</td>' % (day_info.get_date_str(),)
        print '<td>%s</td>' % (day_info.get_dayname(),)

        print '''<td><div class='bar' style='width: %dpx;'>%d</td>''' % (day_info.get_customers_total()/2, day_info.get_customers_total())
        print '''<td><div class='bar' style='width: %dpx;'>%.2f</td>''' % (day_info.get_avg_sales()*10, day_info.get_avg_sales())
        print '''<td><div class='bar' style='width: %dpx;'>%.2f<div style='width: 1px; margin-top: -1em; margin-left: 110px; border-top: 1em solid black'></div></div></td>''' % (day_info.get_gross_sales()/10, day_info.get_gross_sales())

        for h in day_info.get_hourly_sales(hours):
            print '''<td class='tiny' style='background-color: rgb(200,%d,200);'>%d<br/>%.1f<br/><b>$%d</b></td>\n''' % (255 - h.get_gross_sales()*1.3, h.get_customers(), h.get_avg_sales(), h.get_gross_sales())

        if i == 0:  # print arrows on the first row
            print "<td class='tiny' style='border: none;'>&larr;custs<br/>&larr;\$/ring<br/>&larr;gross</td>"

        print '</tr>\n'

    print '''</table>'''
    print '''</body></html>'''

if __name__ == "__main__":
    main()
