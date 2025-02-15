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

from io import StringIO
import os
import tempfile
import decimal
import subprocess
#from os import popen2
import smtplib
import pycurl
import re
import db
import config
import cc
import money
from util import tabutil
import datetime
import json
from datetime import *
import lxml
from lxml import etree
import suds
import urllib



def write_cui_pipe(str):
    if not config.get('cui-enable'):
        return
    cui_pipe_path = config.get('cui-pipe-path')
    try:
        os.stat(cui_pipe_path)
    except OSError as e:
        try:
            os.mkfifo(cui_pipe_path, 0o760)
        except OSError as e:
            return
    try:
        fd = os.open(cui_pipe_path, os.O_NONBLOCK | os.O_RDWR)
        os.write(fd, str)
        os.close(fd)
    except:
        return

def read_scale():
    pass

def print_customer_card(customer):
    barcode_ps = open('postscriptbarcode/barcode.ps')
    out = tempfile.NamedTemporaryFile()
    for line in barcode_ps:
        out.write(line)
    barcode_ps.close()
    out.write("/Helvetica findfont 10 scalefont setfont\n")
    out.write("30 30 moveto (%s) (includetext guardwhitespace) ean13\n" % (
        customer.code))
    out.write("0 -17 rmoveto (%s) show\n" % (customer.name))
    out.write("showpage\n")
    out.flush()
    try:
        subprocess.call(['lpr',
                         '-P'+config.get('label-printer'), out.name])
    except:
        pass

def print_card_receipt(sale, paid, merchant_copy=False):
    tex = _make_card_receipt_tex(sale, paid, merchant_copy)

    if merchant_copy:
        filename = 'merchant_card_receipt'
    else:
        filename = 'customer_card_receipt'
    out = open(filename + '.tex', 'w+t')
    for line in tex:
        out.write(line)
    out.flush()
    out.close()

    # out = tempfile.NamedTemporaryFile(mode='w+t')
    # for line in tex:
    #     out.write(line)
    # out.flush()
    _print_tex_file(filename)

def print_receipt(sale):
    tex = _make_receipt_tex(sale)

    out = open('sale_receipt.tex', 'w+t')
    for line in tex:
        out.write(line)
    out.flush()
    out.close()

    # out = tempfile.NamedTemporaryFile(mode='w+t')
    # for line in tex:
    #     out.write(line)
    # out.flush()
#    _print_tex_file(out.name)
    _print_tex_file('sale_receipt')


def _print_tex_file(fname):
    cwd = os.getcwd()
    try:
        for f in ['logo.eps']:
            os.symlink(os.path.join(cwd, f),
                       os.path.join(tempfile.gettempdir(), f))
    except:
        pass
    dev_null = open('/dev/null')
    err_file = open('err2', 'w')
    os.chdir(os.path.realpath(os.path.dirname(fname)))
    subprocess.call(['latex', fname + ".tex"],stdout = err_file)
    try:
        dvi_file = fname + ".dvi"
        os.stat(dvi_file)
    except:

        os.chdir(cwd)
        return False

    subprocess.call(['dvips', fname + ".dvi"], stdout=err_file)
    subprocess.call(['lpr',
                     '-P'+config.get('receipt-printer'), fname+'.ps'],
                    stdout=err_file)
    for ext in ['.dvi', '.aux', '.log', '.ps']:
        try:
            os.unlink(fname+ext)
        except:
            pass
    os.chdir(cwd)
    return True

