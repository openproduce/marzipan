#!/usr/bin/env python
import os, sys, cgi, datetime
import MySQLdb as sql
import numpy as np
os.environ['MPLCONFIGDIR'] = '/tmp'    # any writeable directory is okay
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def make_graph(x_labels, xaxis_label, y_vals,  yaxis_label, title, size=(8,6),dots=80):
    g = plt.figure(figsize=size, dpi=dots)
    ax = g.add_subplot(1,1,1)
    ind = range(len(x_labels))  # ind var spots
    ax.bar(ind,y_vals, align='center')
    ax.set_title(title)
    ax.set_ylabel(yaxis_label)
    ax.set_xlabel(xaxis_label)
    ax.set_xticks(ind)        # set spots for the xticks
    ax.set_xticklabels(x_labels)  # set labels for those ticks
    ax.grid(True)
    g.savefig(sys.stdout, format='png')

start_date = datetime.datetime(2009,8,1,1,0,0)
form = cgi.FieldStorage()
date_input = form.getvalue("date")
month,day,year = date_input.split('/')
date = datetime.datetime(int(year), int(month), int(day), 1,0,0)
nextdate = date + datetime.timedelta(days=1)
hours = [i for i in range(9,24)]   # labels for hours
hours.append(0)
    
if (date < start_date):
    print "Content-type: text/html\n\n<p> Sorry, we don't have hourly data before August 2, 2009 </p>"
else:
    db = sql.connect("localhost", "marzipan", "", "register_tape")
    c = db.cursor()
    # the values being put into the sql query are ints, doing db.escape_string(date.day) causes an error b/c of this
    query = '''select hour(time_ended), sum(si.total) from sales as s, sale_items  as si 
                  where si.sale_id = s.id and (s.customer_id != 151 or s.customer_id is null) and s.is_void = 0 and si.item_id not in 
                    (select id from inventory.items where name like 'tab payment' or name like 'cash back') and (hour(time_ended)>8 and day(time_ended) = %d and 
                      month(time_ended) = %d and year(time_ended) = %d) group by hour(s.time_ended)''' %  (date.day, date.month, date.year)
    

    midnight_query = '''select sum(si.total) from sales as s, sale_items  as si 
                         where si.sale_id = s.id and (s.customer_id != 151 or s.customer_id is null) and s.is_void = 0 and si.item_id not in 
                           (select id from inventory.items where name like  'tab payment' or name like 'cash back') and (hour(time_ended) = 0 and day(time_ended) = %d and
                             month(time_ended) = %d and year(time_ended) = %d)''' %  (nextdate.day, nextdate.month, nextdate.year)
    
    c.execute(query)
    result = c.fetchall()
    if (not result):
        print "<p>Sorry, our graph is not available right now.  Please try again later.</p>"
    else:
        hour = 9
        i = 0
        sales = []
        while(hour < 24):
            if (i<len(result) and result[i][0] == hour):
                sales.append(result[i][1])
                i+=1
            else:
                sales.append(0)
            hour+=1

        midnight_result = c.execute(midnight_query)
        result = c.fetchall()
        if (result[0][0]):
            sales.append(result[0][0])
        else:
            sales.append(0)
        c.close()
        db.close()
        print "Content-Type: image/png\n"
        make_graph(hours,'Hour',sales, 'Sales in $', date_input,(6,4),50)
