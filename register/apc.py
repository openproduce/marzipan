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
