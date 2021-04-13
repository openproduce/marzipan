#!/usr/bin/env perl

use FindBin;  
use lib $FindBin::Bin;   

use DBI;
use DBD::mysql;

use DBCreds;
$DB_USER="marzipan";
our $DB_PASSWORD;

my $dbh_marzipan = DBI->connect("dbi:mysql:inventory:localhost:3306", 'marzipan', $DBCreds::DB_PASSWORD);
    or die "couldn't connect to database";

    print "Content-type: text/html\n\n";
    print <<EOF;
<!doctype html>
<html>
<head>
<title>Dash board</title>
<style type="text/css">
    .check { width: 400px; height: 200px; }
    body {font-size: 14px; font-family: verdana;}
	td,th {border-bottom: 1px solid #999; padding-right: 1em; padding-left: 1em;}
	.right {text-align: right}
	.bar {background-color: rgb(143, 239, 143);}
	.total td {border-top: 7px solid #fff; border-bottom: none; background-color: #f99;}
	.tiny {font-size: 9px; line-height: 9px; padding-left: 1px; padding-right: 1px;}
	/*.gray {background-color: #ddd;}*/

</style>
</head>
<body>
EOF

$sth = $dbh_marzipan->prepare("SELECT i.name, p.unit_cost from items as i, prices as p, categories as c, category_items as ci where i.price_id = p.id and i.id = ci.item_id and ci.cat_id = c.id and i.is_discontinued = false and (c.name like 'beer' or c.name like 'wine' or c.name like 'spirits') ORDER BY i.name");

$sth->execute;

   print "<p> </p><h1>Prices as of " . `date` . "</h1><table>\n";
    while (my @a = $sth->fetchrow_array()) {
      print "<tr>\n";
      print "<td>$a[0]</td><td>" . sprintf("\$%.2f", $a[1]) . "</td>\n";
      print "</tr>\n";
    }
    print "</table>\n";


print "</body>";
