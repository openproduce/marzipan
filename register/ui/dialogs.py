#!/usr/bin/env python

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

from __future__ import with_statement
import cStringIO
import datetime
import time
import curses
import curses.panel
import curses.ascii
import decimal
import subprocess
from threading import Thread
import re
import os
import db
import marzipan_io
import cc
import match
import money
from widgets import *
from keys import *
import layout
import tabutil

import sys
sys.path.append("..")
import config
import register_logging
from register_logging import *

class Dialog:
    """set of frames with logic for user interaction."""

    def __init__(self):
        self.frames = []
        self.frame = None
        self.focus_index = 0
        self.done = False
        self.compose_keys = False
        self.slurp_input = False

    def __del__(self):
        for f in self.frames:
            layout.del_frame(f)
            f.layout.panel = None
        curses.panel.update_panels()
        curses.doupdate()

    def add_frame(self, frame):
        self.frame = frame
        self.frames.append(frame)
        return frame

    def _set_focus(self, index):
        """ transfer input focus to index'th frame. """
        for i, f in enumerate(self.frames):
            if index != i:
                f.set_focus(None)
            else:
                f.set_focus_first()
        self.focus_index = index

    def _draw_frames(self):
        for f in self.frames:
            f.show()
        curses.panel.update_panels()
        curses.doupdate()

    def update(self):
        pass

    def _compose_key(self, c):
        keys = {
            ord('1'): curses.KEY_F1,
            ord('2'): curses.KEY_F2,
            ord('3'): curses.KEY_F3,
            ord('4'): curses.KEY_F4,
            ord('5'): curses.KEY_F5,
            ord('6'): curses.KEY_F6,
            ord('7'): curses.KEY_F7,
            ord('8'): curses.KEY_F8,
            ord('9'): curses.KEY_F9,
            ord('11'): curses.KEY_F11,
        }
        if keys.has_key(c):
            return keys[c]
        return None

    def input(self, c):
        if self.slurp_input:
            if c == ord('\n'):
                self.slurp_input = False
        elif self.compose_keys:
            self.compose_keys = False
            c = self._compose_key(c)
            if c is None:
                return False
            curses.ungetch(c)
        elif c == ord('`'):
            self.compose_keys = True
        elif c == ord('%'): # card swipe
            self.slurp_input = True
        elif c == curses.KEY_RESIZE:
            layout.resize()
        else:
            return False
        return True

    def main(self):
        while not self.done:
            self.update()
            if self.done:
                return self
            if self.frames:
                self._draw_frames()
                c = self.frames[self.focus_index].layout.window.getch()
                if not self.input(c):
                    self.frames[self.focus_index].input(c)



class PickClerkDialog(Dialog):
    """pick store clerk from list."""

    def __init__(self, sel_clerk=None):
        Dialog.__init__(self)
        self.s = db.get_session()
        self.result = None
        clerks = self.get_clerks()
        clerk0 = None
        clerk0_name = ''
        if clerks:
            clerk0 = clerks[0]
            clerk0_name = clerks[0].name
        if not sel_clerk:
            sel_clerk = clerk0
        self.add_frame(Frame([
            Label(0, 0, 30, 'Select the current clerk.'),
            Label(1, 0, 30, '(ENTER to pick, ESC to cancel)'),
            ListBox('clerks', 2, 0, 30, 6,
                [(c, c.name) for c in clerks],
                sel=sel_clerk),
            Label(9, 0, 14, 'F6: Manage...', color_id=HELP_COLOR),
        ], layout.Center()))

    def __del__(self):
        Dialog.__del__(self)

    def get_result(self):
        return self.result

    def get_clerks(self):
        return self.s.query(db.Clerk).filter(
            db.Clerk.is_valid == True).all()

    def update_clerks(self):
        self.frame.get('clerks').set_labels(
            [ (c, c.name) for c in self.get_clerks() ])

    def input(self, c):
        if Dialog.input(self, c):
            pass
        elif c == KEY_ESCAPE:
            self.result = None
            self.done = True
        elif c == curses.KEY_F6:
            ManageClerksDialog().main()
            self.update_clerks()
        else:
            return False
        return True

    def update(self):
        clerks = self.frame.get('clerks')
        if clerks.get_hit_enter():
            clerks.reset_hit_enter()
            self.result = clerks.get_selection()
            self.done = True


class ManageClerksDialog(Dialog):
    """add/edit/delete clerks."""

    def __init__(self):
        Dialog.__init__(self)
        self.s = db.get_session()
        clerks = self.get_clerks()
        clerk0 = None
        clerk0_name = ''
        if clerks:
            clerk0 = clerks[0]
            clerk0_name = clerks[0].name
        self.add_frame(Frame([
            Label(0, 0, 33, 'Add, edit or delete clerk names.'),
            Label(1, 0, 33, '(ESC to exit, TAB to switch)'),
            Label(3, 0, 30, 'Clerk name:'),
            TextBox('name', 4, 0, 20, ''),
            Label(6, 0, 30, 'Pick clerk to edit or delete:'),
            ListBox('clerks', 7, 0, 30, 6,
                [(c, c.name) for c in clerks],
                sel=clerk0),
            Label(14, 0, 14, 'F6: Add', color_id=HELP_COLOR),
            Label(14, 15, 14, 'F7: Edit', color_id=HELP_COLOR),
            Label(14, 30, 14, 'F8: Delete', color_id=HELP_COLOR),
        ], layout.Center()))

    def __del__(self):
        Dialog.__del__(self)

    def get_clerks(self):
        return self.s.query(db.Clerk).filter(
            db.Clerk.is_valid == True).all()

    def update_clerks(self):
        self.frame.get('clerks').set_labels(
            [ (c, c.name) for c in self.get_clerks() ])

    def input(self, c):
        if Dialog.input(self, c):
            pass
        elif c == curses.KEY_F6:
            name = self.frame.get('name').get_text()
            if name:
                self.s.add(db.Clerk(name))
                self.s.flush()
                self.frame.get('name').set_text('')
                self.update_clerks()
        elif c == curses.KEY_F7:
            name = self.frame.get('name').get_text()
            clerk = self.frame.get('clerks').get_selection()
            if name and clerk:
                clerk.name = name
                self.s.flush()
                self.frame.get('name').set_text('')
                self.update_clerks()
        elif c == curses.KEY_F8:
            clerk = self.frame.get('clerks').get_selection()
            if clerk:
                clerk.is_valid = False
                self.s.flush()
                self.update_clerks()
                if not self.get_clerks():
                    self.frame.set_focus('name')
        elif c == KEY_ESCAPE:
            self.done = True
        else:
            return False
        pass

    def update(self):
        name = self.frame.get('name')
        clerks = self.frame.get('clerks')
        if clerks.get_hit_enter():
            clerks.reset_hit_enter()
            clerk = clerks.get_selection()
            if clerk:
                name.set_text(clerk.name)

