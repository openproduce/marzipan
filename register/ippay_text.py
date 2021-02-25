import StringIO
import config

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

import cc
import pycurl

ms = open("magnetic_stripe", "r").read().rstrip().lstrip("%")
# print(ms)
c = cc.parse_magstripe(ms)

(tid, xml) = cc.make_ippay_sale_xml(0.01, c)
print(xml)
exit
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
b = StringIO.StringIO()
c.setopt(pycurl.WRITEFUNCTION, b.write)
try:
    c.perform()
except:
    raise CCError('can\'t contact ippay server')
if c.getinfo(pycurl.HTTP_CODE) != 200:
    raise CCError('ippay HTTP code %d' % (c.getinfo(pycurl.HTTP_CODE)))
resp = b.getvalue()

print(resp)
