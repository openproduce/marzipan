#!/usr/bin/env python3
# merge_items.py
# Patrick McQuighan
# This file actually merges two item ids based on a set of given options

import op_db_library as db
import smtplib
import cgi

print('''Content-type: text/plain\n''')
form = cgi.FieldStorage()
if 'old' not in form or 'into' not in form or 'barcodes' not in form or 'deliveries' not in form or 'dist_items' not in form or 'sales' not in form:
    print('Error: invalid arguments.')
else:
    old_item_id = int(form.getvalue('old'))
    into_item_id = int(form.getvalue('into'))
    old_item = db.get_item(old_item_id)
    into_item = db.get_item(into_item_id)
    merge_barcodes = form.getvalue('barcodes') == 'true'
    merge_deliveries = form.getvalue('deliveries') == 'true'
    merge_dist_items = form.getvalue('dist_items') == 'true'
    merge_sales = form.getvalue('sales') == 'true'
    db.merge_items(old_item, into_item, merge_barcodes = merge_barcodes, merge_deliveries=merge_deliveries,merge_dist_items=merge_dist_items,merge_sales=merge_sales)
    SERVER = "localhost"

    FROM = "item_notifications@openproduce.org"
    TO = ["info@openproduce.org"]

    SUBJECT = 'Item merger notification'

    TEXT = '''Item %s was merged into %s (%s). '%s' no longer exists in the database.''' % (old_item.id, into_item.id, into_item, old_item)

    message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the mail

    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, message)
    server.quit()
