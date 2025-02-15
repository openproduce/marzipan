import sys

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

from suds.client import Client
import config

gp_login = config.get('globalpay-login')
gp_passwd = config.get('globalpay-password')

url = 'https://certapia.globalpay.com/GlobalPay/transact.asmx?WSDL'
client = Client(url)
print(client)

"""
mc:
%B5499990123456781^GLOBAL PAYMENT TEST CARD/^151250254321987123456789012345?;5499990123456781=15125025432198712345?
visa:
%B4003000123456781^GLOBAL PAYMENT TEST CARD/^151250254321987123456789012345?;4003000123456781=15125025432198712345?
"""
mc_num = '5499990123456781'
visa_num = '4003000123456781'
mc_exp = '1215'
visa_exp = '1215'
mc_track = '%B5499990123456781^GLOBAL PAYMENT TEST CARD/^151250254321987123456789012345?;5499990123456781=15125025432198712345?'
visa_track = '%B4003000123456781^GLOBAL PAYMENT TEST CARD/^151250254321987123456789012345?;4003000123456781=15125025432198712345?'
mc_track = ';5499990123456781=15125025432198712345?'
visa_track = ';4003000123456781=15125025432198712345?'


resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        visa_num,
                                        visa_exp,
                                        visa_track,
                                        'GLOBAL PAYMENT TEST CARD',
                                        '3.56',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')

print(resp)
print("### SWIPED SALE ###")
sys.stdin.readline()

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        visa_num,
                                        visa_exp,
                                        visa_track,
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.53',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        visa_num,
                                        visa_exp,
                                        visa_track,
                                        'GLOBAL PAYMENT TEST CARD',
                                        '11.02',
                                        '', '', '', '', '', '<Force>T</Force><TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        mc_num,
                                        mc_exp,
                                        mc_track,
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.02',
                                        '', '', '', '', '', '<Force>T</Force><TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        mc_num,
                                        mc_exp,
                                        mc_track,
                                        'GLOBAL PAYMENT TEST CARD',
                                        '11.02',
                                        '', '', '', '', '', '<Force>T</Force><TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)


sys.exit()
print("### PARTIAL AUTH ###")
sys.stdin.readline()

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '5111111111111118',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.62',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '4111111111111111',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.54',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '6011000993326655',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.07',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)


resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        '5111111111111118',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.62',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        '4111111111111111',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.54',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')

print((client.last_sent()))
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        '6011000993326655',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.07',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)


print("### PARTIAL AUTH REV ###")
sys.stdin.readline()
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '5111111111111118',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.62',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
pnref = resp.PNRef
print((client.last_sent()))
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'reversal',
                                        '5111111111111118',
                                        '',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '',
                                        '', pnref, '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)


##2##
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '4111111111111111',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.54',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
pnref = resp.PNRef
print((client.last_sent()))
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'reversal',
                                        '4111111111111111',
                                        '',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '',
                                        '', pnref, '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)

##3##
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '6011000993326655',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.07',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
pnref = resp.PNRef
print((client.last_sent()))
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'reversal',
                                        '6011000993326655',
                                        '',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '',
                                        '', pnref, '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)

##4##
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        '5111111111111118',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '23.62',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
pnref = resp.PNRef
print((client.last_sent()))
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'reversal',
                                        '5111111111111118',
                                        '',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '',
                                        '', pnref, '', '', '', '<TermType>3AO</TermType>')
print((client.last_sent()))
print(resp)


print("### KEYED SALE SKIPPED ###")
sys.stdin.readline()

print("### VOID TRANSACTIONS ### first make some transactions")
sys.stdin.readline()

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.08',
                                        '', '', '', '', '', '3AO')
print(resp)
VisaPNRef = resp.PNRef

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.15',
                                        '', '', '', '', '', '3AO')
MCPNRef = resp.PNRef

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '2.08',
                                        '', '', '', '', '', '3AO')
print(resp)
MCPNRef_auth = resp.PNRef

# client.set_options(location='http://localhost:3010')
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'force',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '2.08',
                                        '', MCPNRef_auth, '', '', '', '<TermType>3AO</TermType>')
print(resp)
MCPNRef_authcompl = resp.PNRef
"""

"""
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'force',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '3.08',
                                        '', '', '', '', '', '<AuthCode>999999</AuthCode><TermType>3AO</TermType>')
print(resp)
VisaPNRef_force = resp.PNRef

