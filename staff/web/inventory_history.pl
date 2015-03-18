#!/usr/bin/perl

# PERL MODULES WE WILL BE USING
use DBI;
use DBD::mysql;
use CGI ':standard';

# HTTP HEADER
print "Content-type: text/html\n\n";

# CONFIG VARIABLES
$platform = "mysql";
$database = "marzipan";
$host = "localhost";
$port = "3306";
$user = "marzipan";
$pw = "";

#DATA SOURCE NAME
$dsn = "dbi:mysql:$database:localhost:3306";

my $id = param('id');


# PERL DBI CONNECT
$dbh = DBI->connect($dsn, $user, $pw);

$sth_name = $dbh->prepare("select name from items where id = ?");
$sth_name->execute($id);
@tmp = $sth_name->fetchrow_array();
$name = $tmp[0];

print "<b> 30 day history for $id - $name </b><br/><br/>\n";

$sth = $dbh->prepare("select time_delivered, amount from deliveries where timestampdiff(day, time_delivered, now()) < 31 and item_id =?");
$sth->execute($id);
print "<b>Adjustments on catalog page:</b>";
print "<table><tr><th>When</th><th>+/-</th></tr>\n";
while (@row = $sth->fetchrow_array) {
	print "<td>$row[0]</td><td style='text-align: right; padding-left: 3em;'>$row[1]</td></tr>\n";
}
print "</table>";

$sth = $dbh->prepare("select s.time_ended, si.quantity, s.customer_id, s.is_void from sales as s, sale_items as si where si.sale_id = s.id and si.item_id = ?  and timestampdiff(day, s.time_ended, now()) < 31");
$sth->execute($id);
print "<b>Sales at POS:</b>";
print "<table><tr><th>When</th><th>how many</th><th>notes</th></tr>\n";
while (@row = $sth->fetchrow_array) {
	print "<td>$row[0]</td><td style='text-align: right; padding-left: 3em;'>$row[1]</td><td>";
	print "slush" if $row[2] == 151;
	print "void" if $row[3] != 0;
	print "</td></tr>\n";
}
print "</table>";
