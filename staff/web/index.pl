#!/usr/bin/perl

# PERL MODULES WE WILL BE USING
use DBI;
use DBD::mysql;

# HTTP HEADER
print "Content-type: text/html\n\n";

# CONFIG VARIABLES
$platform = "mysql";
$database = "marzipan";
$host = "localhost";
$port = "3306";
$user = "root";
$pw = "";

#DATA SOURCE NAME
$dsn = "dbi:mysql:$database:localhost:3306";


# PERL DBI CONNECT
$dbh = DBI->connect($dsn, $user, $pw);

sub is_produce {
	my ($desc) = @_;
	my $re = join('|', (
		'^cherries', 'avocado', '^peaches', '^white peaches', 'bananas$',
		'apples?$', '^apples ', 'pear$|pears ', 'blackberries', 'blueberries',
		'^strawberries|organic straw', 'raspberries|blueberries', 'bargain',
		'nectarine', 'roma|tomatoes on vine|heirloom|grape tomatoes|campari',
		'^beefsteak tomato$', '^brussel sprouts$',
		'^baby bella mushrooms$', '^baby bok choy$', '^beefsteak tomato$',
		'^brussel sprouts$', '^bunch mint$', '^bunch rosemary$',
		'^cactus fruit$', '^cara cara orange$', '^chestnuts$', '^chinese garlic$',
		'^clementines$', '^clementines (box)$', '^cranberries$',
		'^cranberries - ocean spray$', '^cranberries - Paradise Meadow fresh bagged$',
		'^earthbound farm organic fresh herb salad$',
		'^earthbound farm organic mixed baby greens$',
		'^greens$', '^hazel farms tomato rhapsody$', '^hurst\'s gooseberries$',
		'^jerusalem artichokes$', '^kumato brown tomato$', '^kumquat$',
		'^m.d. basciani and sons gourmet baby bella$',
		'^mama mia mini sweet tomato$', '^MamaMia tiny tomatoes - organic,clamshell$',
		'^mamamia yellow cherry tomatoes$', '^mananita papaya$', '^mushroom$',
		'^organic golden delicious$', '^organic baby bella$', '^pie pumpkins$',
		'^pomegranate$', 'grapes', 'fresh figs', 'broccoli', 'bell pepper', 'hungarian hot wax pepper',
		'habanero', '^jalapeno', 'lettuce', 'mango$|mangos', 'onions',
		'lemons', 'limes', 'cucumbers', 'squash', 'zucchini', 'pluot',
		'asparagus', 'white mushrooms', '^corn$', 'potatoes', 'arugula',
		'oranges', '^eggplant$', 'celery', 'carrots', '^grapefruit$',
		'garlic clove', 'plantains', 'sweet potato', '^kale$',
		'^lychee$', 'scallions', '^cilantro$', '^parsley$', '^basil$',
		'green beans', '^ginger$', 'collard', 'cabbage$', 'honeydew',
		'currants', '^plums$', 'prune plums', 'shallots', '^leek$', 'longans',
		'\bpears$', 'de jong', 'kiwis', 'plums green', 'organic apples in bags',
		'^dill$', 'red pears', '^guava$', 'beets', 'apricots', 'chard',
		'fennel$', 'cantaloupe', 'cauliflower', 'portobella', '^chives$',
		'lemongrass', '^pomegranate$', '^watermelon$', '^pummelos$', '^clementines$',
		'^tangerine$', '^american garlic$', '^chestnuts$', '^decorative pumpkin$',
		'^straw berries$', '^quince$', '^cactus fruit$',
		'^persimmon - fuyu$', '^cranberries$', '^rutabaga$', '^baby bella mushrooms$',
		'^potato - white$', '^kumquat$', '^dried chiles', '^organic baby bella$',
		'^cara cara orange$', '^tomatillo$', 'papayas$', '^watercress$', 'bok choy$',
		'^potato - fingerling$', '^potato - white$', '^pummelos$', '^pumpkin$',
		'^quince$', '^rhubarb$', '^rutabaga$', '^sage$', '^salad mix$', '^shiitake fresh$',
		'^snap peas$', '^star fruit$', '^sprouts bag$', '^straw berries$', '^sugar cane$', '^thyme$',
		'^thai peppers - fresh$', '^tomatillo$', '^watercress$', '^watermelon$',
	));
	return $desc =~ m/$re/;
}