class PaymentDialog(Dialog):
    """accept payment for sale."""

    def __init__(self, sale):
        Dialog.__init__(self)
        self.s = db.get_session()
        self.sale = sale
        self.sale_done = False
        self.card = None
        assert sale is not None
        cust_name = '?'
        if self.sale.customer is not None:
            cust_name = self.sale.customer.name
        total = money.moneyfmt(self.sale.total, curr='$', sep='')
        total_nod = money.moneyfmt(self.sale.total, curr='', sep='')
        self.add_frame(Frame([
            Label(0, 0, 30, 'Enter payment information.'),
            Label(1, 0, 30, '(ESC to cancel, TAB to switch)'),
            Label(2, 0, 30, 'Customer: %s'%(cust_name), name='customer'),
            Label(3, 0, 30, 'Total due: %s'%(total), name='total'),
            Label(4, 0, 30, '', name='alert', color_id=ALERT_COLOR),
            Label(5, 0, 30, 'Payment method:'),

            #second 6 used to be a 5. changed to accomodate link APC
            ListBox('method', 6, 0, 30, 6, 
                [(k, db.PAYMENT[k]) for k in sorted(db.PAYMENT.keys())],
                sel=1),
            Label(12, 0, 30, 'Amount tendered (d.dd):'), 
            TextBox('paid', 13, 0, 30, total_nod, clear_on_insert=True),
            Label(14, 0, 30, 'Change due: $0.00', name='change'),
            Label(16, 0, 14, 'F6: No Rcpt', color_id=HELP_COLOR),
            Label(16, 15, 14, 'F7: Print Rcpt', color_id=HELP_COLOR),
            Label(17, 0, 14, 'F4: E-mail Rcpt', color_id=HELP_COLOR),
#            Label(17, 15, 14, 'F9: Customer...', color_id=HELP_COLOR),
            ], layout.Center()))

    def __del__(self):
        Dialog.__del__(self)

    def get_sale_done(self):
        return self.sale_done

    def _validate(self):
        alert = self.frame.get('alert')
        method = self.frame.get('method').get_selection()
        paid = self.frame.get('paid').get_text()
        is_void = db.PAYMENT[method] == 'void'
        is_tab = db.PAYMENT[method] == 'tab'
        if not paid or not re.match('^-?\d{0,6}(\.\d{0,2})?$', paid):
            alert.set_text('execting amount like 1.25')
            return self.frame.get('paid')
        elif is_void and decimal.Decimal(paid):
            alert.set_text('sale void but paid?')
            return self.frame.get('method')
        elif not is_void and (not paid or not decimal.Decimal(paid)):
            alert.set_text('must be void if not paid')
            return self.frame.get('paid')
        elif not is_void and decimal.Decimal(paid) < self.sale.total and \
             not is_tab and self.sale.total != decimal.Decimal('0.00'):
            alert.set_text('whole total not paid')
            return self.frame.get('paid')
        elif is_tab and not self.sale.customer:
#            alert.set_text('need customer for tab')
            # prompt for customer
            self.sale.customer = _find_customer()
            cust_name = '?'
            if self.sale.customer is not None:
                cust_name = self.sale.customer.name
            self.frame.get('customer').set_text('Customer: %s'%(cust_name))
            return self.frame.get('method')
        elif self.sale.has_tab_payment() and not self.sale.customer:
            alert.set_text('need customer to pay tab')
            return self.frame.get('method')
        elif is_tab and self.sale.has_tab_payment():
            alert.set_text("can't pay tab by tab")
            return self.frame.get('method')
        elif is_tab and self.sale.customer.balance + self.sale.total > \
             self.sale.customer.credit:
            alert.set_text('customer credit exceeded')
            return self.frame.get('method')
        return None

    def _fill(self):
        self.sale.payment = self.frame.get('method').get_selection()
        self.sale.is_void = db.PAYMENT[self.sale.payment] == 'void'
        self.sale.time_ended = datetime.datetime.now()
        if db.PAYMENT[self.sale.payment] == 'tab':
            paid = self.frame.get('paid').get_text()
            self.sale.customer.balance += decimal.Decimal(paid)
        if self.sale.customer and self.sale.has_tab_payment():
            self.sale.customer.balance -= self.sale.tab_payment_amount()
        # TEST ME --- no tax on link
        if db.PAYMENT[self.sale.payment] == 'link':
            pass
        # END TEST ME
        self.done = True
        self.sale_done = True
        self.s.commit()

    def _finish_sale(self, want_receipt=False):
        bad_widget = self._validate()
        if bad_widget is not None:
            self.frame.set_focus(bad_widget)
            return False
        pm_id = self.frame.get('method').get_selection()
        if db.PAYMENT[pm_id] == 'debit/credit':
            return self._pay_credit(want_receipt)

        if db.PAYMENT[pm_id] == 'link':
            return self._pay_link() #TODO make _pay_link()

        self._fill()
        return True

    def _pay_credit(self, want_receipt):
        if not self.card:
            self._get_card()
            if not self.card:
                return False
        paid = decimal.Decimal(self.frame.get('paid').get_text())
        if paid < decimal.Decimal('0'):
            self.frame.get('alert').set_text("can''t credit card account")
            return False
        self.frame.get('alert').set_text('authorizing card...')
        self.frame.show()
        curses.panel.update_panels()
        curses.doupdate()
        try:
            if config.get('cc-processor') == 'ippay':
                (xid, status) = marzipan_io.send_ippay_request(paid, self.card)
            if config.get('cc-processor') == 'tnbci':
                (xid, status) = marzipan_io.send_tnbci_request(paid, self.card)
            if config.get('cc-processor') == 'globalpay':
                (xid, status) = marzipan_io.send_globalpay_request(paid, self.card, self.sale)

        except marzipan_io.CCError, e:
            self.frame.get('alert').set_text(str(e))
            return False
        except ValueError:
            alert = self.frame.get('alert')
            alert.set_text('CC value error')
            return False
        self.frame.get('alert').set_text(status)
        self.frame.show()
        curses.panel.update_panels()
        curses.doupdate()
        
        self.sale.cc_trans = xid
        
        if status.upper() != 'APPROVED':
            if 'DUPLICATE' in status.upper():
                sale = db.get_session().query(db.Sale).filter(db.Sale.cc_name == self.card.account_name).filter( db.Sale.time_started > datetime.datetime.now()-datetime.timedelta(minutes=4)).first()
                if sale:
                    return False
                #but if there's no recorded sale, then we should record it now
                self.sale.cc_trans = 'unknown'
            else:
                return False

        self.sale.cc_name = '' if self.card.account_name == '?'\
                               else self.card.account_name
        self.sale.cc_last4 = self.card.number[-4:]
        self.sale.cc_exp_date = "%02d/%02d" % (self.card.exp_month, self.card.exp_year)
        if self.card.number[0] == '4':
            self.sale.cc_brand = 'VISA'
        else:
            self.sale.cc_brand = 'Mastercard'
        self._fill()
        marzipan_io.print_card_receipt(self.sale, paid, merchant_copy=True)
        TearDialog('merchant receipt').main()
        if want_receipt:
            marzipan_io.print_card_receipt(self.sale, paid, merchant_copy=False)
        #TearDialog('customer receipt').main()
        return True

    def _pay_link(self):
        # stub for now. 
        try:
            self.link
        except:
            self._get_link_info()
            try:
                self.link
            except:
                return False
        #if not self.link:
            #self._get_link_info()
            #if not self.link:
                #return False
        self.sale.cc_trans = self.link
        self.sale.cc_name = 'link customer'
        self._fill()
        paid = self.frame.get('paid')
        paid.set_text( str(self.sale.base_cost) )

        return True

    def _get_card(self, in_swipe=False):
        try:
            cd = CCInfoDialog(in_swipe)
            cd.main()
            self.card = cd.get_result()
        except:
            alert = self.frame.get('alert')
            alert.set_text('CC processing failure')
            return self.frame.get('method')

    def _get_link_info(self):
        ld = LinkDialog(self.sale)
        ld.main()
        self.link = ld.get_result()  

    def input(self, c):
        #all credit cards start with a percent sign 
        if c == ord('%'): 
            cc_method = filter(lambda (k,v): v == 'debit/credit',
                db.PAYMENT.items())[0][0]
            self.frame.get('method').set_selection(cc_method)
            self._get_card(in_swipe=True)
        elif Dialog.input(self, c):
            pass
        elif c == curses.KEY_F6:
            self._finish_sale(want_receipt=False)
        elif c == curses.KEY_F7:
            if self._finish_sale(want_receipt=True):
                marzipan_io.print_receipt(self.sale)
                #TearDialog('sale receipt').main()
        elif c == curses.KEY_F8:
            if self.sale.customer is None:
                self.frame.get('alert').set_text('need customer to e-mail')
            elif not self.sale.customer.email:
                self.frame.get('alert').set_text('customer e-mail not set')
            elif self._finish_sale():
                self.frame.get('alert').set_text('sending e-mail...')
                self.frame.show()
                curses.panel.update_panels()
                curses.doupdate()
                if not marzipan_io.email_receipt(
                    self.sale.customer.email, self.sale):
                    self.frame.get('alert').set_text('error sending e-mail!')
                    self.frame.show()
                    curses.panel.update_panels()
                    curses.doupdate()
                    marzipan_io.print_receipt(self.sale)
                    #TearDialog('sale receipt').main()
                    self.done = True
