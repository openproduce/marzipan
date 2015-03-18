#!/usr/bin/env perl
use DBI;
use DBD::mysql;
use CGI qw/:standard/;

print "Content-type: text/html\n\n";

$platform = "mysql";
$database = "register_tape";
$host = "localhost";
$port = "3306";
$user = "root";
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
