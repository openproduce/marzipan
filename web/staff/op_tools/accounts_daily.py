#!/usr/bin/env python
# account.py
# Patrick McQuighan
# Replacement for catalog.pl written in Python and using the new database as of 11/2010

import op_db_library as db
import cgi, datetime
import cgitb
cgitb.enable()

def print_results(results,order=None):
    '''order specifies the order we want to print out the columns.  it should be a list of strings eg ['cash','check'] etc
    corresponding to the payment type'''
    for date in sorted(results.keys()):
        row = results[date]
        print '<tr>'
        print '<td><b>%s</b></td>' % (date.strftime('%Y-%m-%d'))
        if order != None:
            for o in order:
                if row.has_key(o):
                    print '<td>%s</td>' % (row[o])
                else:
                    print '<td>0</td>'
        else:
            print '<td>%s</td>' % (row)
        print '</tr>'

def print_body(month,year):
    start = datetime.datetime(year,month,1)
    if month != 12:
        end = datetime.datetime(year,month+1,1)
    else:
        end = datetime.datetime(year+1,1,1)

    sales,payments,cash = db.get_accounts('daily',start,end)
    
    print '''
<table border='1'> <caption>Total Sales</caption>
 <thead>
 <tr>
  <th>Date</th>
  <th>Cash</th>
  <th>Check</th>
  <th>Credit</th>
  <th>Tab</th>
  <th>LINK</th>
  <th>total</th>
 </tr>
</thead>

<tbody>'''
    print_results(sales, ['cash','check','debit/credit','tab','link','total'])
    print '''
</tbody>

</table>
'''
    print '''
<table border='1'> <caption>Tab Payments</caption>
<thead>
 <tr>
  <th>Date</th>
  <th>Cash</th>
  <th>Check</th>
  <th>Credit</th>
  <th>LINK</th>
 </tr>
</thead>

<tbody>'''
    print_results(payments, ['cash','check','debit/credit','link'])
    
    print '''
</tbody>

</table>'''

    print '''
<table border='1'> <caption>Total Cash In (including tab payments)</caption>
<thead>
 <tr>
  <th>Date</th>
  <th>Cash In</th>
 </tr>
</thead>

<tbody>'''
    print_results(cash)
    print '''
</tbody>

</table>'''
    


print 'Content-Type: text/html\n'
print '''<html>
 <head>
    <title>OP Daily Accounts</title>

</head>
 <body>'''
form = cgi.FieldStorage()
if not form.has_key('month') or not form.has_key('year'):
    print 'Error! You must include a year and a month. Please go through <a href="accounts.py"> this tool</a>'
else:
    print_body(int(form.getvalue('month')), int(form.getvalue('year')))

print '</body></html>'