#        elif c == curses.KEY_F9:
#            self.sale.customer = _find_customer()
#            cust_name = '?'
#            if self.sale.customer is not None:
#                cust_name = self.sale.customer.name
#            self.frame.get('customer').set_text('Customer: %s'%(cust_name))
        elif c == KEY_ESCAPE:
            self.done = True
            self.sale_done = False
        else:
            return False
        return True

    def update(self):
        (method, paid) = [
            self.frame.get(x) for x in [
                'method', 'paid' ]]

        if self.frame.get_focus() != method and\
           db.PAYMENT[method.get_selection()] == 'void':
           paid.set_text('0.00')
        if self.frame.get_focus() == paid:
            paid_text = paid.get_text()
            if paid_text and\
               re.match('^\d{0,6}(\.\d{0,2})?$', paid_text) and\
               paid_text != '.':
                amount = decimal.Decimal(paid_text)
                if amount >= self.sale.total:
                    self.frame.get('change').set_text('Change due: %s'%(
                        money.moneyfmt(amount - self.sale.total,
                                       curr='$', sep='')))
        if method.get_hit_enter():
            method.reset_hit_enter()
            pm_id = method.get_selection()
            if db.PAYMENT[pm_id] == 'debit/credit':
                self._get_card()
            if db.PAYMENT[pm_id] == 'link':
                self._get_link_info()
            if db.PAYMENT[pm_id] == 'tab':
                self.sale.customer = _find_customer()
                cust_name = '?'
                if self.sale.customer is not None:
                    cust_name = self.sale.customer.name
                self.frame.get('customer').set_text('Customer: %s'%(cust_name))



class TearDialog(Dialog):
    """prompt to wait for receipt then tear."""
    def __init__(self, clue):
        Dialog.__init__(self)
        self.add_frame(Frame([
            Label(0, 0, 40, 'Wait for %s, then tear.'%(clue)),
            Label(1, 0, 40, 'Press any key to continue...')
            ], layout.Center()))

    def input(self, c):
        if not Dialog.input(self, c):
            self.done = True
        return True


def check_network():
    url = config.get('tnbci-url')
    try:
        retcode = subprocess.call( ['wget', '-O', '/dev/null', '-q', url] )
        return ( retcode == 0 )
    except:
        return False

class CCInfoDialog(Dialog):
    """enter credit card payment information."""
    def __init__(self, in_swipe=False):
        Dialog.__init__(self)
        self.card = cc.Card()
        self.result = None
        self.in_swipe = in_swipe
        self.magstripe = []
        r_margin = 10
        self.add_frame(Frame([
            Label(0, 0, 40, 'Swipe or key card number.'),
            Label(1, 0, 40, '(ESC to cancel.)'),
            Label(2, 0, 30, '', name='alert', color_id=ALERT_COLOR),
            Label(3, 0, 40, 'Name: ?', name='name'),
            Label(4, 0, r_margin-1, 'Card #:'),
            Label(5, 0, r_margin-1, '(just #s)'),
            TextBox('number', 4, r_margin, 30, ''),
            Label(6, 0, r_margin-1, 'Exp. MM/YY:'),
            TextBox('month', 6, r_margin, 4, ''),
            TextBox('year', 6, r_margin+8, 8, ''),
            Label(8, 0, 15, 'F6: Save Info', color_id=HELP_COLOR),
            ], layout.Center()))

    def get_result(self):
        return self.result

    def _finish_entry(self):
        number = self.frame.get('number')
        month = self.frame.get('month')
        year = self.frame.get('year')
        if not re.match('^\d{16}$', number.get_text()):
            self.frame.get('alert').set_text('expecting 16-digit card #')
            self.frame.set_focus(number)
        elif not re.match('^\d+$', month.get_text()) or\
             int(month.get_text()) < 1 or\
             int(month.get_text()) > 12:
            self.frame.get('alert').set_text('expecting month 1-12')
            self.frame.set_focus(month)
        elif not re.match('^\d+$', year.get_text()):
            self.frame.get('alert').set_text('invalid year')
            self.frame.set_focus(year)
        else:
            self.card.account_name = self.frame.get('name').get_text().strip()
            self.card.number = number.get_text().strip()
            self.card.exp_month = int(month.get_text())
            self.card.exp_year = int(year.get_text())

    def input(self, c):
        if self.in_swipe:
            if c == ord('\n'):
                try:
                    self.card = cc.parse_magstripe(self.magstripe)
                    self.frame.get('name').set_text(self.card.account_name)
                    self.frame.get('number').set_text(self.card.number)
                    self.frame.get('month').set_text("%02d"%(self.card.exp_month))
                    self.frame.get('year').set_text("%02d"%(self.card.exp_year))
                except cc.BadSwipeError, e:
                    self.frame.get('alert').set_text(str(e))
                self.in_swipe = False
            self.magstripe.append(c)
        elif c == ord('%') and not self.in_swipe:
            self.in_swipe = True
        elif Dialog.input(self, c):
            pass
        elif c == curses.KEY_F6:
            self._finish_entry()
            self.result = self.card
            self.done = True
        elif c == KEY_ESCAPE:
            self.result = None
            self.done = True
        else:
            return False
        return True


class LinkDialog(Dialog):
    """enter link card transaction number."""
    def __init__(self, sale):
        Dialog.__init__(self)
        self.sale = sale
        self.link = None
        self.result = None
        r_margin = 10
        self.add_frame(Frame([
            Label(0, 0, 40, 'Please enter transaction ID.'),
            Label(1, 0, 40, '(ESC to cancel.)'),
            Label(2, 0, 30, '', name='alert', color_id=ALERT_COLOR),
            Label(3, 0, 30, "Total (no tax): %s" % self.sale.base_cost ),
            Label(4, 0, 40, 'Approval Code:', name='name'),
            TextBox('number', 4, r_margin, 30, ''),
            Label(6, 0, 15, 'F6: Save Info', color_id=HELP_COLOR),
            ], layout.Center()))

    def get_result(self):
        return self.result

    def _finish_entry(self):
        number = self.frame.get('number')
        self.link = number

    def input(self, c):
        if Dialog.input(self, c):
            pass
        elif c == curses.KEY_F6 or c == KEY_RETURN:
            self._finish_entry()
            self.result = self.link
            self.done = True

        elif c == KEY_ESCAPE:
            self.result = None
            self.done = True
        else:
            return False
        return True


def _get_units(s):
    units = s.query(db.SaleUnit).all()
    unit0 = None
    unit0_name = ''
    if units:
        unit0 = units[0]
        unit0_name = units[0].name
    return (unit0, unit0_name, units)


