#!/usr/bin/env python

# This file is part of Marzipan, an open source point-of-sale system.
# Copyright (C) 2012 Open Produce LLC
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

import re
import sys
import decimal
import time
import config
import random
import urllib.request, urllib.parse, urllib.error


class Card:
    def __init__(self):
        self.account_name = ''
        self.number = ''
        self.exp_month = 0
        self.exp_year = -1
        self.track1 = ''  # added by APC
        self.track2 = ''  # added by APC
        self.magtext = ''  # added by APC mar 30 2012

    def validate(self):
        if not re.match('^\d{16}$', self.number):
            return False
        if type(self.exp_month) is not int or\
           type(self.exp_year) is not int:
            return False
        if self.exp_month < 1 or self.exp_month > 12:
            return False
        if self.exp_year < 0:
            return False
        return True


class BadSwipeError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'bad swipe: %s' % (self.error)


def parse_magstripe(magstripe):
    magtext = ''.join([chr(x) for x in magstripe])  # todo uncomment
    card = Card()
    card.magtext = "%" + magtext
    tracks = magtext.split(';')
    card.track1 = "%" + tracks[0]  # added by apc
    card.track2 = ';' + tracks[1]
    if "%E?" in magtext or "+E?" in magtext:
        raise BadSwipeError("need both tracks")

    try:
        (number, name, exp) = magtext.split('^', 2)
    except:
        raise BadSwipeError('bad field sep')
    if number.startswith('B'):
        number = number[1:]
    else:
        raise BadSwipeError('unrecognized track format')
    if not re.match('^\d{16}$', number):
        raise BadSwipeError('non 16-digit number')
    card.number = number
    name = name.strip()
    if '/' in name:
        (last, first) = name.split('/')
        card.account_name = '%s %s' % (first, last)
    else:
        card.account_name = '?'
    m = re.match('^(\d{2})(\d{2})', exp)
    if m:
        (year, month) = m.groups()
        if int(month) < 1 or int(month) > 12:
            raise BadSwipeError('bad month')
        card.exp_year = int(year)
        card.exp_month = int(month)
    else:
        raise BadSwipeError('no expiration')
    return card


def _gen_transaction_id():
    ts = str(int(time.time()))
    return ts + ''.join([chr(ord('A')+random.randint(0, 25))
                         for x in range(18-len(ts))])


def make_ippay_sale_xml(amount, card):
    xid = _gen_transaction_id()
    return (xid, """<JetPay>
        <Track1>%s</Track1>
        <TransactionType>SALE</TransactionType>
        <Origin>POS</Origin>
        <IndustryInfo Type="RETAIL"></IndustryInfo>
        <TerminalID>%s</TerminalID>
        <TransactionID>%s</TransactionID>
        <FeeAmount>0</FeeAmount>
        <BillingPostalCode>60601</BillingPostalCode>
        <CardNum>%s</CardNum>
        <CardExpMonth>%02d</CardExpMonth>
        <CardExpYear>%02d</CardExpYear>
        <TotalAmount>%d</TotalAmount>
</JetPay>
""" % (card.track1, config.get('ippay-terminalid'), xid,
       card.number, card.exp_month, card.exp_year % 100,
       int(amount*100)))


# This is not used. It is provided in case the WSDL stuff in marzipan_io.send_globalpay_request stops working
def make_globalpay_sale_xml(amount, card):
    xid = _gen_transaction_id()
    return (xid, """<?xml version="1.0" encoding="UTF-8"?>
    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="GlobalPayments">
    	<SOAP-ENV:Body>
    		<ns1:ProcessCreditCard>
    			<ns1:GlobalUserName>%s</ns1:GlobalUserName>
    			<ns1:GlobalPassword>%s</ns1:GlobalPassword>
    			<ns1:TransType>Sale</ns1:TransType>
    			<ns1:CardNum>%s</ns1:CardNum>
    			<ns1:ExpDate>%02d%0d</ns1:ExpDate>
    			<ns1:MagData>%s</ns1:MagData>
    			<ns1:NameOnCard>%s</ns1:NameOnCard>
    			<ns1:Amount>%.2f</ns1:Amount>
    			<ns1:InvNum>%s</ns1:InvNum>
    			<ns1:PNRef></ns1:PNRef>
    			<ns1:Zip></ns1:Zip>
    			<ns1:Street></ns1:Street>
    			<ns1:CVNum></ns1:CVNum>
    			<ns1:ExtData>&lt;TermType&gt;3AO&lt;/ns1:TermType&gt;</ns1:ExtData>
    		</ns1:ProcessCreditCard>
    	</SOAP-ENV:Body>
    </SOAP-ENV:Envelope>
""" % (config.get('globalpay-login'), config.get('globalpay-password'), card.number, card.exp_month, card.exp_year % 100, card.track1, card.account_name, amount, xid))


def make_tnbci_txn_data(amount, card):

    txn = {'type': 'sale',
           'username': config.get('tnbci-login'),
           'password': config.get('tnbci-password'),
           'ccnumber': str(card.number),
           'ccexp': '%02d%02d' % (card.exp_month, card.exp_year % 100),
           'amount': '%.2f' % amount,
           'track_1': urllib.parse.quote(card.track1),
           'payment': 'creditcard'
           }
    kvpairs = ["%s=%s" % (x[0], x[1]) for x in list(txn.items())]
    #print >>sys.stderr, '&'.join(kvpairs)
    return '&'.join(kvpairs)
