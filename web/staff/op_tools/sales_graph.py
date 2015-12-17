#!/usr/bin/env python
# sales_graph.py
# Patrick McQuighan
# Displays a png graph with sales between 9am-11pm, 11pm-midnight, midnight-4am
# The graph is either of gross sales $ or customers

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
import os,sys, datetime
import cgi
os.environ['MPLCONFIGDIR'] = '/tmp'    # any writeable directory is okay
from matplotlib import use
use('Agg')
from matplotlib.pyplot import figure
from matplotlib.font_manager import FontProperties

hour_ranges = [range(8,10),range(10,12),range(12,14),range(14,16),range(16,18),range(18,20),range(20,22),[22,23],[0,1,2,3]]  # The hourly ranges we wish to display. 9am-11pm, 11pm-midnight, midnight-4am
hour_idx_range = range(len(hour_ranges))

labels = ['8am-10am','10am-Noon','Noon-2pm','2pm-4pm','4pm-6pm','6pm-8pm','8pm-10pm','10pm-Midnight','Midnight-4am']
low_threshold = 100  # threshold below which days won't be included in the running avg thing

def make_graph(dates, vals, name):
    fmt = "%m/%d/%y"
    g = figure(figsize=(12,6), dpi=80)
    ax = g.add_subplot(1,1,1)
    ind = range(len(dates))
    xlabels = []
    xticks = []
    cnt = 0
    for d in dates:
        if d.day == 1:
            xlabels.append(d.strftime(fmt))
            xticks.append(cnt)
        cnt+=1

    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)

    # plot & fill the graphs
    colors = ['r','g','b','c','m','y','#888888','#ff6600','#660066']
    for i,v in enumerate(vals):
        ax.plot(ind,v,color=colors[i%len(colors)],label=labels[i])
        if i > 0:
            ax.fill_between(ind,vals[i-1],v,color=colors[i%len(colors)],alpha=.5)
        else:
            ax.fill_between(ind,0,v,color=colors[i%len(colors)],alpha=.5)


    # Make sure we don't have negative values on the y-axis
    ymin,ymax = ax.get_ylim()
    ax.set_ylim(0,ymax)
    
    ax.set_title(name)
    ax.grid(True)
    ax.legend(loc=0,ncol=2,prop=FontProperties(size='small'))
    g.autofmt_xdate()
    g.savefig(sys.stdout, format='png')

def find_index(hour):
    '''Given an hour, finds which range it belongs to'''
    for i,r in enumerate(hour_ranges):
        if hour in r:
            return i

def get_values(value_type):
    '''Returns a list containing 1 list for each hour range.  Each inner list contains a 14-day moving average of 
    values for each day since store opening'''
    hours = [9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3]    
    
    values = [[] for i in hour_idx_range]
    dates = []

    day_infos = db.get_daily_sales()
    window_size = 14   # number of days to use in running avg 
    running_avgs = [[0.0 for w in range(window_size)] for i in hour_idx_range]   # indexed by hour-range-index then 0 to window_size-1
    window_idx = 0
    for i,key in enumerate(sorted(day_infos.keys())):   # go through days in order
        day_info = day_infos[key]
        daily_sales =  day_info.get_gross_sales()

        dates.append(day_info.get_date())
        
        hourly_sales = [0.0 for h in hour_idx_range]

        for hour_info in day_info.get_hourly_sales(hours):
            idx = find_index(hour_info.get_hour())
            if (value_type == 'sales'):
                hourly_sales[idx] += hour_info.get_gross_sales()
            else:
                hourly_sales[idx] += hour_info.get_customers()

        if daily_sales > low_threshold:
            for hour,val in enumerate(hourly_sales):
                running_avgs[hour][window_idx] = val

            num_avgs = float(min(i+1,window_size))
            to_append = map(lambda l: sum(l)/num_avgs, running_avgs)  # avg each of the running_avgs lists to get the value for each hour range for the day
            window_idx = (window_idx + 1) % window_size
        else:
            to_append = hourly_sales

        for idx,val in enumerate(to_append):
            values[idx].append(val)
        
    return dates,values

def accumulate(values):
    '''Accumulates the values between the lists so that we can use a stacked graph'''
    acc = [[] for i in hour_idx_range]
    for j,row in enumerate(zip(*values)):
        for i,v in enumerate(row):
            if i==0:
                acc[i].append(v)
            else:
                acc[i].append(acc[i-1][j] + v)
    return acc

def main():
    print 'Content-Type: image/png\n'
    form = cgi.FieldStorage()
    graph = form.getvalue('graph')
    dates,vals = get_values (graph)
    if graph == 'sales':
        name = 'Gross Sales'
    else:
        name = 'Number of Customers'
    acc = accumulate(vals)
    make_graph(dates,acc, name)

if __name__ == "__main__":
    main()