class CustomerAddEditDialog(Dialog):
    """add/edit customer information."""
    def __init__(self, customer=None, name=""):
        this_logger.debug("trying to display dialog")
        Dialog.__init__(self)
        self.s = db.get_session()
        postal = ['','','','']
        if customer is None:
            self.adding_customer = True
            customer = db.Customer()
            customer.name = name
            customer.code = db.new_customer_code()
        else:
            self.adding_customer = False
            postal = customer.postal.split('\n', 4)
        self.customer = customer
        this_logger.debug("found customer")
        r_margin = 10
        try:
           self.add_frame(Frame([
               Label(0, 0, 40, 'Edit customer information.'),
               Label(1, 0, 40, '(ESC to cancel, UP/DOWN/TAB to switch.)'),
               Label(2, 0, 40, '', name='alert', color_id=ALERT_COLOR),
               Label(3, 0, r_margin-1, 'Account#:'),
               Label(3, r_margin, 40, customer.code, name='id'),
               Label(4, 0, r_margin-1, 'Name:'),
               TextBox('name', 4, r_margin, 40, customer.name),
               Label(5, 0, r_margin-1, 'E-mail:'),
               TextBox('email', 5, r_margin, 40, customer.email),
               Label(6, 0, r_margin-1, 'Telephone:'),
               TextBox('tel', 6, r_margin, 40, customer.tel),
               Label(7, 0, r_margin-1, 'Postal:'),
               TextBox('postal_1', 7, r_margin, 40, postal[0]),
               TextBox('postal_2', 8, r_margin, 40, postal[1]),
               TextBox('postal_3', 9, r_margin, 40, postal[2]),
               TextBox('postal_4', 10, r_margin, 40, postal[3]),
               Label(11, 0, r_margin-1, 'Limit:'),
               TextBox('credit', 11, r_margin, 40, str(customer.credit)),
               Label(12, 0, r_margin-1, 'Balance:'),
               Label(12, r_margin, 40, str(customer.balance)),
#               TextBox('balance', 12, r_margin, 40, str(customer.balance)),
               Label(14, 0, 14, 'F6: Save', color_id=HELP_COLOR),
               Label(14, 15, 14, 'F7: Print card', color_id=HELP_COLOR),
               Label(14, 30, 18, 'F9: Tab history', color_id=HELP_COLOR),
               ], layout.Center()))
        except IndexError:
            import sys
            print >>sys.stderr, len(postal)
            print >>sys.stderr, postal
            raise

    def __del__(self):
        Dialog.__del__(self)

    def _validate(self):
        name = self.frame.get('name').get_text()
        email = self.frame.get('email').get_text()
        tel = self.frame.get('tel').get_text()
#        balance = self.frame.get('balance').get_text()
        credit = self.frame.get('credit').get_text()
        alert = self.frame.get('alert')
        if not re.match('\S+', name):
            alert.set_text('expect name to be non-empty')
            return self.frame.get('name')
        elif not re.match('^[-\w\.%+]+@([-\w]+\.?)+$|^$', email):
            alert.set_text('expect e-mail like words@words')
            return self.frame.get('email')
        elif not re.match('^[-\d+ ]*$', tel):
            alert.set_text('only expect digits, -, + in tel')
            return self.frame.get('tel')
        elif not re.match('^\d{0,6}(\.\d{0,2})?$', credit):
            alert.set_text('expect credit like dddddd.dd')
            return self.frame.get('credit')
        # elif not re.match('^[-+]?\d{0,6}(\.\d{0,2})?$', balance):
        #     alert.set_text('expect balance like [-+]dddddd.dd')
        #     return self.frame.get('balance')
        return None

    def _fill(self):
        self.customer.name = self.frame.get('name').get_text()
        self.customer.email = self.frame.get('email').get_text()
        self.customer.tel = self.frame.get('tel').get_text()
        self.customer.postal = '\n'.join(
            [self.frame.get(x).get_text() for x in [
                'postal_1','postal_2','postal_3','postal_4']])
#        self.customer.balance = decimal.Decimal(
#            self.frame.get('balance').get_text())
        self.customer.credit = decimal.Decimal(
            self.frame.get('credit').get_text())

    def _fill_or_focus_bad_widget(self):
        bad_widget = self._validate()
        if bad_widget is not None:
            self.frame.set_focus(bad_widget)
            return True
        self._fill()
        return False

    def input(self, c):
        if Dialog.input(self, c):
            pass
        elif c == curses.KEY_F6:
            if not self._fill_or_focus_bad_widget():
                if self.adding_customer:
                    self.s.add(self.customer)
                self.s.commit()
                self.done = True
        elif c == curses.KEY_F7:
            if not self._fill_or_focus_bad_widget():
                marzipan_io.print_customer_card(self.customer)
                TearDialog('customer code').main()
        elif c == curses.KEY_F9:
            TabHistoryDialog(self.customer.id).main()
#            TabHistoryProcessingDialog(self.customer.id).main()
#            self.clear()
#            raise KeyboardInterrupt     # force a redraw!
        elif c == KEY_ESCAPE:
            self.done = True
        else:
            return False
        return True

class ConfirmDeletionDialog(Dialog):
    """Really delete?  For use in SearchDialog.  At this point, I think it only still affects the CustomerSearchDialog."""
    def __init__(self):
        Dialog.__init__(self)
        self.done = False
        self.result = False
        self.add_frame( Frame( [
                Label(0, 0, 40, "Really delete?"),
                Label(1, 0, 20, "N: No", color_id=HELP_COLOR),
                Label(1, 21, 20, "Y: Yes", color_id=HELP_COLOR),
            ], layout.Center() ) )

    def __del__(self):
        self._draw_frames()
        Dialog.__del__(self)

    def get_result(self):
        return self.result

    def input(self, c):
        if c == ord('y') or c == ord('Y'):
            self.result = True
            self.done = True
        elif c == ord('n') or c == ord('N') or c == KEY_ESCAPE:
            self.result = False
            self.done = True
        else:
            return False
        return True


class SearchDialog(Dialog):
    """incremental search for database object using textbox contents
       to filter result list.  include buttons to add/edit/delete or
       accept ('ok') search result."""

    def __init__(self, obj_name, has_cancel, layout, search="", editable=True):
        Dialog.__init__(self)
        self.s = db.get_session()
        self.result = None
        self.search_edited = False
        self.has_cancel = has_cancel
        self.make_index()
        self.find_match_set(search)
        widgets = [ Label(0, 0, 40, 'Search for %s.'%(obj_name)) ]
        h = 0
        if self.has_cancel:
            widgets.append(Label(1, 0, 40, '(ENTER to accept, ESC to cancel.)'))
            h = 2
        widgets.extend([
            #Label(h+1, 0, 10, 'Look for:'),
            #Label(h+3, 0, 10, 'Matches:'),
            Searcher('search', h+1, 0, 50, 5, self.get_labels()),
            ])
        if editable is True:
            widgets.extend([
                Label(h+9, 0, 14,  'F6: Add...', color_id=HELP_COLOR),
                Label(h+9, 15, 14, 'F7: Edit...', color_id=HELP_COLOR),
                Label(h+9, 30, 14, 'F8: Delete', color_id=HELP_COLOR),
                ])
        self.add_frame(Frame(widgets, layout))

    def __del__(self):
        Dialog.__del__(self)

    def get_result(self):
        return self.result

    def get_selection(self):
        return self.frame.get('search').get_selection()

    def get_labels(self):
        return [(o, o.name) for o in self.match_set]

    def make_index(self):
        pass

    def find_match_set(self, search):
        self.match_set = []

    def clear(self):
        search = self.frame.get('search')
        self.make_index()
        search.set_text('')
        self.find_match_set('')
        self.frame.set_focus(search)

    def add_edit(self, edit):
        pass

    def notify(self, c):
        search = self.frame.get('search')
        if self.frame.get_focus() == search and\
           c != curses.KEY_UP and c != curses.KEY_DOWN and\
           c != KEY_TAB and c != curses.KEY_ENTER and\
           c != KEY_RETURN:
            self.search_edited = True

    def input(self, c):
        if Dialog.input(self, c):
            pass
        elif c == curses.KEY_F6:
            self.add_edit(False)
            self.clear()
        elif c == curses.KEY_F7:
            this_logger.debug("looking for the add/edit customer dialog")
            self.add_edit(True)
            this_logger.debug("went thru the add/edit customer dialog")
            self.clear()
        elif c == curses.KEY_F8:
            db_obj = self.get_selection()
            if db_obj is not None:
                cd = ConfirmDeletionDialog()
                cd.main()
                if cd.get_result() is True:
                    self.s.delete(db_obj)
                    self.s.commit()
            self.clear()
        elif c == KEY_ESCAPE and self.has_cancel:
            self.result = None
            self.done = True
        else:
            self.notify(c)
            return False
        return True

    def update(self):
        search = self.frame.get('search')
        if self.search_edited:
            self.find_match_set(search.get_text())
            self.search_edited = False
        if search.get_hit_enter():
            search.reset_hit_enter()
            if self.match_set and len(search.get_text()) > 0:
                search.set_text(self.match_set[0].name)
