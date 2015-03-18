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


# PERL DBI CONNECT
$dbh = DBI->connect($dsn, $user, $pw);

#my $distributor_ref = $dbh->selectall_hashref("select * from distributors", "id");
#my %distributors;

#foreach $k (keys %$distributor_ref) {
	#$distributors{$k} = $distributor_ref->{$k}->{'name'};
#}

#$distributors{0} = "";

$sth = $dbh->prepare("select count(distinct date(time_ended)) from sales");
$sth->execute();
my $days = ($sth->fetchrow_array())[0];

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
	return 0; #disable produce filter
	return $desc =~ m/$re/;
}

print "<html>\n\n";
print "<head>\n";
print '<style type="text/css">'."\n";
print ".bad { background-color: #f33; }\n";
print ".na { color: #aaa; }\n";
print ".out { background-color: #f77; }\n";
print ".low { background-color: #ff7; }\n";
print "* { font-size: 12px; }\n";
print "td,tr { line-height: 14px; height: 14px; border-top: 1px solid #bbb;}\n";
print "div.key span {padding: 4px;}\n";
print "table.sortable thead { background-color:#ddd; color:#333; font-weight: bold; cursor: default; }\n";
print "</style>\n";
print "<script src=\"../jquery-1.3.2.min.js\"></script>\n";
print '<script src="../sorttable.js"></script>'."\n";
print <<EOF;
<script type="text/javascript">
function filter() {
	var re = new RegExp(document.getElementById("re").value);
	var tbody = document.getElementById("item-stats");
	for (var i = 0; i < tbody.rows.length; ++i) {
		var tr = tbody.rows[i];
		var prod_td = tr.childNodes[0];
		if (prod_td.innerHTML.match(re)) {
			tr.style.display = '';
		} else {
			tr.style.display = 'none';
		}
	}
}
\$(document).ready(function() {
	filter();
	\$('#re').keypress(function() {
		filter();
	});
	\$('.amt').keypress(function(e) {
		if (e.which == 13) {
			var id = parseInt(this.name);
			\$.post('delivery.pl', { id: id, amt: \$(this).val() },
			       function(data) {
					\$('#'+id+'_amt').html(data);
					\$('#'+id+'_in').val('');
					if (parseFloat(data) < -10) {
						\$('#tr_'+id).removeClass('out').removeClass('bad').addClass('na');
					} else if (parseFloat(data) < -1) {
						\$('#tr_'+id).removeClass('na').removeClass('out').addClass('bad');
					} else if (parseFloat(data) < 1) {
						\$('#tr_'+id).removeClass('bad').removeClass('na').addClass('out');
					} else {
						\$('#tr_'+id).removeClass('bad').removeClass('out').removeClass('na');
					}
				}, 'text');
		}
	});
	\$('.itemnum').keypress(function(e) {
		if (e.which == 13) {
			var id = parseInt(this.name);
			\$.post('change_distributor.pl', { id: id, itemnum: \$(this).val() },
			       function() {}, 'text');
		}
	});
	\$('.distr').change(function() {
		var id = parseInt(this.name);
		\$.post('change_distributor.pl', {id: id, new_distr: \$(this).val()}, function() {}, 'text');
	});
});

</script>
EOF
print qq{</head><body>\n\n};