$sth = $dbh->prepare("select count(distinct date(time_ended)) from sales where is_void=0");
$sth->execute();
my $days = ($sth->fetchrow_array())[0];


print "<html>\n\n";
print "<head>\n";
print '<script src="/sorttable.js"></script>'."\n";
print <<EOF;
<script type="text/javascript">
function filter() {
	var re = new RegExp(document.getElementById("re").value);
	var tbody = document.getElementById("item-stats");
	var total = { qty:0, stdev:0, sales:0, cost:0, gross:0 };
	var n = 0;
	for (var i = 0; i < tbody.rows.length; ++i) {
		var tr = tbody.rows[i];
		var prod_td = tr.childNodes[4];
		if (prod_td.innerHTML.match(re)) {
			tr.style.display = '';
			total.qty += parseFloat(tr.childNodes[0].innerHTML);
			total.stdev += parseFloat(tr.childNodes[1].innerHTML);
			total.sales += parseFloat(tr.childNodes[2].innerHTML);
			total.cost += parseFloat(tr.childNodes[3].innerHTML);
			total.gross += parseFloat(tr.childNodes[5].innerHTML);
			n++;
		} else {
			tr.style.display = 'none';
		}
	}
	var tr = document.getElementById("total");
	tr.childNodes[0].innerHTML = total.qty.toFixed(2);
	tr.childNodes[1].innerHTML = (total.stdev/n).toFixed(2);
	tr.childNodes[2].innerHTML = total.sales.toFixed(2);
	tr.childNodes[3].innerHTML = (total.cost/n).toFixed(2);
	tr.childNodes[5].innerHTML = total.gross.toFixed(2);
}
</script>
EOF
print qq{</head><body onload="filter();">\n\n};

