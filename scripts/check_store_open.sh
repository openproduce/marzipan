#!/bin/bash

TIME=`date -d "5:00am" --rfc-3339=seconds | sed -e 's/-..:.*//'`

SALES=`mysql -u root register_tape -e "select * from sales where time_ended > \"$TIME\" limit 1" | wc -l`

if [ $SALES -gt 1 ]
  then
    echo yes sales
  else
    echo no sales
    curl -X POST --data-urlencode 'payload={"text": "@slucy @bex @julian @Meredith @jopro @wrleitch @alina: Opening clerk has not checked in...  Please follow up!", "channel": "#timesensitive", "username": "OP Bot"}' https://hooks.slack.com/services/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
fi