#                self.s.commit()
                self.result = self.get_selection()
                self.done = True
            return


class CustomerSearchDialog(SearchDialog):
    """find customers."""
    def __init__(self, layout, search=""):
        SearchDialog.__init__(self, 'customer', True, layout)

    def __del__(self):
        SearchDialog.__del__(self)

    def make_index(self):
        self.customers = self.s.query(db.Customer).all()
        self.codes = {}
        self.phones = {}
        self.emails = {}
        self.names = match.Index()
        for cust in self.customers:
            self.codes[cust.code] = cust
            ph_digs = re.sub('[^\d]', '', cust.tel)
            if ph_digs:
                self.phones[ph_digs] = cust
            if cust.email:
                self.emails[cust.email] = cust
            self.names.add_item(cust.name, cust)

    def find_match_set(self, search_text):
        self.match_set = []
        if search_text == "":
            self.match_set = self.customers
        else:
            digs = re.sub('[^\d]', '', search_text)
            # no check digit in db
            code_digs = digs[:12] if digs else ''
            ids = {}
            for k in self.codes.keys():
                if code_digs and k.startswith(code_digs):
                    cust = self.codes[k]
                    if not ids.has_key(cust.id):
                        self.match_set.append(cust)
                        ids[cust.id] = True
            for k in self.emails.keys():
                if search_text and k.startswith(search_text):
                    cust = self.emails[k]
                    if not ids.has_key(cust.id):
                        self.match_set.append(cust)
                        ids[cust.id] = True
            for k in self.phones.keys():
                if digs and k.startswith(digs):
                    cust = self.phones[k]
                    if not ids.has_key(cust.id):
                        self.match_set.append(cust)
                        ids[cust.id] = True
            self.match_set.extend(filter(
                lambda x: not ids.has_key(x.id),
                self.names.match(search_text)))
        if self.frame:
            self.frame.get('search').set_labels(self.get_labels())

    def add_edit(self, edit):
        this_logger.debug("in the add_edit....")
        cust = None
        if edit:
            this_logger.debug("looking for edit...")
            cust = self.get_selection()
        this_logger.debug("should be pulling up the dialog...")
        CustomerAddEditDialog(cust, self.frame.get('search').get_text()).main()

def _find_customer():
    cd = CustomerSearchDialog(layout.Center())
    cd.main()
    return cd.get_result()

all_items = [ ]
all_barcodes = [ ]
all_plus = { }
all_names = match.Index()
class ItemSearchDialog(SearchDialog):
    """find items."""

    def __init__(self, layout, has_cancel=False, search=""):
        SearchDialog.__init__(self, 'item', has_cancel, layout, search, editable=False)

    def __del__(self):
        SearchDialog.__del__(self)

    def make_index(self):
#        self.items = self.s.query(db.Item).filter(db.item_filter).all()
#        self.barcodes = list(self.s.query(db.BarcodeItem).join(db.Item).filter(db.item_filter))
#        self.plus = {}
#        self.names = match.Index()
        self.items = all_items
        self.barcodes = all_barcodes
        self.names = all_names
        self.plus = all_plus

    def find_match_set(self, search_text):
        self.match_set = []
        if search_text == "":
            self.match_set = self.items
        else:
            digs = re.sub('[^\d]', '', search_text)
            ids = {}
            if digs:
                for k in self.barcodes:
                    if k.barcode.startswith(digs):
                        item = k.item
                        if not ids.has_key(item.id):
                            self.match_set.append(item)
                            ids[item.id] = True
                for k in self.plus.keys():
                    if k.startswith(digs):
                        item = self.plus[k]
                        if not ids.has_key(item.id):
                            self.match_set.append(self.plus[k])
                            ids[item.id] = True
            self.match_set.extend(filter(
                lambda x: x.id not in ids,
                self.names.match(search_text)))
        if self.frame:
            self.frame.get('search').set_labels(self.get_labels())

    def get_labels(self):
        def size_unit(i):
            if i.size_unit.name != 'each' and i.size_unit.name != 'count':
                return ' [%.1f %s]'%(i.size, i.size_unit)
            return ''
        return [(i, '%s%s'%(i.name, size_unit(i)))
                for i in self.match_set]

    def input(self, c):
        """Override the default SearchDialog.input(), because the POS can't modify Items any more."""
        if Dialog.input(self, c):
            pass
        elif c == KEY_ESCAPE and self.has_cancel:
            self.result = None
            self.done = True
        elif c == curses.KEY_F10:
            d = ItemInfoDialog(self.get_selection())
            d.main()
        else:
            self.notify(c)
            return False
        return True

    def update(self):
        if self.barcode_match():
#            self.s.commit()		# I hope...
            self.result = self.get_selection()
            self.done = True
        elif not self.done:
            SearchDialog.update(self)

    def barcode_match(self):
        search = self.frame.get('search')
        search_text = search.get_text()
        if search_text and re.match('^\d{6,}$', search_text) and\
           search.get_hit_enter() and len(self.match_set) == 1:
            return True
        return False

    def add_edit(self, edit):
        item = None
        if edit:
            item = self.get_selection()
        ItemAddEditDialog(item, self.frame.get('search').get_text()).main()


_current_clerk = None # clerk is persistent across sales