if ($ENV{'QUERY_STRING'} eq 'sales') {
	$sth = $dbh->prepare("select id, date(time_ended) as d, hour(time_ended) as h, total from sales where is_void=0 order by concat(d,if(h<10,concat('0',h),h)) desc, total desc;");
	$sth->execute();
	print <<EOF;
	<script type="text/javascript">
	function toggle(id) {
		var elt = document.getElementById(id);
		if (elt.style.display == "block") {
			elt.style.display = "none";
		} else {
			elt.style.display = "block";
		}
	}
	</script>
EOF
	print "<table border=1><thead>\n";
	print qq{<tr><th>Date</th><th>Hour</th><th>Sales</th></tr>\n};
	print qq{</thead><tbody>\n};
	my $last_hour = undef;
	my $last_date = undef;
	my $dark = sub { qq{style="{background-color: #cccccc;}"} };
	my $light = sub { qq{style="{background-color: #ffffff;}"} };
	my $bg = $dark;
	my @data = ();
	while (@row = $sth->fetchrow_array) {
		$sq = $dbh->prepare("select i.name,si.quantity,si.unit_cost,si.total from sale_items as si, items as i where i.id = si.item_id and si.sale_id = $row[0]");
		$sq->execute();
		if ($last_date ne $row[1]) {
			$bg = $bg == $dark ? $light : $dark;
		}
		if ($last_hour != $row[2]) {
			print "</td></tr>" if defined $last_hour;
			my $bc = $bg->();
			print qq{<tr $bc><td>$row[1]</td><td>$row[2]</td><td>\n};
		}
		print qq{<table border=1 style="float: left;">};
		print qq{<thead><tr><th colspan=3 onclick="toggle('body-$row[0]');">$row[3]</th></tr></thead>\n};
		print qq{<tbody id="body-$row[0]" style="display:none;">\n};
		my $prod_total = 0;
		while (@r2 = $sq->fetchrow_array) {
			print "<tr><td>$r2[3]</td><td>$r2[0]</td><td>$r2[1]</td></tr>";
			$prod_total += $r2[3] if is_produce($r2[0]);
		}
		push @data, [$row[3], $prod_total];
		print "</tbody></table>";
		$last_hour = $row[2];
		$last_date = $row[1];
	}
	print "</td></tr>";
	print "</table>";
	#print "<pre>";
	#foreach my $r (@data) {
	#	print "$r->[0] $r->[1]\n";
	#}
	#print "</pre>";
	exit 0;
} elsif ($ENV{'QUERY_STRING'} eq 'items') {
	$sth=$dbh->prepare("select distinct date(time_ended) as d from sales order by d desc limit 30;");
	$sth->execute();
	my @dates = ();
	while (@row = $sth->fetchrow_array) { push @dates, $row[0]; }
	my $ds=join(',',map {"'$_'"} @dates);
	my @items = ();
	$sth=$dbh->prepare("select si.item_id,i.name,sum(si.total) as t from sale_items as si, sales as s, items as i where i.id=si.item_id and s.id=si.sale_id and s.is_void=0 and date(s.time_ended) in ($ds) group by si.item_id order by t desc;");
	$sth->execute();
	while (@row = $sth->fetchrow_array) { push @items, [@row]; }
	print qq[<table border=1><thead><tr><th style="{min-width: 400px;}">Item&nbsp;Description</th><th>Gross</th>];
	foreach my $d (@dates) {
		my $k = $d;
		$k=~s/^\d{4}-//;
		print "<th>$k</th>";
	}
	print "</tr></thead><tbody>\n";
	for my $i (@items) {
		my ($id, $n, $t) = @$i;
		print qq{<tr><td>$n</td><td>$t</td>};
		my $query = "select sum(si.quantity),date(s.time_ended) as d from sale_items as si, sales as s where si.sale_id=s.id and si.item_id=$id and s.is_void=0 and date(s.time_ended) in ($ds) group by d;";
		$sth=$dbh->prepare($query);
		$sth->execute();
		my %bd = ();
		while (@row=$sth->fetchrow_array) {
			$bd{$row[1]} = $row[0];
		}
		foreach my $d (@dates) {
			printf "<td>%.2f</td>", $bd{$d} || 0;
		}
		print "</tr>\n";
	}
	print "</tbody></table>\n";
	exit 0;
}

sub profits { 
	print "<table border=1>";
	print "<thead><tr><th>Date</th><th>Gross</th><th>Net(?=0%)</th><th>margin(?=0%)</th><th>Net(?=20%)</th><th>margin(?=20%)</th></tr></thead><tbody>\n";
	$sth = $dbh->prepare("select date(s.time_ended),si.total,m.percent from sale_items as si left join margins as m on si.item_id=m.item_id, sales as s where s.id=si.sale_id and s.is_void=0 and si.item_id not in (select id from items where name like '%tab payment%');");
$sth->execute();
	my $last = undef;
	my $gross = 0;
	my $net0 = 0;
	my $net20 = 0;
	my $emit = sub {
		printf "<tr><td>$last</td><td>%.2f</td><td>%.2f</td><td>%.3f</td><td>%.2f</td><td>%.3f</td><td><div style=\"{width: %dpx; background: blue;}\">&nbsp;</div></tr>\n", $gross, $net0, $net0/$gross, $net20, $net20/$gross, $net20/5.0;
		$gross = $net0 = $net20 = 0;
	};
	while (@row = $sth->fetchrow_array) {
		if ($last and $last ne $row[0]) { $emit->(); }
		$last = $row[0];
		$gross += $row[1];
		$net0 += $row[2] ? ($row[2]/100.0)*$row[1] : 0;
		$net20 += $row[2] ? ($row[2]/100.0)*$row[1] : .2*$row[1];
	}
	$emit->();
	print "</tbody></table><br/>\n";
}

profits();