def _make_card_receipt_tex(sale, paid, merchant_copy=False):
    out = [
r"""\nonstopmode
\documentclass[12pt]{article}
\usepackage[paperwidth=7cm,top=1cm]{geometry}
\pagestyle{empty}
\usepackage{epsfig}
\begin{document}
\epsfig{file=logo.eps,width=4cm,height=1.5cm}
\parindent=0pt
\vskip 0.2cm
\begin{center}
{\small 1635 E. 55th St.}\\
{\small Chicago, IL 60615}\\
{\small (773) 496-4327}\\
\vskip 0.5cm
{\Large \sf \bf CARD RECEIPT}
\end{center}
""",
    ]
    out.append(sale.time_ended.strftime("\n%m/%d/%y %H:%M:%S\n\n"))
    out.append("\\vskip 0.5cm\n")
    if sale.clerk:
        out.append("{\\small Clerk: %s}\n\n" % (sale.clerk.name))
    out.append("{\\small Card brand: %s}\n\n" % (sale.cc_brand))
    out.append("{\\small Last 4 of card: %s}\n\n" % (sale.cc_last4))
    out.append("{\\small Card expires: xx/xx}\n\n")
    if sale.cc_name:
        out.append("{\\small Holder:\n\n \\textsf{%s}}\n\n" % (sale.cc_name))
    out.append("{\\small Trans. type: Sale (Swiped)}\n\n")
    out.append("{\\small Trans. ID:} {\\tiny %s}\n\n" % (sale.cc_trans))
    out.append("{\\small Auth. code:} {\\tiny %s}\n\n" % (sale.cc_auth))
    if merchant_copy:
        out.append("{\\small PNRef:} {\\tiny %s}\n\n" % (sale.cc_pnref))
    out.append("\\textbf{\\small Total:} \$%s\n\n" % (
        money.moneyfmt(paid, curr='', sep='')))
    if merchant_copy:
        out.append("""\\vskip 0.4cm\n{\\scriptsize I agree to pay the above amount \n\n according to the cardholder agreement.}
        \\vskip 0.2cm
{\\small Signature:}

\\vskip 2em
\\hline

\\vskip 0.5cm
""")
    if sale.customer and sale.customer.balance:
        out.append("{\small Tab balance:} \$%s\n\n" % (
            money.moneyfmt(decimal.Decimal(sale.customer.balance),
                           curr='', sep='')))
    out.append("""
\\vskip 2.0cm

.
""")
    out.append("\end{document}\n")
    return out

def _make_receipt_tex(sale):
    out = [
        r"""\nonstopmode
\documentclass[12pt]{article}
\usepackage[paperwidth=7cm,top=0cm,left=.25cm,right=.25cm]{geometry}
\pagestyle{empty}
\usepackage{epsfig}
\begin{document}
\hskip .75cm
\epsfig{file=logo.eps,width=4cm,height=1.5cm}
\parindent=0pt
\vskip 0.2cm
\begin{center}
{\small 1635 E. 55th St.}\\
{\small Chicago, IL 60615}\\
{\small (773) 496-4327}\\
www.openproduce.org\\\\
\vskip 0.3cm""", ]
    if sale.is_void == 1:
        out.append("{\Large \sf \\bf VOIDED SALE}\n\n")
    else:
        out.append("{\Large \sf \\bf SALE RECEIPT}\n\n")
    out.append("""\\end{center}
    {\scriptsize Returns, exchanges, and refunds are allowed at manager's discretion and as required by law. Bargain items cannot be returned.  To comply with Chicago's health code, frozen and refrigerated items cannot be returned for a refund, and may only be exchanged for the same item.  On all other items, only the person who made the original purchase may request a refund.\par}
\\begin{center}
""")
    out.append(sale.time_ended.strftime("%m/%d/%y %H:%M:%S\n"))
    out.append("\\end{center}\n\n")
    if sale.clerk:
        out.append("\nClerk: %s\n\n" % (sale.clerk.name))

    out.append("\nSale ID: %d\n\n" % (sale.id))
    out.append("""
\\vskip 0.3cm
\\vskip 3pt
\\hrule
\\vskip 3pt
""")

    def size_unit(i):
        if i.size_unit.name != 'each' and i.size_unit.name != 'count':
            return ' [%.1f %s]' % (i.size, i.size_unit)
        return ''
    total_tax = 0
    for si in sale.items:
        name = 'other/grocery'
        qty = si.quantity
        unit = ''
        unit_cost = money.moneyfmt(si.unit_cost, curr='\$', sep='')
        tax = ''
        total = money.moneyfmt(si.total, curr='\$', sep='')
        if si.item:
            name = si.item.name
            unit = ''.join(['/', si.item.price.sale_unit.name])
            tax = str(si.item.tax_rate)
            total_tax += si.tax
        out.append("%s\n\n\\hskip 1cm %.2f @ %s%s = %s\n\n" %
                   (name, qty, unit_cost, unit, total))
        out.append("\\hskip 2cm (tax = %s)\n\n" %
                   money.moneyfmt(si.tax, curr='', sep=''))

    out.append("""
\\vskip 3pt
\\hrule
\\vskip 3pt
""")
    out.append("(Total Tax: \$%s)\n\n" %
               money.moneyfmt(total_tax, curr='', sep=''))
    out.append("Total: \$%s\n\n" % (
        money.moneyfmt(sale.total, curr='', sep='')))
    if db.PAYMENT[sale.payment] == 'void':
        out.append("Sale void, no payment.\n\n")
    else:
        out.append("Paid with %s.\n\n" % (db.PAYMENT[sale.payment]))
    if sale.customer and sale.customer.balance:
        out.append("Tab balance: \$%s\n\n" % (
            money.moneyfmt(decimal.Decimal(sale.customer.balance),
                           curr='', sep='')))
        out.append("{\small Customer: %s}\n\n" % sale.customer.name)
    out.append("""
\\vskip 0.5cm
\\begin{center}
Thanks for shopping!\n\n
\\vskip 0.2cm
{\\large \\textbf{Open 8am -- 12 midnight every day}}
\end{center}
%\\vspace*{4cm}
\\vskip 1.5cm

.
""")
    out.append("\end{document}\n")
    return out