class SaleDialog(Dialog):
    """sell people stuff; the main UI."""
    ITEM_LIST_WIDTH=52
    DEFAULT_TAX=decimal.Decimal('.0200')

    MEASURE_FRAME=0
    SEARCH_FRAME=1
    STATUS_FRAME=2
    ITEMS_FRAME=3
    TOTAL_FRAME=4

    def __init__(self):
        Dialog.__init__(self)
        self.s = db.get_session()
        self.barcode_matched = False
        self.measure = self.add_frame(Frame([
            Label(0, 0, 12, "Quantity"),
            BigNumberBox('qty', 1, 0, 5, "1", clear_on_insert=True),
            Label(6, 0, 12, "Cost", name="unit"),
            BigNumberBox('cost', 7, 0, 5, "0.00", clear_on_insert=True),
            ], layout.Fixed(0, 0), border=False))
        self.status = self.add_frame(Frame([
            Label(0, 0, 14,  "F1: Clerk", color_id=HELP_COLOR),
            Label(0, 15, 14, "F2: Customer", color_id=HELP_COLOR),
            Label(0, 30, 14, "F3: Sale", color_id=HELP_COLOR),
            Label(0, 45, 14, "F4: Reprint Receipt", color_id=HELP_COLOR),
            Label(0, 60, 14, "F5: Pay", color_id=HELP_COLOR),
            Label(0, 75, 14, "F9: Review", color_id=HELP_COLOR),
            ], layout.BottomEdge(0), border=False))
        self.total = self.add_frame(Frame([
            Label(0, 0, 20, 'Clerk: ?', name='clerk'),
            Label(1, 0, 20, 'Customer: ?', name='customer'),
            Label(2, 0, 20, 'Tab: ?', name='tab'),
            Label(3, 0, 20, '', name='clock'),
            Label(4, 0, 20, 'Items: 0', name='nr_items'),
            Label(5, 0, 20, 'Taxless total: 0', name='taxless'),
            Label(6, 0, 20, 'Total'),
            BigNumberBox('total', 6, 0, 5, '0.00'),
            ], layout.BottomEdge(1, 2), border=False))
        self.total.layout.panel.bottom()
        curses.panel.update_panels()
        self.reindex()
        self._make_search()
        self.search.frame.layout.pack()
        self.items = self.add_frame(Frame([
            ListBox('items', 0, 0,
                layout.columns-self.total.layout.width-8,
                (layout.lines-self.search.frame.layout.height-2)/2,
                [], label_height=2),
            ],
            layout.FillRightDown(self.total.layout.width+4,
                                 self.search.frame.height,
                                 fill_to_bottom=True),
            border=False))
        self.frames = [
            self.measure,
            self.search.frame,
            self.status,
            self.items,
            self.total
        ]
        self._reset()

    def __del__(self):
        Dialog.__del__(self)

    def _reset(self):
        self.sale_items = []
        self.sale = db.Sale(_current_clerk, None)
        self.item_to_buy = None
        self.measure.get('qty').set_text('1')
        self.measure.get('cost').set_text('0.00')
        self.search.frame.get('search').set_text('')
        self.items.get('items').set_labels([])
        self.total.get('total').set_text('0.00')
        self.total.get('customer').set_text('Customer: ?')
        self.total.get('tab').set_text('Tab: ?')
        self.total.get('nr_items').set_text('Items: 0')
        self.total.get('taxless').set_text('Taxless total: 0')
        self._set_focus(SaleDialog.SEARCH_FRAME)

    def _make_item_list_labels(self):
        labels = []
        # "1.05 apples - golden delicious"
        # "$4.99 ($1.59/lb)"),
        for si in self.sale_items:
            name = 'other/grocery'
            qty = si.quantity
            unit = ''
            unit_cost = money.moneyfmt(si.unit_cost, curr='$', sep='')
#            tax = ''
            total = money.moneyfmt(si.total, curr='$', sep='')
            if si.item:
                name = si.item.name
                unit = ''.join(['/',si.item.price.sale_unit.name])
#                tax = str(si.item.price.tax)
            s = "%s x %s [%.2f %s]\n%5s (%s%s)"%(qty, name, si.item.size, si.item.size_unit, total, unit_cost, unit)
            labels.append((si, s))
        item_list = self.items.get('items')
        item_list.set_labels(labels)
        item_list.scroll.end()

    def _update_total(self, change):
        self.sale.total += change
        self.total.get('total').set_text(
            money.moneyfmt(self.sale.total, curr='', sep=''))
        marzipan_io.write_cui_pipe("total %s\n"%(self.sale.total))
        self.total.get('nr_items').set_text( "Items: %d" % len(self.sale_items) )
        self.total.get('taxless').set_text(
            "Taxless total: %s" % money.moneyfmt( decimal.Decimal(sum(si.cost  for si in self.sale_items)) , curr='', sep=''))

    def _buy(self):
        qty = decimal.Decimal(self.measure.get('qty').get_text())
        unit_cost = decimal.Decimal(self.measure.get('cost').get_text())
        tax_frac = decimal.Decimal('.0000')
        is_tax_flat = False
        if self.item_to_buy is not None:
            tax_frac = self.item_to_buy.tax_rate
            is_tax_flat = self.item_to_buy.price.is_tax_flat
        (cost, tax, total) = money.cost(qty, unit_cost,
                                        tax_frac, is_tax_flat)
        #self.s.add(db.SaleItem(self.sale, self.item_to_buy,
        #    qty, unit_cost, cost, tax, total))
        #self.s.flush()
        #self.s.commit()
        self.sale_items.append(db.SaleItem(self.sale, self.item_to_buy,
            qty, unit_cost, cost, tax, total))
        self._update_total(total)
        self._make_item_list_labels()
        self.measure.get('qty').set_text('1')

    def update(self):
        qty = self.measure.get('qty')
        cost = self.measure.get('cost')
        if (qty.get_hit_enter() and cost.get_text()) or\
           cost.get_hit_enter() or self.barcode_matched:
            self.barcode_matched = False
            cost.reset_hit_enter()
            qty.reset_hit_enter()
            qty_text = qty.get_text()
            amt = decimal.Decimal('1')
            try:
                amt = decimal.Decimal(qty_text)
            except:
                qty.set_text('1')
                self.measure.set_focus(qty)
                return

            if qty_text and amt < decimal.Decimal('1000'):
                self._buy()
                self.search.frame.get('search').set_text('')
                self._set_focus(SaleDialog.SEARCH_FRAME)
            else:
               qty.set_text('1')
               self.measure.set_focus(qty)

    def _get_clerk(self):
        global _current_clerk
        cd = PickClerkDialog(_current_clerk)
        cd.main()
        _current_clerk = cd.get_result()
        if _current_clerk is not None:
            self.total.get('clerk').set_text('Clerk: '+_current_clerk.name)
        else:
            self.total.get('clerk').set_text('Clerk: ?')
        self.sale.clerk = _current_clerk

    def _get_customer(self):
        self.sale.customer = _find_customer()
        if self.sale.customer is not None:
            self.total.get('customer').set_text('Customer: %s'%(
                self.sale.customer.name))
            self.total.get('tab').set_text( 'Tab: %.2f' % (
                self.sale.customer.balance) )
        else:
            self.total.get('customer').set_text('Customer: ?')
            self.total.get('tab').set_text('Tab: ?')

    def _pay(self):
        self.sale.items = self.sale_items
        pd = PaymentDialog(self.sale)
        pd.main()

        if pd.get_sale_done():
            self.s.add(self.sale)
            for i in self.sale.items:
                self.s.add(i)
            self.s.commit()
        if pd.get_sale_done():
            self.reindex()
            self._reset()
            marzipan_io.write_cui_pipe("paid\n")

    def _del_item(self, items_list, si):
        self._update_total(-si.total)
        self.sale_items.remove(si)
