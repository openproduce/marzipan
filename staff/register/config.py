#!/usr/bin/env python
import sys
import os
import getopt

class _Option:
    """configurable program setting"""
    def __init__(self, is_cmdline, desc, short, has_arg, value):
        self.is_cmdline = is_cmdline
        self.desc = desc
        self.short = short
        self.has_arg = has_arg
        self.value = value

_options = {
    'help':
        _Option(True, 'dump usage info', 'h', False, None),

    'cui-enable':
        _Option(True, 'enable customer-facing display', None, False, None),
    'cui-pipe-path':
        _Option(True, 'pipe to customer UI', None, True, '/tmp/cuipipe'),

    'db-init':
        _Option(True, 'create db', None, False, None),
    'db-import':
        _Option(True, 'import price list', None, True, ''),
    'db-mysql-path':
        _Option(True, 'path to mysql shell', None, True, 'mysql'),
    'db-mysql-admin':
        _Option(True, 'mysql admin user', None, True, 'root'),

    'db-host':
        _Option(True, 'mysql db hostname', None, True, 'localhost'),
    'db-user':
        _Option(True, 'mysql db username', None, True, 'marzipan'),
    'db-passwd':
        _Option(True, 'mysql db password', None, True, ''),
    'db-name-reg':
        _Option(True, 'mysql db name - register tape', None, True, 'register_tape'),
    'db-name-inv':
        _Option(True, 'mysql db name - inventory', None, True, 'inventory'),
        
    'globalpay-login':
        _Option(True, 'globalpay login', None, True, 'open9738'),
    'globalpay-password':
        _Option(True, 'globalpay password', None, True, 'Aimedaca1'),            
    'globalpay-url':
        _Option(True, 'globalpay url', None, True, 'https://api.globalpay.com/GlobalPay/transact.asmx'),        

    'ippay-terminalid':
        _Option(True, 'ippay terminal id', None, True, 'OPENPRODU001'),
#    'ippay-url':
#        _Option(True, 'ippay url', None, True, 'https://test1.jetpay.com/jetpay'),
    'ippay-url':
        _Option(True, 'ippay url', None, True, 'https://gateway17.jetpay.com/jetpay'),
    'smtp-server':
        _Option(True, 'smtp server', None, True, 'mail.parallactic.com'),
    'receipt-printer':
        _Option(True, 'receipt printer name', None, True, 'tsp100'),
    'label-printer':
        _Option(True, 'label printer name', None, True, 'QL-500'),
    'cc-processor':
        _Option(True, 'ippay, tnbci, or globalpay', None, True, 'globalpay'),
    'tnbci-url':
        _Option(True, 'tnbci url', None, True, 'https://secure.tnbcigateway.com/api/transact.php'),
#        _Option(True, 'tnbci url', None, True, 'https://www.gmail.com'),
#        _Option(True, 'tnbci url', None, True, 'http://localhost:9001'),

}

def usage():
    """print usage info to stdout. doesn't exit afterwards."""
    print "marzipan.py [OPTIONS]"
    print "point-of-sale terminal software\n"
    for name in sorted(_options.keys()):
        o = _options[name]
        if o.is_cmdline:
            o_str = ""
            if o.short is not None:
                o_str = "--%s, -%s"%(name, o.short)
            else:
                o_str = "--%s"%(name)
            print "  %-24s %s"%(o_str, o.desc)
    print

def get(name):
    """lookup option value. assume parse_cmdline() called."""
    return _options[name].value

def parse_cmdline(argv):
    """assume program name stripped from argv"""
    global _options

    # build argument spec parameters for getopt.getopt.
    short_opts = ''
    long_opts = []
    short_to_long = {}
    for long_name in sorted(_options.keys()):
        o = _options[long_name]
        if o.is_cmdline:
            if o.has_arg:
                long_opts.append(long_name+'=')
            else:
                long_opts.append(long_name)
            if o.short is not None:
                short_to_long[o.short] = long_name
                short_opts += o.short
                if o.has_arg:
                    short_opts += ':'

    # call getopt and populate option values.
    try:
        [opts, rest] = getopt.getopt(argv, short_opts, long_opts)
        for opt, value in opts:
            opt_name = ''
            if opt.startswith('--'):
                opt_name = opt[2:]
            elif opt.startswith('-'):
                opt_name = short_to_long[opt[1:]]
            else:
                assert False, opt_name
            o = _options[opt_name]
            if o.has_arg:
                o.value = value
            else:
                o.value = True
    except getopt.GetoptError, e:
        print "marzipan: %s"%(e)
        usage()
        sys.exit(1)

    if rest:
        print "marzipan: leftover command-line `%s'"%(rest)
        usage()
        sys.exit(1)
    if get("help"):
        usage()
        sys.exit(0)

if __name__ == "__main__":
    parse_cmdline(sys.argv[1:])
    for name in sorted(_options.keys()):
        print "%-20s %s"%(name, _options[name].value)