print("### VOID TRANSACTIONS ### time to void")
sys.stdin.readline()

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.08',
                                        '', VisaPNRef, '', '', '', '<TermType>3AO</TermType>')
VisaPNRef_return = resp.PNRef
print(resp)
"""


"""
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'void',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.15',
                                        '', MCPNRef, '', '', '', '<TermType>3AO</TermType>')
print(resp)


resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'void',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '2.08',
                                        '', MCPNRef_authcompl, '', '', '', '<TermType>3AO</TermType>')
print(resp)


resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'void',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '3.08',
                                        '', VisaPNRef_force, '', '', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'void',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.08',
                                        '', VisaPNRef_return, '', '', '', '<TermType>3AO</TermType>')
print(resp)


print("### FORCE TRANSACTIONS ###")
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'force',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.99',
                                        '', '', '', '', '', '<AuthCode>999999</AuthCode><TermType>3AO</TermType>')
print(resp)
"""

### OVERRIDE TRANSACTIONS ###

"""
# this one gets approved
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'force',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.00',
                                        '', '', '', '', '', '<AuthCode>999999</AuthCode><TermType>3AO</TermType>')
print(resp)

# this one gets rejected (duplicate)
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'force',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.00',
                                        '', '', '', '', '', '<AuthCode>999999</AuthCode><TermType>3AO</TermType>')
print(resp)

# this one gets approved (duplicate force)
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'force',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.00',
                                        '', '', '', '', '', '<Force>T</Force><AuthCode>999999</AuthCode><TermType>3AO</TermType>')
print(resp)
"""

### RETURN TRANSACTIONS ###
"""
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.20',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
PNRef1 = resp.PNRef
print(resp)

"""

"""
# THIS ONE IS BORKEN:
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.20',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
PNRef2 = resp.PNRef
print(resp)
"""

"""
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '36018634567895',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.19',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
PNRef3 = resp.PNRef
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        '373953191351005',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.01',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
PNRef4 = resp.PNRef
print(resp)
"""

#now the returns
"""

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.20',
                                        '', PNRef1, '', '', '', '<TermType>3AO</TermType>')
print(resp)
"""

#THIS ONE IS BORKEN:
"""
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.20',
                                        '', PNRef2, '', '', '', '<TermType>3AO</TermType>')
print(resp)
"""

"""
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '36018634567895',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.19',
                                        '', PNRef3, '', '', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '373953191351005',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.01',
                                        '', PNRef4, '', '', '', '<TermType>3AO</TermType>')
print(resp)
"""

print "### CREDIT TRANSACTIONS ###"
print "## orig PNRef OFF ##"
sys.stdin.readline()

"""
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '4003000123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.21',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '5499990123456781',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.21',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '36018634567895',
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.18',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'return',
                                        '373953191351005',
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.00',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print(resp)


print("### PREAUTH TRANS ###")
sys.stdin.readline()
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        visa_num,
                                        visa_exp,
                                        visa_track,
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.30',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        visa_num,
                                        '1012',
                                        visa_track,
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.31',
                                        '', '', '30329', '4', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        mc_num,
                                        mc_exp,
                                        mc_track,
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.32',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        mc_num,
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.33',
                                        '', '', '30329', '4', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        '36018634567895',
                                        '1012',
                                        '373953191351005',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.18',
                                        '', '', '30329', '4', '', '<TermType>3AO</TermType>')
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        mc_num,
                                        '1215',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.00',
                                        '', '', '30329', '4', '', '<TermType>3AO</TermType>')
print(resp)

print("### PREAUTH REV TRANS ###")
sys.stdin.readline()
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'auth',
                                        visa_num,
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.31',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
pnref = resp.PNRef
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'reversal',
                                        visa_num,
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.31',
                                        '', pnref, '', '', '', '<TermType>3AO</TermType>')


print("### REV TRANS ###")
sys.stdin.readline()
resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'sale',
                                        visa_num,
                                        '1012',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.15',
                                        '', '', '', '', '', '<TermType>3AO</TermType>')
pnref = resp.PNRef
print(resp)

resp = client.service.ProcessCreditCard(gp_login, gp_passwd, 'reversal',
                                        visa_num,
                                        '',
                                        '',
                                        'GLOBAL PAYMENT TEST CARD',
                                        '1.15',
                                        '', pnref, '', '', '', '<TermType>3AO</TermType>')
print(resp)