#        try:
#            self.sale.items.remove(si)
#        except ValueError:
#            pass
        items_list.delete_label(si)
        self.measure.get('cost').set_text('0.00')
        self.measure.get('qty').set_text('1')
        self.total.get('nr_items').set_text( "Items: %d" % len(self.sale_items) )
        self.total.get('taxless').set_text(
            "Taxless total: %s" % money.moneyfmt( decimal.Decimal(sum(si.cost  for si in self.sale_items))  , curr='', sep=''))
        #self.s.delete(si)
        #self.s.flush()
        #self.s.commit()

    def input(self, c):
        if Dialog.input(self, c):
            return True
        in_items_frame = self.focus_index == SaleDialog.ITEMS_FRAME
        in_measure_frame = self.focus_index == SaleDialog.MEASURE_FRAME
        if c == curses.KEY_F1:
            self._get_clerk()
        elif c == curses.KEY_F2:
            self._get_customer()
        elif c == curses.KEY_F3:
            if in_items_frame:
                self._set_focus(self.old_focus_index)
            elif self.items.get('items').labels:
                self.old_focus_index = self.focus_index
                self._set_focus(SaleDialog.ITEMS_FRAME)
        elif c == curses.KEY_F5:
            self._pay()
        elif in_measure_frame and c == KEY_ESCAPE:
            self.search.frame.get('search').set_text('')
            self._set_focus(SaleDialog.SEARCH_FRAME)
        elif self.focus_index == SaleDialog.SEARCH_FRAME and c == ord('-'):
            items_list = self.items.get('items')
            if items_list.labels:
                self._del_item(items_list, items_list.labels[-1].key)
                items_list.scroll.end()
        elif in_items_frame and (c == curses.KEY_DC or c == ord('-')):
            items_list = self.items.get('items')
            si = items_list.get_selection()
            if si is not None:
                self._del_item(items_list, si)
                if not items_list.labels:
                    self._set_focus(self.old_focus_index)
        elif in_items_frame and (c == KEY_ESCAPE or c == KEY_TAB):
            self._set_focus(self.old_focus_index)
        elif c == curses.KEY_F9:
            TransactionSelectionDialog().main()
        elif c == curses.KEY_F4: #reprint
            session = db.get_session()
            sale = db.get_sales(session, 1)[0]
            marzipan_io.print_receipt(sale)
            if db.PAYMENT[self.sale.payment] == 'debit/credit':
                 marzipan_io.print_card_receipt(sale, sale.total, merchant_copy=False)
            TearDialog('sale receipt').main()
        elif c == curses.KEY_F12:
            sys.exit()
        else:
            return False
        return True

    def _make_search(self):
        self.search = ItemSearchDialog(
            layout.FillRightDown(self.measure.layout.width, 0))

    def reindex(self):
        global all_items
        global all_barcodes
        global all_plus
        global all_names
        all_items = self.s.query(db.Item).filter(db.item_filter).all()
        all_barcodes = list(self.s.query(db.BarcodeItem).join(db.Item).filter(db.item_filter))
        all_plus = { }
        all_names = match.Index()
        for item in all_items:
            if item.plu:
                all_plus[item.plu] = item
            try:
               all_names.add_item(item.name, item)
            except UnicodeEncodeError:
               import sys
               print >>sys.stderr, self
               print >>sys.stderr, item.barcodes
               raise


    def main(self):
        while not self.done:
            self.search.update()
            if self.search.done:
                self.item_to_buy = self.search.get_result()
                if self.search.barcode_match():
                    self.barcode_matched = True
                name = ''
                if self.item_to_buy is not None:
                    name = self.item_to_buy.name
                    if self.item_to_buy.id == 807:  # tab payment
                        if self.sale.customer is None:
                            # Need to choose a customer
                            self._get_customer()
                        self.measure.get('qty').set_text(str(self.sale.customer.balance))
                    self.measure.get('cost').set_text(
                        str(self.item_to_buy.price.unit_cost))
                    self.measure.get('unit').set_text(''.join([
                        'Cost (',
                        self.item_to_buy.price.sale_unit.name, ')']))
                else:
                    self.measure.get('cost').set_text('0')
                self._make_search()
                self.frames[SaleDialog.SEARCH_FRAME] = self.search.frame
                self.search.frame.get('search').set_text(name)
                self._set_focus(SaleDialog.MEASURE_FRAME)
            self.update()
            if self.done:
                return
            self._draw_frames()
            c = self.frames[self.focus_index].layout.window.getch()
            if not self.input(c):
                if self.focus_index == SaleDialog.SEARCH_FRAME:
                    self.search.input(c)
                self.frames[self.focus_index].input(c)


class SaleAsyncUpdater(Thread):
    """thread to asynchronously update clock and scale readout"""

    def __init__(self, sale_dialog):
        Thread.__init__(self)
        self.sale_dialog = sale_dialog
        self.last_time_update = 0

    def run(self):
        try:
            while 1:
                if int(time.time()) > self.last_time_update:
                    clock_label = self.sale_dialog.total.get('clock')
                    clock_label.set_text(
                        datetime.datetime.now().strftime(
                        '%m/%d/%y %H:%M:%S'))
                    (y, x) = curses.getsyx()
                    clock_label.show()
                    self.sale_dialog.total.layout.panel.bottom()
                    curses.panel.update_panels()
                    self.sale_dialog.total.layout.window.noutrefresh()
                    curses.setsyx(y, x)
                    curses.doupdate()
                    self.last_time_update = int(time.time())
                time.sleep(0.250)
        except:
            pass

def _void_mark(sale):
    if sale.is_void:
        return "X"
    else:
        return " "

class TabHistoryProcessingDialog(Dialog):
    """Please wait...
    
    (unused)"""
    def __init__(self, customer_id):
        Dialog.__init__(self)
        self.customer_id = customer_id
        self.s = db.get_session()
        self.setup_frame()
        text, self.tab_history = tabutil.show_tab_history(self.customer_id, return_log=True)
        curses.def_prog_mode()
        curses.endwin()
        with os.popen("less", 'w') as f:
            print >>f, text
        curses.reset_prog_mode()

    def setup_frame(self):
        self.add_frame( Frame(
                [   Label(0, 0, 40, "Processing transaction records"),
                    Label(1, 0, 40, "Please hold..."),
                    Label(3, 0, 18, "ESC: done", color_id = HELP_COLOR),
                    Label(3, 19, 18, "F9: Print history", color_id = HELP_COLOR),
                ],
                layout.Center()
            ) )

    def __del__(self):
        self._draw_frames()
        Dialog.__del__(self)

    def input(self, c):
        if Dialog.input(self,c):
            pass    # really pass
        elif c == curses.KEY_F9:
            if not self._fill_or_focus_bad_widget():
                customer = tabutil.find_customer_by_id(self.customer_id)
                marzipan_io.print_tab_history(customer, self.tab_history)
                TearDialog('tab history').main()
        elif c == KEY_ESCAPE:
            self.done = True
        else:
            return False
        return True

class TabHistoryDialog(Dialog):
    '''Show tab history since last zeroed.'''
    def __init__(self, customer_id):
        Dialog.__init__(self)
        self.filled_in = False
        self.customer_id = customer_id
        self.s = db.get_session()
        self.setup_frame()

    def setup_frame(self):
        self.add_frame( Frame(
            [   Label(0, 0, 70, "Tab Changes:"),
                ListBox("tablog", 1, 0, 65, 20,
                    [ (0, "Processing... (this can take a while)") ],
                    sel=1),
                Label(21, 0, 18, "F9: Print history", color_id=HELP_COLOR),
            ]
        , layout.Center()) )

    def fill_in_text(self):
        self.filled_in = True
        text, self.tab_history = tabutil.show_tab_history(self.customer_id, return_log=True)
        history_lines = ( line  for line in text.split('\n') )
        self.frame.get("tablog").set_labels([ (n,line)  for (n,line) in enumerate(history_lines) ])
        self._draw_frames()

    def __del__(self):
        Dialog.__del__(self)

    def _draw_frames(self):
        Dialog._draw_frames(self)
        if self.filled_in is not True:
            self.fill_in_text()

    def input(self, c):
        if Dialog.input(self,c):
            pass    # really pass
        elif c == curses.KEY_F9:
            if not self._fill_or_focus_bad_widget():
                customer = tabutil.find_customer_by_id(self.customer_id)
                marzipan_io.print_tab_history(customer, self.tab_history)
                TearDialog('tab history').main()
        elif c == KEY_ESCAPE:
            self.done = True
        else:
            return False
        return True

