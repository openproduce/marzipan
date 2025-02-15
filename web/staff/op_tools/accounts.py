#!/usr/bin/env python3
# account.py
# Patrick McQuighan
# Replacement for catalog.pl written in Python and using the new database as of 11/2010

import op_db_library as db

def print_results(results,order=None):
    '''order specifies the order we want to print out the columns.  it should be a list of strings eg ['cash','check'] etc
    corresponding to the payment type'''
    for date in sorted(results.keys()):
        row = results[date]
        print('<tr>')
        print('<td><b><a href="accounts_daily.py?year=%d&month=%d">%s</a></b></td>' % (date.year,date.month,date.strftime('%Y-%m')))
        if order != None:
            for o in order:
                if o in row:
                    print('<td>%10.2f</td>' % (row[o]))
                else:
                    print('<td>0</td>')
        else:
            print('<td>%10.2f</td>' % (row))
        print('</tr>')

print('Content-Type: text/html\n')
print('''<html>
 <head>
    <title>OP Monthly Accounts</title>

</head>
 <body>''')

sales,payments,cash,cards = db.get_accounts('monthly')

print('''
<table border='1'> <caption>Total Sales</caption>
 <thead>
 <tr>
  <th>Date</th>
  <th>cash</th>
  <th>check</th>
  <th>credit</th>
  <th>tab</th>
  <th>LINK</th>
<th>manual credit/debit</th>
<th>online</th>
  <th>total</th>
 </tr>
</thead>

<tbody>''')
print_results(sales, ['cash','check','debit/credit','tab','link','manual credit/debit', 'paid online', 'total'])
print('''
</tbody>

</table>
''')

print('''
<table border='1'> <caption>Tab Payments</caption>
<thead>
 <tr>
  <th>Date</th>
  <th>cash</th>
  <th>check</th>
  <th>credit</th>
  <th>LINK</th>
<th>manual credit/debit</th>
<th>online</th>

 </tr>
</thead>

<tbody>''')
print_results(payments, ['cash','check','debit/credit','link', 'manual credit/debit', 'paid online'])

print('''
</tbody>

</table>''')

print('''
<table border='1'> <caption>Total Cash In (including tab payments)</caption>
<thead>
 <tr>
  <th>Date</th>
  <th>Cash In</th>
 </tr>
</thead>

<tbody>''')
print_results(cash)
print('''
</tbody>

</table>''')

print('''
<table border='1'> <caption>Total Cards In (including tab payments)</caption>
<thead>
 <tr>
  <th>Date</th>
  <th>Cards In</th>
 </tr>
</thead>

<tbody>''')
print_results(cards)
print('''
</tbody>

</table>''')


print('</body></html>')
