#!/usr/bin/env python
# make_dinnerrush_sales_csv.py
# Steven Lucy
# This file generates a .csv file which is used to make a dygraphs graph.
# The data outputted are: 
#   Date, Sales between 5pm-9pm, # customers between 5pm-9pm

import op_db_library as db

hours = [17,18,19,20]
outputfilename = 'dinnerrush_sales.csv'
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

