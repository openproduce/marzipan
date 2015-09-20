# Marzipan

Marzipan is an open source point-of-sale system for a small retailer.

* `register/` tree handles actual sales, including printing receipts.

* `web/customer/` holds customer-facing web tools that allow customers
  to look at their personal information (tab balances, for example).  

* `web/staff/` holds staff-facing web tools, which allow staff to
   access data and manage ordering through the web.

* `scripts/` holds non-web scripts that can be run against the
  marzipan databases.

This is a work in progress.  This repository has been created for the
purpose of cleaning up the code before moving it to a public
repository.  Current problems include private information saved in the
code and non-anonymized sample data.


Installing Marzipan
----------------

See INSTALL.md.


Need more information?
----------------------

Marzipan is currently in use at Open Produce.  See
github.com/openproduce and openproduce.org.
