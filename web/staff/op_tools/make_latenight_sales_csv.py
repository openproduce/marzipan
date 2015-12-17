#!/usr/bin/env python
# make_latenight_sales_csv.py
# Patrick McQuighan
# This file generates a .csv file which is used to make a dygraphs graph.
# The data outputted are: 
#   Date, Sales between 11pm-4am, # customers between 11pm-4am

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

hours = [0,1,2,3,23]
outputfilename = '../site/latenight_sales.csv'
outputfile = open(outputfilename, 'w')
daily_sales = db.get_daily_sales()
format = "%Y%m%d"
outputfile.write('"Date",Gross $,Customers\n')
for key in sorted(daily_sales.keys()):
    day_info = daily_sales[key]
    date = day_info.get_date().strftime(format)
   
    customers = 0
    gross = 0
    for h in day_info.get_hourly_sales(hours):
        customers += h.get_customers()
        gross += h.get_gross_sales()

    outputfile.write("%s,%.2f,%d\n" % (date,gross,customers))

