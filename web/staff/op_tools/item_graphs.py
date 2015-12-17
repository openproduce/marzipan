#!/usr/bin/env python

# item_graphs.py
# 2/2/2011
# Patrick McQuighan

# Prints out an appropriate PNG file containing a graph
# with sales data about a particular item

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

import cgi, os,sys, datetime

os.environ['MPLCONFIGDIR'] = '/tmp'    # any writeable directory is okay
from matplotlib import use
use('Agg')
from matplotlib.pyplot import figure

def make_graph(x_labels, xaxis_label, y_vals, title, legend,size=(8,6),dots=80, grid=True):
    '''y_vals is a list of lists containing the y_values we want to map'''
    g = figure(figsize=size, dpi=dots)
    ax = g.add_subplot(1,1,1)
    ind = range(len(y_vals[0]))  # ind var spots
    for vals in y_vals:
        ax.plot(ind,vals)
    ax.set_title(title)

    ax.set_xlabel(xaxis_label)
    ax.set_xticks(ind)        # set spots for the xticks
    ax.set_xticklabels(x_labels)  # set labels for those ticks
    if grid:
        ax.grid(True)
    ax.legend(legend,loc=0)
    g.autofmt_xdate()
    g.savefig(sys.stdout, format='png')

def price_graph(item,days):
    sales = db.get_recent_item_sales(item,days,False)
    x_labels = []
    prices = []
    cur_unit_cost = -1
    for i,(sale,sale_item) in enumerate(sales):
        if cur_unit_cost == sale_item.get_unit_cost():
            continue
        cur_unit_cost = sale_item.get_unit_cost()
        x_labels.append(sale.get_time_ended().strftime('%m/%d/%y'))
        prices.append(sale_item.get_unit_cost())

    if x_labels == []:
        prices.append(0)
        x_labels.append(datetime.datetime.today().strftime('%m/%d/%y'))
    elif datetime.datetime.today().strftime('%m/%d/%y') not in x_labels:
        prices.append(prices[-1])
        x_labels.append(datetime.datetime.today().strftime('%m/%d/%y'))
    make_graph(x_labels,'Day',[prices], 'Item price of a unit sold in the last %d days'%days,['Unit Price in $'],grid=False)    

def sales_graph(item,days):
    s = db.get_recent_item_sales(item,days,False)

    start_date = datetime.datetime.today() - datetime.timedelta(days=(days-1))
    start_date -= datetime.timedelta(hours=start_date.hour-1, minutes=start_date.minute, seconds=start_date.second, microseconds=start_date.microsecond)  # 1:00 AM 29 days ago, any sale before this time should be recorded as happening days days ago
    x_labels = []     # labels for x_axis
    sale_dollars = []         # sales in dollars for y-axis
    sale_counts = []   # sale in units for y-axis

    s_index = 0        # current sale to look at
    s_len = len(s)    

    for i in range(days):
        cur_date = start_date + datetime.timedelta(days=i)
        if i % 3 == 0:
            # Say cur_date = 1/4/11 1:00:00AM, then any sale occuring BEFORE then should be logged as on 1/3/11
            # Hence we subtract 1 from the date to get the label
            x_labels.append((cur_date-datetime.timedelta(days=1)).strftime('%m/%d/%y'))
        else:  
            # Don't want to clutterthe x-axis so we only print every third
            x_labels.append('')

        if s_index >= s_len:         # We have no more sales to look at so we just add in a bunch of 0s
            sale_dollars.append(0)
            sale_counts.append(0)
            continue

        sale,sale_item = s[s_index]
        day_total = 0
        day_sale_count = 0

        # Add together all sale costs/quantities that ocurred on this day
        while sale.get_time_ended() < cur_date:
            day_total += sale_item.get_cost()
            day_sale_count += sale_item.get_quantity()
            s_index += 1
            if s_index >= s_len:
                break
            sale,sale_item = s[s_index]

        sale_dollars.append(day_total)
        sale_counts.append(day_sale_count)

    make_graph(x_labels,'Day',[sale_dollars,sale_counts], 'Item sales in the last %d days'%days,['Sales in $', 'Units sold'])

form = cgi.FieldStorage()
if 'itemid' in form and 'graph' in form:
    itemid = int(form.getvalue('itemid'))
    graph = form.getvalue('graph')
    item = db.get_item(itemid)
    print "Content-Type: image/png\n"
    if graph == 'sales':
        sales_graph(item,30)
    if graph == 'prices':
        price_graph(item,30)
