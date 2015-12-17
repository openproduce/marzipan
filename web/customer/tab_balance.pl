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
use CGI qw/:standard/;

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

print '<table border=1 class="sortable">';
print "<caption></caption>\n";
print "<thead><tr>";
print "<th>Date/time</th>";
print "<th>Old Balance</th>";
print "<th>New Balance</th>";
print "</tr></thead><tbody>\n";

$sth = $dbh->prepare(qq{
		select l.when_logged, l.old_balance, l.new_balance from tab_log as l where l.customer_id = ? order by when_logged
});

$sth->execute(param('id'));

$old_time = 0;

while (@row = $sth->fetchrow_array) {
	print "<tr>";
	print "<td>", $row[0], "</td>";
	print "<td>", $row[1], "</td>";
	print "<td>", $row[2], "</td>";
	print "<td>", $row[3], "</td>";
	print "</tr>\n";
	$old_time = $row[0];
}

print "</tbody></table><br/>\n";