$sth = $dbh->prepare("
	select i.id, i.name, p.unit_cost, su.name, i.size, su2.name, i.barcode, i.barcode, i.barcode from items as i, prices as p, sale_units as su, sale_units as su2 where i.price_id = p.id and p.sale_unit_id = su.id and i.size_unit_id = su2.id and i.id < 6000 and i.id > 0 order by i.name;
		");
$sth->execute();

#foreach my $i (sort(keys(%distributors))) {
#	print "$i: $distributors{$i}<br/>";
#}

print qq{
<div class="key">
Key:
	<span class="na"> very negative (produce, etc.) </span>
	<span class="bad"> slightly negative (counting error?) </span>
	<span class="out"> out (0 in stock) </span>
	<span class="low"> &lt;14 day supply in stock </span>
</div>
<div>Click table headers to sort</div>
<div>Click distributor to change</div>
<div>Type and hit ENTER to change item number or to adjust quantity</div>
<div style="clear: both; height: 15px;"> </div>
};
#print qq{<br/></br><form action="?">\n};
#print "Filter: ";
print qq{<div style="display: none;"><input type="text" name="re" id="re"></div>\n};
#print qq{<input type="submit" value="Filter">\n};
#print qq{</form>\n};
print '<table border=0 class="sortable" cellspacing=0 cellpadding=0>';
print "<thead><tr>";
#print "<th>distributor</th>";
#print "<th>item #</th>";
print "<th>name</th>";
print "<th>size</th>";
print "<th>price</th>";
print "<th>7d</th>";
print "<th>14d</th>";
print "<th>30d</th>";
print "<th>#stocked</th>";
print "<th>+/-</th>";
print "<th>Open Produce SKU</th>";
print "<th>barcode</th>";
print "</thead><tbody id=\"item-stats\">\n";
#print '</tr><tr style="display: none;" id="total" style="background: black; color: red;"><td></td><td></td><td></td></tr>'."\n";

print qq{<form name="plus-minus">\n};
while (@row = $sth->fetchrow_array) {
	next if is_produce($row[1]);
	$sth2 = $dbh->prepare("select sum(quantity) from sale_items where item_id=$row[0]");
	$sth2->execute();
	$num_out = ($sth2->fetchrow_array())[0];
	$sth2 = $dbh->prepare("select sum(amount) from deliveries where item_id=$row[0]");
	$sth2->execute();
	$num_in = ($sth2->fetchrow_array())[0];
	$stocked = $num_in - $num_out;
	$sth3 = $dbh->prepare("select sum(si.quantity) from sale_items as si, sales as s where si.item_id=$row[0] and s.id=si.sale_id and date(s.time_ended) >= date_sub(now(), interval 7 day)");
	$sth3->execute();
	$d7 = ($sth3->fetchrow_array())[0] || 0;
	$sth3 = $dbh->prepare("select sum(si.quantity) from sale_items as si, sales as s where si.item_id=$row[0] and s.id=si.sale_id and date(s.time_ended) >= date_sub(now(), interval 14 day)");
	$sth3->execute();
	$d14 = ($sth3->fetchrow_array())[0] || 0;
	$sth3 = $dbh->prepare("select sum(si.quantity) from sale_items as si, sales as s where si.item_id=$row[0] and s.id=si.sale_id and date(s.time_ended) >= date_sub(now(), interval 30 day)");
	$sth3->execute();
	$d30 = ($sth3->fetchrow_array())[0] || 0;
	if ($stocked < -10.0) {
		print "<tr id=\"tr_$row[0]\" class=\"na\">";
	} elsif ($stocked < 0.0) {
		print "<tr id=\"tr_$row[0]\" class=\"bad\">";
	} elsif ($stocked < 1.0) {
		print "<tr id=\"tr_$row[0]\" class=\"out\">";
	} elsif ($stocked < $d14) {
		print "<tr id=\"tr_$row[0]\" class=\"low\">";
	} else {
		print '<tr>';
	}
	#my @distributor_ids = sort(keys(%distributors));
	#print "<td sorttable_customkey='$row[6]'>", popup_menu(-name=>"$row[0]_distr", -values=>\@distributor_ids, -default=>$row[6], -labels=>\%distributors, -class=>'distr', -id=>"$row[0]_distr"), "</td>";
	#print "<td sorttable_customkey='$row[7]' id=\"$row[0]_itemnum\" style=\"border-left: 1px solid #999; padding-left: 1em;\"><input class='itemnum' id='$row[0]_itemnum' name='$row[0]_itemnum' size=7 value='$row[7]'</td>";
	print "<td style='padding-left: 1em;'>", $row[1], "</td>";
	printf "<td>%.2f %s</td>", $row[4], $row[5];
	printf "<td>%.2f %s</td>", $row[2], $row[3];
	printf "<td>%.2f</td><td>%.2f</td><td>%.2f</td>", $d7, $d14, $d30;
	print "<td id=\"$row[0]_amt\" style=\"border-left: 1px solid #999; padding-left: 1em;\">", $stocked, "</td>";
	print qq{<td><input class="amt" id="$row[0]_in" name="$row[0]_in" size="2"/></td>\n};
	print "<td style='text-align: center;'> ", $row[0], "&nbsp;</td>";
	print "<td> ", $row[8], "&nbsp;</td>";
	print "</tr>\n";
}
print qq{</form>\n};
print "</tbody></table>\n";

print "</body></html>\n";
