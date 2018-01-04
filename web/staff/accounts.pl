#!/usr/bin/env perl

# This file is part of Marzipan, an open source point-of-sale system.
# Copyright (C) 2015 Open Produce LLC
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

use DBI;
use DBD::mysql;

print "Content-type: text/html\n\n";

$platform = "mysql";
$database = "register_tape";
$host = "localhost";
$port = "3306";
$user = "marzipan";
$pw = "";

$dsn = "dbi:mysql:$database:localhost:3306";
$dbh = DBI->connect($dsn, $user, $pw);

sub is_produce {
	my ($desc) = @_;
	my $re = join('|', (
		'^cherries', 'avocado', '^peaches', '^white peaches', 'bananas$',
		'apples?$', 'pear$|pears ', 'blackberries', 'blueberries',
		'^strawberries|organic straw', 'raspberries|blueberries', 'bargain',
		'nectarine', 'roma|tomatoes on vine|heirloom|grape tomatoes|campari',
		'grapes', 'fresh figs', 'broccoli', 'bell pepper', 'hungarian hot wax pepper',
		'habanero', 'jalapeno', 'lettuce', 'mango$|mangos', 'onions',
		'lemons', 'limes', 'cucumbers', 'squash', 'zucchini', 'pluot',
		'asparagus', 'white mushrooms', '^corn$', 'potatoes', 'arugula',
		'oranges', '^eggplant$', 'celery', 'carrots', '^grapefruit$',
		'garlic clove', 'plantains', 'sweet potato', '^kale$',
		'^lychee$', 'scallions', '^cilantro$', '^parsley$', '^basil$',
		'green beans', '^ginger$', 'collard', 'cabbage', 'honeydew',
		'currants', '^plums$', 'prune plums', 'shallots', '^leek$', 'longans',
		'\bpears$', 'de jong', 'kiwis', 'plums green', 'organic apples in bags',
		'^dill$', 'red pears', '^guava$', 'beets', 'apricots', 'chard',
		'fennel', 'cantaloupe', 'cauliflower', 'portobella', '^chives$',
		'lemongrass'
	));
	return $desc =~ m/$re/;
}

print "<html>\n\n";
print "<head>\n";
print qq{</head><body onload="filter();">\n\n};

print '<table border=1 class="sortable">';
print "<caption>Total sales</caption>\n";
print "<thead><tr>";
print "<th>Date</th>";
print "<th>cash</th>";
print "<th>check</th>";
print "<th>credit</th>";
print "<th>tab</th>";
print "<th>LINK</th>";
print "<th>total</th>";
print "</tr></thead><tbody>\n";

$sth = $dbh->prepare(qq{
select date(s.time_ended) as d,dayname(s.time_ended),case s.payment when 1 then "cash" when 2 then "check" when 3 then "credit" when 4 then "link" when 5 then "tab" end,sum(si.total),count(distinct s.id) from sales as s, sale_items as si where si.sale_id = s.id and s.is_void=0 and si.item_id not in (select id from inventory.items where name like '%tab payment%' or name like '%cash back%') and (customer_id <> 151 OR customer_id is null) and date(time_ended) > date '2009-12-31' group by d, s.payment
});
my $sth2 = $dbh->prepare(qq{select date(s.time_ended) as d,case s.payment when 1 then "cash" when 2 then "check" when 3 then "credit" when 4 then "tab" end,si.total from sale_items as si, sales as s where s.id=si.sale_id and s.is_void=0 and (customer_id <> 151 OR customer_id is null) and si.item_id in (select id from inventory.items where name like '%tab payment%') and date(time_ended) > date '2009-12-31' order by d;});

$sth->execute();
$sth2->execute();
sub clear_gross { map {$_=>[0,0]}("cash","check","tab","credit","link","total") }
my %gross = &clear_gross();
sub emit_row {
	my ($date, $day) = @_;
	print "<tr>";
	print "<td style=\"font-weight:bold;\">$date</td>";
	for my $pay (sort keys(%gross)) {
		next if $pay eq "";
		print "<td>", $gross{$pay}[0], "</td>";
	}
	print "</tr>\n";
	%gross = &clear_gross();
}

my %mtotal = ();
my $last_day = '';
my $last_date = '';
while (@row = $sth->fetchrow_array) {
	if ($last_date ne '' and $last_date ne $row[0]) {
		if ($last_date =~ /(\d+-\d+)/) {
			$mtotal{$1} += $gross{'total'}[0];
		}
		&emit_row($last_date, $last_day);
	}
	$gross{$row[2]} = [$row[3],$row[4]];
	$gross{'total'}[0] += $row[3];
	$gross{'total'}[1] += $row[4];
	$last_date = $row[0];
	$last_day = $row[1];
}
if ($last_date =~ /(\d+-\d+)/) {
	$mtotal{$1} += $gross{'total'}[0];
}
&emit_row($last_date, $last_day);
print "</tbody></table><br/>\n";

print "<table border=1><caption>Tab Payments</caption><thead>\n";
print "<tr><th>Date</th><th>Cash</th><th>Card</th><th>Check</th></tr></thead><tbody>\n";
my $sth = $dbh->prepare(qq{select date(s.time_ended) as d,case s.payment when 1 then "cash" when 2 then "check" when 3 then "credit" when 4 then "tab" end,si.total from sale_items as si, sales as s where s.id=si.sale_id and s.is_void=0 and si.item_id in (select id from inventory.items where name like '%tab payment%') and date(time_ended) > date '2009-08-01' order by d;});
$sth->execute();
my $last_date = undef;
my %by_meth = ("cash"=>0,"credit"=>0,"check"=>0,"tab"=>0);
sub emit_tab_row {
    print "<tr><td style=\"font-weight: bold;\">$last_date</td><td>$by_meth{cash}</td><td>$by_meth{credit}</td><td>$by_meth{check}</td></tr>\n";
    %by_meth = ("cash"=>0,"credit"=>0,"check"=>0,"tab"=>0);
}
while (@row = $sth->fetchrow_array) {
    if ($last_date and $row[0] ne $last_date) {
        &emit_tab_row();
    }
    $by_meth{$row[1]} += $row[2];
    $last_date = $row[0];
}
&emit_tab_row();
print "</tbody></table><br/>\n";
print "<table border=1><caption>Total Cash In (including tab payments)</caption><thead>\n";
print "<tr><th>Date</th><th>Cash In</th></tr></thead><tbody>\n";
$sth = $dbh->prepare(qq{select date(time_ended) as d,sum(total) from sales where is_void=0 and payment=1 and date(time_ended) > date '2009-08-01' group by d});
$sth->execute();
while (@row = $sth->fetchrow_array()) {
    print "<tr><td style=\"font-weight: bold\">$row[0]</td><td>$row[1]</td></tr>\n"
}
print "</tbody></table><br/>\n";

print "<table border=1><caption>Total Cash In (by month)</caption><thead>\n";
print "<tr><th>Month</th><th>Cash In</th></tr></thead><tbody>\n";
$sth = $dbh->prepare("select concat(year(time_ended),'-',month(time_ended)) as d, sum(total) from sales where payment=1 and is_void=0 and date(time_ended) > '2009-08-01' group by d;");
$sth->execute();
while (@row = $sth->fetchrow_array) {
    print "<tr><td style=\"font-weight:bold;\">$row[0]</td><td>$row[1]</td></tr>\n";
}
print "</tbody></table>";
print "</body></html>\n";
