import config
import cc
import pycurl

ms = open("magnetic_stripe", "r").read().rstrip().lstrip("%")
#print(ms)
c = cc.parse_magstripe(ms)

(tid, xml) = cc.make_ippay_sale_xml(0.01, c)
print(xml)
exit
c = pycurl.Curl()
c.setopt(pycurl.URL, config.get('ippay-url'))
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.HTTPHEADER, [
       'Content-type: text/xml',
       'Content-length: %d'%(len(xml))])
c.setopt(pycurl.POSTFIELDS, xml)
c.setopt(pycurl.SSL_VERIFYPEER, 0)
c.setopt(pycurl.SSL_VERIFYHOST, 2)
c.setopt(pycurl.TIMEOUT, 30)
import StringIO
b = StringIO.StringIO()
c.setopt(pycurl.WRITEFUNCTION, b.write)
try:
       c.perform()
except:
    raise CCError('can\'t contact ippay server')
if c.getinfo(pycurl.HTTP_CODE) != 200:
    raise CCError('ippay HTTP code %d'%(c.getinfo(pycurl.HTTP_CODE)))
resp = b.getvalue()

print(resp)
