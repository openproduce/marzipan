#!/bin/bash
su - openproduce -c "(cd /home/openproduce/marzipan-prep/register; python ui.py 2> /var/tmp/pos_errs)"