def email_receipt(address, sale):
    email = _make_receipt_email(address, sale)
    try:
        s = smtplib.SMTP(config.get('smtp-server'),
                         timeout=20)
        s.sendmail("sales@openproduce.org", [address],
                   '\n'.join(email))
        s.quit()
        return True
    except:
        return False

def _make_receipt_email(address, sale):
    out = []
    out.append("From: Open Produce <sales@openproduce.org>")
    out.append("To: %s" % (address))
    out.append("Subject: Open Produce sale receipt")
    out.append("")
    out.append("Here is a receipt for your purchase on %s." % (
        sale.time_ended.strftime("%m/%d/%y %H:%M:%S")))
    if sale.clerk:
        out.append("Clerk: %s" % (sale.clerk.name))
    out.append("")
    for si in sale.items:
        out.append(si.item.name)
        out.append("                %s" % (
            money.moneyfmt(si.total, curr='$', sep='')))
    if db.PAYMENT[sale.payment] == 'void':
        out.append("Sale void, no payment.")
    else:
        out.append("Total: %s paid with %s." % (
            money.moneyfmt(sale.total, curr='$', sep=''),
            db.PAYMENT[sale.payment]))
    out.append("")
    if sale.customer and sale.customer.balance:
        out.append("Your current tab balance is %s." % (
            money.moneyfmt(decimal.Decimal(sale.customer.balance),
                           curr='$', sep='')))
    out.append("")
    out.append("Thanks for shopping at Open Produce!")
    return out


class CCError(Exception):
    def __init__(self, error):
        self.error = error
    def __str__(self):
        return self.error

def send_dejavoo_void_request(amount, xid):

    c = pycurl.Curl()
    if amount > 0:
        #c.setopt(pycurl.URL, config.get('dejavoo-url') + '/terminal/charge/queue')
        # opting to use /terminal/charge because it's compatible with /terminal/credit so only one set of code for handling response
        c.setopt(pycurl.URL, config.get('dejavoo-url') + '/terminal/void')
        credit = False
    else:
        c.setopt(pycurl.URL, config.get('dejavoo-url') + '/terminal/void')
        amount = -amount
        credit = True

    values = {
    "total": str(amount),
    "meta": { },
    "printReceipt": "Both",
    "transactionId": xid
    #"register": tid
}

    headers = {
      'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + config.get('dejavoo-api-key'),
      'Accept': 'application/json'
    }

    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, [
      'Content-Type: application/json',
      'Authorization: Bearer ' + config.get('dejavoo-api-key'),
      'Accept: application/json'])
    c.setopt(pycurl.POSTFIELDS, json.dumps(values))
    c.setopt(pycurl.USERAGENT, 'curl/7.58.0') # was getting blocked by cloudflare with pycurl user agent
    c.setopt(pycurl.TIMEOUT, 75) #terminal times out in 60s so this must be longer than that
    import io
    b = io.BytesIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    try:
        c.perform()
    except:
        raise CCError('can\'t contact dejavoo server')
    if c.getinfo(pycurl.HTTP_CODE) == 504: #terminal timed out
        return {"success": False, "message": "No card inserted"}

    if c.getinfo(pycurl.HTTP_CODE) != 200 and c.getinfo(pycurl.HTTP_CODE) != 400:
        sys.stderr.write(b.getvalue().decode('utf-8'))
        raise CCError("dejavoo HTTP code %d" % (c.getinfo(pycurl.HTTP_CODE)))
    resp = b.getvalue()
    sys.stderr.write(resp.decode('utf-8'))
    c.close()
    return json.loads(resp)

