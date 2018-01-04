#!/usr/bin/env python
# make_latenight_sales_csv.py
# Patrick McQuighan
# This file generates a .csv file which is used to make a dygraphs graph.
# The data outputted are: 
#   Date, Sales between 11pm-4am, # customers between 11pm-4am

import op_db_library as db

hours = [0,1,2,3,23]
outputfilename = 'latenight_sales.csv'
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