class TransactionSelectionDialog(Dialog):
    '''choose transaction to examine'''
    def __init__(self):
        Dialog.__init__(self)
        self.s = db.get_session()
        self.setup_frame()

    def setup_frame(self):
        self.sales = db.get_sales(self.s, 50)
        self.add_frame(Frame([
            Label(0, 0, 60, "Recent transactions:"),
            ListBox("transaction", 1, 0, 50, 15,
                [ (sale, "%1s $%5.2f\t%s" % (_void_mark(sale), sale.total, sale.time_ended)) for sale in self.sales ],
                sel=1),
        ], layout.Center()))

    def __del__(self):
        Dialog.__del__(self)

    def input(self, c):
        if Dialog.input(self,c):
            pass    # really pass
        elif c == KEY_ESCAPE:
            self.done = True
        else:
            return False
        return True

    def update(self):
        transaction = self.frame.get("transaction")
        if transaction.get_hit_enter():
            sale = transaction.get_selection()
            td = TransactionDialog(sale)
            td.main()
            if td.get_result():
                self.done = True
            else:
                transaction.reset_hit_enter()
            self.s.commit()
#            self.frames.pop()
#            self.setup_frame()

class TransactionDialog(Dialog):
    '''list/void/reprint selected transaction'''
    def __init__(self, sale):
        Dialog.__init__(self)
        self.s = db.get_session()
        self.result = False     # Did I make changes?
        self.sale = sale
        self.sale_items = self.sale.items
#        self.sale_items = self.s.query(db.SaleItem).filter(
#                db.SaleItem.sale_id == sale.id).all()
#        self.sale.items = self.sale_items
        try:
            customer_name = self.sale.customer.name
        except AttributeError:
            customer_name = ""
        total = money.moneyfmt(self.sale.total, curr='$', sep='')
        void_color = HELP_COLOR if self.sale.is_void else FRAME_BG
        void_str = "VOID" if self.sale.is_void else ""
        void_toggle = "UNVOID" if self.sale.is_void else "VOID"
        self.add_frame(Frame([
            Label(0,0, 50, "Transaction %d" % sale.id, color_id=void_color),
            Label(1,0, 50, void_str, color_id=void_color),
            Label(2,0, 50, "Time: %s" % sale.time_ended),
            Label(3,0, 50, "Customer: %s" % customer_name),
            Label(4,0, 50, "Paid by: %s" % db.PAYMENT[sale.payment]),
            Label(5,0, 50, "TOTAL: %s" % total),
            ListBox("bought_items", 7,0, 50, 10,
                [ (si.id, "$%6s:  %2d x %s" % (si.total, si.quantity, si.item.name))  for si in self.sale_items ]),
            Label(18,  0, 25, "F6: %s transaction" % void_toggle, color_id=HELP_COLOR),
            Label(18, 26, 25, "F7: REPRINT receipt", color_id=HELP_COLOR),
        ], layout.Center()))

    def __del__(self):
        Dialog.__del__(self)

    def get_result(self):
        return self.result

    def input(self, c):
        if Dialog.input(self,c):
            pass    # really pass
        elif c == curses.KEY_F6:    # void transaction
            if self.sale.is_void:
                if self.sale.has_tab_payment():
                    self.sale.customer.balance -= self.sale.tab_payment_amount()
                elif db.PAYMENT[self.sale.payment] == 'tab':
                    self.sale.customer.balance += self.sale.total
                self.sale.is_void = 0
            else:
                if self.sale.has_tab_payment():
                    self.sale.customer.balance += self.sale.tab_payment_amount()
                elif db.PAYMENT[self.sale.payment] == 'tab':
                    self.sale.customer.balance -= self.sale.total
                self.sale.is_void = 1
                marzipan_io.print_receipt(self.sale)
            self.done = True
            self.result = True
        elif c == curses.KEY_F7:    # reprint receipt
            marzipan_io.print_receipt(self.sale)
            if db.PAYMENT[self.sale.payment] == 'debit/credit':
                marzipan_io.print_card_receipt(self.sale, self.sale.total, merchant_copy=False)
            #TearDialog('sale receipt').main()
            self.done = True
        elif c == KEY_ESCAPE:
            self.done = True
        else:
            return False
        return True

def item_info(session, item):
    """Item information for ItemInfoDialog.setup_frame()"""
    try:
        mct = item.countlogs[-1].new_count    # last manual count
        mct_when = item.countlogs[-1].when_logged
    except IndexError:
        mct = 0
        mct_when = datetime.datetime(1900, 1, 1, 1, 1, 1)
    q = session.query(db.SaleItem).filter_by(item = item)
    sold = q.join(db.Sale).filter( db.Sale.time_ended > mct_when)
    quantity_sold = sum( x.quantity  for x in sold )
    last_sold = session.query(db.Sale).join(db.SaleItem).filter_by(item = item).order_by(db.Sale.time_ended.desc()).first().time_ended
    this_logger.debug(last_sold)
    ret = cStringIO.StringIO()
    this_logger.debug("in item dialog")
    print >>ret, "Item %d: %s" % (item.id, item.name)
    print >>ret, "Barcode(s): %s" % (', '.join( b.barcode for b in item.barcodes ) )
    print >>ret, ""
    print >>ret, "Categories: %s" % (', '.join(cat.name for cat in item.categories))
    try:
        print >>ret, "Tax category: %s  (%.2f%%)" % (item.tax_category.name, item.tax_category.rate * 100)
    except AttributeError:  # tax category not set
        print >>ret, "Tax category: None (2.25%% by default)"
    print >>ret, ""
    if item.size_unit.name in ("each", "count"):
        print >>ret, "Unit size: %s" % item.size_unit.name
    else:
        print >>ret, "Unit size: %s %s" % (item.size, item.size_unit.name)
    print >>ret, "Retail price: $%.2f    per %s" % (item.price.unit_cost, item.price.sale_unit.name)
    print >>ret, "            = $%.2f + $%.2f (tax)" % ( item.price.unit_cost - item.tax_amt, item.tax_amt )
    print >>ret, ""
    print >>ret, "Ordering:"
    for di in item.dist_items:
        print >>ret, "  * %s:" % di.distributor.name
        print >>ret, "    $%.2f  for case of %s %s" % ( di.wholesale_price, di.case_size, di.case_unit )
        try:
            print >>ret, "    margin: %.2f%%" % (100 * di.margin)
            print >>ret, "    markup: %.2f%%" % (100 * di.markup)
        except:
            pass
        # margin, markup
    print >>ret, ""
    print >>ret, "Latest manual count: %s" % mct
    print >>ret, "        timestamped: %s" % mct_when.strftime("%c")
    print >>ret, "Quantity sold since last count: %s" % quantity_sold
    print >>ret, "Number on hand: %s" % (mct - quantity_sold)
    print >>ret, "Last sale: %s" % last_sold.strftime("%c")
    if not item.deliveries:
        print >>ret, "No recorded deliveries"
    else:
        print >>ret, "Last delivery: %s" % (item.deliveries[-1]).time_delivered.strftime("%c")
    return ret.getvalue()

class ItemInfoDialog(Dialog):
    """Displays information on item counts and prices."""

    def __init__(self, item):
        Dialog.__init__(self)
        self.s = db.get_session()
        self.item = item
        self.setup_frame()

    def setup_frame(self):
        text = item_info(self.s, self.item)
        self.add_frame(Frame([
            Label(0, 0, 60, 'Item information:'),
            Label(1, 0, 60, "" ),
            ListBox("info", 2,0, 60, 15, list(enumerate(text.split("\n")) )
                ),
        ], layout.Center()))

    def input(self, c):
        if Dialog.input(self,c):
            pass    # really pass
        elif c == KEY_ESCAPE:
            self.done = True
        else:
            return False
        return True