def send_dejavoo_request(amount, tid):

    c = pycurl.Curl()
    if amount > 0:
        #c.setopt(pycurl.URL, config.get('dejavoo-url') + '/terminal/charge/queue')
        # opting to use /terminal/charge because it's compatible with /terminal/credit so only one set of code for handling response
        c.setopt(pycurl.URL, config.get('dejavoo-url') + '/terminal/charge')
        credit = False
    else:
        c.setopt(pycurl.URL, config.get('dejavoo-url') + '/terminal/credit')
        amount = -amount
        credit = True

    values = {
    "total": str(amount),
    "meta": { },
    "printReceipt": "No",
    "paymentType": "Credit",
    "register": tid
}

    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + config.get('dejavoo-api-key'),
      'Accept': 'application/json'
    }

    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, [
      'Content-Type: application/json',
      'Authorization: Bearer ' + config.get('dejavoo-api-key'),
      'Accept: application/json'])
    c.setopt(pycurl.POSTFIELDS, json.dumps(values))
    c.setopt(pycurl.USERAGENT, 'curl/7.58.0') # was getting blocked by cloudflare with pycurl user agent
    c.setopt(pycurl.TIMEOUT, 75) #terminal times out in 60s so this must be longer than that
    import io
    b = io.BytesIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    try:
        c.perform()
    except Exception as e:
        print(e)
        return {"success": False, "message": "Can't contact Fatt Merchant server"}
    if c.getinfo(pycurl.HTTP_CODE) == 504: #terminal timed out
        return {"success": False, "message": "No card inserted"}
    if c.getinfo(pycurl.HTTP_CODE) == 502: #bad gateway
        return {"success": False, "message": "bad gateway; try again"}
    if c.getinfo(pycurl.HTTP_CODE) != 200 and c.getinfo(pycurl.HTTP_CODE) != 400:
        sys.stderr.write(b.getvalue().decode('utf-8'))
        return {"success": False, "message": "dejavoo HTTP code %d" % (c.getinfo(pycurl.HTTP_CODE))}
        #raise CCError()
    resp = b.getvalue().decode('utf-8')
    sys.stderr.write(resp)
    c.close()
    return json.loads(resp)
    

def request_dejavoo_status(xid):

    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + config.get('dejavoo-api-key'),
      'Accept': 'application/json'
    }

    c = pycurl.Curl()
    c.setopt(pycurl.URL, config.get('dejavoo-url') + '/transaction/' + str(xid))
    #c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, [
      'Content-Type: application/json',
      'Authorization: Bearer ' + config.get('dejavoo-api-key'),
      'Accept: application/json'])
    c.setopt(pycurl.USERAGENT, 'curl/7.58.0') # was getting blocked by cloudflare with pycurl user agent
    c.setopt(pycurl.TIMEOUT, 5)
    import StringIO
    b = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    try:
        c.perform()
    except:
        raise CCError('can\'t contact dejavoo server')
    if c.getinfo(pycurl.HTTP_CODE) != 200:
        print(xid)
        sys.stderr.write(b.getvalue().decode('utf-8'))
        raise CCError("dejavoo HTTP code %d" % (c.getinfo(pycurl.HTTP_CODE)))
    resp = b.getvalue().decode('utf-8')
    sys.stderr.write(resp)
    return json.loads(resp)



    
def _parse_ippay_response(resp):
    m = re.search('<ResponseText>(.*)</ResponseText>', resp)
    if not m:
        raise CCError('no ResponseText in ippay xml')
    return m.group(1)

