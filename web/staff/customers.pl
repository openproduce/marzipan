#!/usr/bin/env perl

use FindBin;  
use lib $FindBin::Bin;   

use DBI;
use DBD::mysql;

use DBCreds;
$DB_USER="marzipan";
our $DB_PASSWORD;

print "Content-type: text/html\n\n";

%names = (
		"1" => "January",
		"2" => "February",
		"3" => "March",
		"4" => "April",
		"5" => "May",
		"6" => "June",
		"7" => "July",
		"8" => "August",
		"9" => "September",
		"10" => "October",
		"11" => "November",
		"12" => "December");

my $dbh_marzipan = DBI->connect("dbi:mysql:register_tape:localhost:3306", 'marzipan', $DBCreds::DB_PASSWORD)
    or die "couldn't connect to database";
my $dbh = $dbh_marzipan;

$sth = $dbh->prepare('select * from customers order by balance desc;');
$sth->execute();

$sth2 = $dbh->prepare('select * from tab_log where customer_id = ? order by when_logged desc limit 1');

print "<table border=1 style='font-size: 75%;'>";
print "<tr>";
print "<th>id</th>";
print "<th>code</th>";
print "<th>name</th>";
print "<th>email</th>";
print "<th>phone</th>";
print "<th>addr</th>";
print "<th>balance</th>";
print "<th>limit</th>";
print "<th>went from</th>";
print "<th>to</th>";
print "<th>on</th>";
print "</tr>\n";

while (my @row = $sth->fetchrow_array) {
	print "<tr>";
	foreach $i (0..7) {
		print "<td>$row[$i]&nbsp;</td>";
	}
	$sth2->execute($row[0]);
	@row2 = $sth2->fetchrow_array;
	print "<td>$row2[2]</td>";
	print "<td>$row2[3]</td>";
	print "<td>$row2[4]</td>";
	print "</tr>\n";
}

print "</table>";