print '<table border=1 class="sortable">';
print "<thead><tr>";
print "<th>date</th>";
print "<th>day</th>";
print "<th>cash gross</th>";
print "<th>cash sales</th>";
print "<th>check gross</th>";
print "<th>check sales</th>";
print "<th>credit gross</th>";
print "<th>credit sales</th>";
print "<th>tab gross</th>";
print "<th>tab sales</th>";
print "<th>total gross</th>";
print "<th>total sales</th>";
print "<th>ring</th>";
print "<th></th>";
print "</tr></thead><tbody>\n";

	$sth = $dbh->prepare(qq{
select date(s.time_ended) as d,dayname(s.time_ended),case s.payment when 1 then "cash" when 2 then "check" when 3 then "credit" when 4 then "tab" end,sum(si.total),count(distinct s.id) from sales as s, sale_items as si where si.sale_id = s.id and s.is_void=0 and si.item_id not in (select id from items where name like '%tab payment%' or name like '%cash back%') group by d, s.payment
});

	$sth->execute();
sub clear_gross { map {$_=>[0,0]}("cash","check","tab","credit","total") }
my %gross = &clear_gross();
sub emit_row {
	my ($date, $day) = @_;
	print "<tr>";
	print "<td>$date</td>";
	print "<td>$day</td>";
	for my $pay (sort keys(%gross)) {
		next if $pay eq "";
		print "<td>", $gross{$pay}[0], "</td>";
		print "<td>", $gross{$pay}[1], "</td>";
	}
	printf "<td>%.2f</td>\n", $gross{'total'}[1] ?
		$gross{'total'}[0]/$gross{'total'}[1] : 0;
	printf qq{<td><div style="{width: %dpx; background:blue;}">&nbsp;</div></td>},
		$gross{'total'}[0]/10.0;
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
print "</tbody></table>\n";

$sth = $dbh->prepare("
select date(s.time_ended) as d,i.name,si.total from sales as s, sale_items as si, items as i where si.sale_id = s.id and s.is_void=0 and i.id = si.item_id order by d");
$sth->execute();
my %mproduce;
while (@row = $sth->fetchrow_array) {
	if (is_produce($row[1]) and $row[0] =~ /(\d+-\d+)/) {
		$mproduce{$1} += $row[2];
	}
}

print "<br/><br/><table border=1><thead><tr><th>Month</th><th>Gross</th><th>Produce Gross</th><th></th></tr></thead>\n";
print "<tbody>\n";
for my $mo (sort keys %mtotal) {
	printf qq[<tr><td>%s</td><td>%.2f</td><td>%.2f</td><td><div style="{width: %dpx; background:blue;}">&nbsp</div></td></tr>\n], $mo, $mtotal{$mo}, $mproduce{$mo}, $mtotal{$mo}/100;
}
print "</tbody></table>";

print "<br/><br/><table border=1><thead><tr><th>\$/ring</th><th>Sales/day</th><th>\$/day</th></tr></thead>\n";
print "<tbody>\n";
$sth = $dbh->prepare("
select truncate(total,0) as t,count(*),sum(total) from sales where is_void=0 group by t;
");
$sth->execute();
while (@row = $sth->fetchrow_array) {
	printf qq{<tr><td>%s</td><td>%.2f</td><td><div style="{width: %dpx; background: blue;}">&nbsp;</div></td></tr>\n}, $row[0], $row[1]/$days, 5*$row[2]/$days;
}
print "</tbody></table>";

$sth = $dbh->prepare("
select hour(time_ended) as h,sum(total) from sales where is_void=0 group by h
");
$sth->execute();
print "<br/><br/><table border=1><thead><tr><th>Hour</th><th>Gross</th><th></th></tr></thead><tbody>\n";
while (@row = $sth->fetchrow_array) {
	printf qq{<tr><td>%s</td><td>%.2f</td><td><div style="{width: %dpx; background: blue;}">&nbsp;</div></td></tr>\n}, $row[0], $row[1]/$days, 2*$row[1]/$days;
}
print "</tbody></table>\n";

$sth = $dbh->prepare("
select dayname(time_ended) as h,sum(total) from sales where is_void=0 group by h order by weekday(time_ended)
");
$sth->execute();
print "<br/><br/><table border=1><thead><tr><th>Day</th><th>Gross</th><th></th></tr></thead><tbody>\n";
while (@row = $sth->fetchrow_array) {
	printf qq{<tr><td>%s</td><td>%.2f</td><td><div style="{width: %dpx; background: blue;}">&nbsp;</div></td></tr>\n}, $row[0], $row[1]/($days/7), 0.5*$row[1]/($days/7);
}
print "</tbody></table>\n";

$sth = $dbh->prepare("select name, balance from customers where balance != 0 order by balance desc");
print "<br/><br/><table border=1><thead><tr><th>Customer</th><th>Balance</th></tr></thead>\n";
print "<tbody>\n";
$sth->execute();
while (@row = $sth->fetchrow_array()) {
	printf qq{<tr><td>%s</td><td>%.2f</td><td><div style="{width: %dpx; background: blue;}">&nbsp;</div></td></tr>\n}, $row[0], $row[1], $row[1]/4;
}
print "</tbody></table>\n";

$sth = $dbh->prepare("
select cc_name,count(*),sum(total) as t from sales where payment=3 and is_void=0 group by cc_name order by t desc");
print "<br/><br/><table border=1 class=\"sortable\"><thead><tr><th>Card Name</th><th>Visits</th><th>Total</th><th></th></tr></thead>\n";
print "<tbody>\n";
$sth->execute();
while (@row = $sth->fetchrow_array()) {
	printf qq{<tr><td>%s</td><td>%d</td><td>%.2f</td><td><div style="{width: %dpx; background: blue;}">&nbsp;</div></td></tr>\n}, $row[0]||"Unknown", $row[1], $row[2], $row[2]/5;
}
print "</tbody></table>\n";


$sth = $dbh->prepare("
select sum(si.quantity),stddev(si.quantity),count(*),avg(si.unit_cost),i.name,sum(si.total) as t,m.percent from sale_items as si left join margins as m on si.item_id=m.item_id, items as i, sales as s where s.id=si.sale_id and s.is_void=0 and i.id=si.item_id and i.name not like '%tab payment' and i.name not like '%cash back%' group by i.id order by t desc;");
$sth->execute();

print qq{<br/></br><form action="javascript: filter();">\n};
print qq{<input type="text" name="re" id="re">\n};
print qq{<input type="submit" value="Filter">\n};
print qq{</form>\n};
print '<table border=1 class="sortable">';
print "<thead><tr>";
print "<th>quantity/day</th>";
print "<th>stdev</th>";
print "<th># of sales</th>";
print "<th>unit cost (avg)</th>";
print "<th>description</th>";
print "<th>gross sales</th>";
print "<th>margin</th>";
print '</tr><tr id="total" style="background: black; color: red;"><td></td><td></td><td></td><td></td><td></td><td></td></tr>'."\n";
print "</thead><tbody id=\"item-stats\">\n";

my @pi = ();
my $produce_gross = 0;
while (@row = $sth->fetchrow_array) {
	print "<tr>";
	printf "<td>%.2f</td>", $row[0]/$days;
	printf "<td>%.2f</td>", $row[1];
	print "<td>", $row[2], "</td>";
	printf "<td>%.2f</td>", $row[3];
 	my $style = "";
	if (is_produce($row[4])) {
		$style = ' style="{background:green;}"';
		$produce_gross += $row[5];
		push @pi, $row[6];
	}
	print "<td $style>", $row[4], "</td>";
	print "<td>", $row[5], "</td>";
	print "<td>", $row[6] || 'unknown', "</td>";
	print "</tr>\n";
}
print "</tbody></table>\n";

#	foreach my $item (@pi) {
#		$sth = $dbh->prepare("insert into category_items(cat_id, item_id) values (1, $item);");
#		$sth->execute();
#	}


print "</body></html>\n";