def send_ippay_request(amount, card):
    if not card.validate():
        raise CCError('invalid card info')
    (xid, xml) = cc.make_ippay_sale_xml(amount, card)
    c = pycurl.Curl()
    c.setopt(pycurl.URL, config.get('ippay-url'))
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, [
        'Content-type: text/xml',
        'Content-length: %d' % (len(xml))])
    c.setopt(pycurl.POSTFIELDS, xml)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 2)
    c.setopt(pycurl.TIMEOUT, 30)
    import io
    b = io.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    try:
        c.perform()
    except:
        raise CCError('can\'t contact ippay server')
    if c.getinfo(pycurl.HTTP_CODE) != 200:
        raise CCError('ippay HTTP code %d' % (c.getinfo(pycurl.HTTP_CODE)))
    resp = b.getvalue()
    status = _parse_ippay_response(resp)
    return (xid, status)


def _parse_tnbci_response(resp):
    resp_hash = {}
    for key, value in [kvp.split('=') for kvp in resp.split('&')]:
        resp_hash[key] = value

    resp_code = int(resp_hash['response_code'])

    if resp_code == 100:
        response_text = "APPROVED"
    elif resp_code >= 200 and resp_code < 300:
        response_text = "DECLINED (%d)" % resp_code
    elif resp_code >= 300 and resp_code < 400:
        response_text = "MERCHANT ERROR (%d)" % resp_code
    elif resp_code >= 400 :
        response_text = "PROCESSOR ERROR (%d)" % resp_code
    else:
        response_text = "I'M QUITE CONFUSED"

    return (resp_hash['transactionid'], response_text)

def send_tnbci_request(amount, card):
    if not card.validate():
        raise CCError('invalid card info')
    txn_data = cc.make_tnbci_txn_data(amount, card)

    cmd = 'wget -q -O- --post-data="' + txn_data + \
        '" "' + config.get('tnbci-url') + '"'

    r, w, e = popen2.popen3(cmd)
    wget_output = r.readlines()
    wget_errors = e.readlines()
    r.close()
    e.close()
    w.close()

    resp_text = ''.join(wget_output)

    if len(wget_errors) > 0:
        raise CCError('wget can\'t contact tnbci')
    
    (xid, status) = _parse_tnbci_response(resp_text)
    return (xid, status)

# def _parse_globalpay_response(resp):
# #This is not used. It is provided in case the WSDL stuff in formerly_io.send_globalpay_request stops working 
#     m = re.search('<Message>(.*)</Message>', resp)
#     if m:
#         print "global said: %s" % m.group(1)
    
#     m = re.search('<RespMSG>(.*)</RespMSG>', resp)
#     if not m:
#         raise CCError('no RespMSG in globalpay xml')
    
#     return m.group(1).upper()

# try:
#     transact = suds.client.Client('https://api.globalpay.com/GlobalPay/transact.asmx?WSDL')
#     transact.set_options(timeout=7)
#     report = suds.client.Client('https://api.globalpay.com/GlobalPay/transact.asmx?WSDL')
#     report.set_options(timeout=7)
#     # try to setup cc on boot, but fail silently if we can't
# except:
#     pass



