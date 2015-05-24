#!/usr/bin/env perl
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

$sth = $dbh->prepare(qq{
		select balance from customers where id = 403
		});
$sth->execute();
@row = $sth->fetchrow_array;
$balance = $row[0];

print '<table border=1 class="sortable">';
print "<caption>Current balance: \$$balance</caption>\n";
print "<thead><tr>";
print "<th>Date/time</th>";
print "<th>Number</th>";
print "<th>Item</th>";
print "<th>Total</th>";
print "</tr></thead><tbody>\n";

$sth = $dbh->prepare(qq{
		select s.time_ended, si.quantity, i.name, si.total from sales as s, sale_items as si, inventory.items as i where s.id = si.sale_id and si.item_id = i.id and s.customer_id = 403 and payment = 4 order by s.time_ended desc
});

$sth->execute();

$old_time = 0;

while (@row = $sth->fetchrow_array) {
	print "<tr>";
	if ($old_time eq $row[0]) {
		print "<td> </td>";
	} else {
		print "<td>", $row[0], "</td>";
	}
	print "<td>", $row[1], "</td>";
	print "<td>", $row[2], "</td>";
	print "<td>", $row[3], "</td>";
	print "<td>", $row[4], "</td>";
	print "</tr>\n";
	$old_time = $row[0];
}

print "</tbody></table><br/>\n";
