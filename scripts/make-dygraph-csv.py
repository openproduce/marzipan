#!/usr/bin/env python
# Name: make-dygraph-csv.py
# Author: Patrick McQuighan
# Date: 3/4/2010

import MySQLdb as sql
import datetime, math

output_filename = "/var/www/marzipan/web/site/openproduce.org/wordpress/daily_gross.csv"
olddata_filename = "/var/www/marzipan/web/site/openproduce.org/wordpress/old_gross.csv"

db = sql.connect("localhost", "root", "", "register_tape") #, unix_socket="/opt/lampp/var/mysql/mysql.sock")  # might need to add the argument 'unix_socket=/path/to/socket' if mysql socket is not in '/var/run/mysqld/mysqld.sock'
c = db.cursor()   # cursor is used to execute sql statements on db

today = datetime.date.today()


c.execute('''select  date(s.time_ended), sum(si.total), hour(s.time_ended), count(distinct(s.id)) from sales as s, sale_items as si
                           where si.sale_id = s.id and (s.customer_id != 151 or s.customer_id          
				is null) and s.is_void=0 and si.item_id not in (807, 909) group by date(s.time_ended),hour(s.time_ended)''')


all =  c.fetchall()

outputfile = open(output_filename, "w")
outputfile.write('"Date",Sales,Customers,AvgRing\n')

olddata = open(olddata_filename, "r")
for line in olddata:
    outputfile.write(line)
olddata.close()


# keep track of actual date that should be next and do stuff accordingly            
format = "%Y%m%d"
curdate = datetime.datetime(2009,8,1,1,0,0) # start on 8/1/2009 1:00:00 am 
today = datetime.datetime.today()
index = 0
hour_delta = datetime.timedelta(hours = 1)
daily_sum = 0
daily_custs = 0

while (curdate < today):
    entry = all[index]
    if(entry[0] == None):
        index += 1
        continue
    hour = int(entry[2])
    day = datetime.datetime(entry[0].year, entry[0].month, entry[0].day, hour)
    datestr = (day+datetime.timedelta(hours=-1)).strftime(format)
    if(curdate == day):  # we're at the day/hour we want
        daily_sum += float(entry[1])
        daily_custs += entry[3]
        if ( curdate.hour == 0):  # hit midnight so print the data for the previous day
            outputfile.write(datestr + ',' + str(daily_sum) +  ',' + str(daily_custs) + ',' + str(100*daily_sum/daily_custs) + '\n')
            daily_sum = 0
            daily_custs = 0
        curdate += hour_delta
        index += 1
    elif(curdate < day):   # we skipped the day/hour we want so we need to print 0s
        if(curdate.hour == 0):
            outputfile.write((curdate+datetime.timedelta(hours=-1)).strftime(format) + ','+str(daily_sum)+',' + str(daily_custs) + ',' + str(100*daily_sum/(daily_custs or 1)) + '\n')
            daily_sum = 0
            daily_custs = 0
        curdate += hour_delta
    else:                  # we're earlier than the day/hour we want so skip over this entry
        index += 1
    if (index >= len(all)):   # this is just in case something gets screwed up although i don't think it should ever get here
        break

outputfile.close()