# def send_globalpay_request(amount, card, sale):
#     try:
#         transact
#     except NameError:
#         transact = suds.client.Client('https://api.globalpay.com/GlobalPay/transact.asmx?WSDL')
#         transact.set_options(timeout=7)
#         report = suds.client.Client('https://api.globalpay.com/GlobalPay/transact.asmx?WSDL')
#         report.set_options(timeout=7)
#     f = open('/tmp/marzipanlog', 'w')
#     f.write("file open\n")
#     f.flush
#     if not card.validate():
#         raise CCError('invalid card info')
#     try:
#         resp = transact.service.ProcessCreditCard(config.get('globalpay-login'), config.get('globalpay-password'), 'sale',
#                                                 card.number,
#                                                 '%02d%02d' % (card.exp_month, card.exp_year % 100),
#                                                 card.track2,
#                                                 card.account_name,
#                                                 '%.2f' % amount,
#                                                 '', '', '', '', '', '3AO')
#     except:
#         #request timed out. check logs to see if it managed to go through.
#         now = datetime.now()
#         twenty_seconds_ago = (now - timedelta(seconds=20)).strftime("%Y-%m-%dT%H:%M:%S")
#         try:
#             resp = report.service.GetCardTrx(config.get('globalpay-login'), config.get('globalpay-password'), '84571', '', twenty_seconds_ago, now, '', '', '', '', '', '', '', '', '', '', ' ', 'TRUE', '', '', '', '', '', '', '', '', '', '', '<TermType>3A0</TermType>')
#             root = etree.fromstring(str(resp))
#             res = root.xpath("//TrxDetailCard[Name_on_Card_VC[starts-with(.,'%s')]]" % card.account_name)
#             if len(res) >= 1:
#                 #we don't deal with the case that there are two or more transactions in the past 20 seconds with the same cardholder name.
#                 return (res[0].find('TranID').text.strip(), 'APPROVED')
#             else:
#                 #If reporting works but transaction timed out, just try again 
#                 send_globalpay_request(amount, card, sale)
#         except:
#             #asking for the log timed out too.
#             #if the clerk reruns it and it says "duplicate", then we're fine, and the sale should be logged as completed 
#             return ('','timeout. re-run transaction.' )
#     try:
#         f.write(str(resp))
#         f.write("\n--------------------\n")
#         f.flush
#         f.close
#         if resp.RespMSG != 'Approved':
#             msg = "%s (%s)" % (resp.RespMSG, resp.Message)
#         else:
#             msg = resp.RespMSG
#         m = re.search('<MID>(.*)</MID><Trans_Id>(.*)</Trans_Id>', str(resp))
#         if not m:
#             raise AttributeError()
#         sale.cc_mid = m.group(1)
#         xid = m.group(2)
#         sale.cc_pnref = resp.PNRef
#         sale.cc_auth = resp.AuthCode    
#     except AttributeError:
#         msg = resp.RespMSG
#         xid = ""

#     return (xid, msg)


def print_ar_report(customers):
    pass


def print_tabhistory(customer, tab_history):
    out = tempfile.NamedTemporaryFile()
    out.writelines(_make_tabhistory_tex(customer, tab_history))
    out.flush()
    _print_tex_file(out.name)

def _texify_tablog(entry):
    d = entry.delta()
    if d >= 0:
        s = "CHARGED"
    else:
        s = "PAID"
    return "%s \\$%.2f\t(\\$%.2f $\\to$ \\$%.2f) \\\\%s" % (
        s,
        abs(d),
        entry.old_balance,
        entry.new_balance,
        entry.when_logged,
    )


def _make_tabhistory_tex(customer, tab_history):
    real_stdout = sys.stdout
    out = cStringIO.StringIO()
    sys.stdout=out
    print((r"""\\nonstopmode
\documentclass[12pt]{article}
\usepackage[paperwidth=7cm,top=0cm,left=.25cm,right=.25cm]{geometry}
\pagestyle{empty}
\usepackage{epsfig}
\begin{document}
\hskip .75cm
\epsfig{file=logo.eps,width=4cm,height=1.5cm}
\parindent=0pt
\vskip 0.2cm
\begin{center}
{\small 55th and Cornell, Chicago\\\\
www.openproduce.org\\\\
(773) 496--4327}
\vskip 0.3cm
{\Large \sf \\bf TAB HISTORY} \\\\
for customer: %s

""" % customer.name))
    print( "\\end{center}\n\n")
    print("""
\\vskip 0.3cm
\\vskip 3pt
\\hrule
\\vskip 3pt
""")
    ###
    print(r"\tiny")
    print(r"\begin{itemize}")
    for entry in tab_history:
        print(("\\item %s" % _texify_tablog(entry)))
        if entry.is_payment() is False:
            print(r"\begin{itemize}")
            for si in tabutil.tab_charged_items(entry):
                try:
                    si_item_name = si.item.name
                except AttributeError:
                    si_item_name = "<unknown item>"
                print(("\\item \\$%5.2f\t%s" % (si.total, si_item_name)))
            print(r"\end{itemize}")
    print(r"\end{itemize}")
    ###
    print("""
\\vskip 3pt
\\hrule
\\vskip 3pt
\\vskip 0.5cm
Thanks for shopping!
%\\vspace*{4cm}
\\vskip 1.5cm

.
""")
    print("\\end{document}\n")
    sys.stdout = real_stdout
    our_string = out.getvalue();
    out.close();
    return our_string;
