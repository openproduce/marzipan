#!/usr/local/bin/python
#
# Library for making sense of tab histories.
#
# 10 Aug 2010

# This file is part of Marzipan, an open source point-of-sale system.
# Copyright (C) 2010 Open Produce LLC
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

import cStringIO

from db import *


def tab_last_zeroed(tab_changes):
    """Given a list of a customer's TabLog transactions, find when they were last paid up in full."""
    zeroes = [ idx  for (idx,tab_change) in enumerate(tab_changes)
                        if tab_change.new_balance <= 0 ]
    try:
        return zeroes[-1]
    except IndexError:
        return 0

def tab_charged_items(tab_change):
    """Find the sale items that were bought on this tab charge."""
    assert tab_change.is_payment() is False
    session = get_session()
    try:
        s_id = tab_change.find_sale().id
        return session.query(SaleItem).filter_by(sale_id = s_id).all()
    except AttributeError:  # no sale found
        return []

def tab_last_changed(customer):
    session = get_session()
    q = session.query(TabLog).filter_by(customer_id = customer.id)
    q = q.order_by(TabLog.when_logged.desc())
    tc = q.first()
    try:
        return tc.when_logged
    except AttributeError:  # no results found
        return None

def find_customer_by_id(id):
    session = get_session()
    return session.query(Customer).filter_by(id = id).one()

def find_unpaid_tabs(customer_ids, threshold = 3, staleness = datetime.timedelta(days=30)):
    """Find which of the given customers owe nontrivial money on their tabs and
    haven't had any tab activity in a while.
    
    Returns an iterator of (customer, last_activity) pairs."""
    def tab_is_stale(customer, last_activity):
        if customer.balance < threshold:
            return False
        if last_activity is not None  and  (datetime.datetime.now() - last_activity) < staleness:
            return False
        return True
    #
    customers_list = ( find_customer_by_id(c_id)  for c_id in customer_ids )
    L = ( (c, tab_last_changed(c))  for c in customers_list )
    return ( (c, last_activity)  for (c, last_activity) in L
                                if tab_is_stale(c, last_activity) )

def format_tablog(tc):
    d = tc.delta()
    if d >= 0:
        s = "CHARGED"
    else:
        s = "PAID"
    return """%s $%7.2f        ($%.2f -> $%.2f)\n%s""" % (
            s,
            abs(d),
            tc.old_balance,
            tc.new_balance,
            tc.when_logged
        )

def show_tab_history(c_id, return_log=False):
    """Pretty-print tab history.  If return_log is True, return the tab transaction objects as well as the pretty-printed text."""
    ret = cStringIO.StringIO()

    _session = get_session()
    tab_activity = _session.query(TabLog).filter_by(customer_id = c_id).all()
    idx = tab_last_zeroed(tab_activity)
    latest_run = tab_activity[(idx+1):]
#    print >>ret, "Customer %d (%s)\n" % (c_id, find_customer_by_id(c_id).name)
    for tc in latest_run:
        print >>ret, '###  %s' % format_tablog(tc)
        if tc.is_payment() is False:
            for si in tab_charged_items(tc):
                try:
                    si_item_name = si.item.name
                except AttributeError:
                    si_item_name = "<unknown item>"
                print >>ret, "   * $%6.2f        %s" % (si.total, si_item_name)
        print >>ret
    if return_log is True:
        return ret.getvalue(), latest_run
    else:
        return ret.getvalue()
