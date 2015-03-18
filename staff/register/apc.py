import io
import config
import cc
import pycurl

ms = open("ms", "r").read().rstrip().lstrip("%")
#ms = open("dummy_ms", "r").read().rstrip().lstrip("%")
#print(ms)
card = cc.parse_magstripe(ms)

#txn_data = cc.make_tnbci_txn_data(0.01, card)
#print(txn_data)
(xid, status) = io.send_tnbci_request(0.01, card)

print(xid)
print(status)
