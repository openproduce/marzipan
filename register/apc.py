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

import marzipan_io
import config
import cc
import pycurl

ms = open("magnetic_stripe", "r").read().rstrip().lstrip("%")
#print(ms)
card = cc.parse_magstripe(ms)

#txn_data = cc.make_tnbci_txn_data(0.01, card)
#print(txn_data)
(xid, status) = marzipan_io.send_tnbci_request(0.01, card)

print(xid)
print(status)
