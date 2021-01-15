#!/bin/bash
#su - openproduce -c "ssh -L 3306:localhost:3306 cardamom -N&"
su - openproduce -c "(cd /home/openproduce/marzipan/register; python ui.py 2> /var/tmp/pos_errs-`date +%s`)"

