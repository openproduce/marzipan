#!/usr/bin/env perl

use DBI;
use DBD::mysql;

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

my $dbh_marzipan = DBI->connect("dbi:mysql:register_tape:localhost:3306", 'root', '')
    or die "couldn't connect to database";
my $dbh = $dbh_marzipan;

	$sth_balance = $dbh_marzipan->prepare(qq{
			select id, name, balance from customers;
			}); 

	$sth_last_new = $dbh_marzipan->prepare(qq{
			select new_balance from tab_log where customer_id = ? and when_logged < ? order by when_logged desc limit 1;
			});

	$sth_next_old = $dbh_marzipan->prepare(qq{
			select old_balance from tab_log where customer_id = ? and when_logged > ? order by when_logged asc limit 1;
			});

=cut
	$sth_new = $dbh_marzipan->prepare(qq{
			select customers.id,name,new_balance,min(if(when_logged>'2010-01-10 01:00',NULL,timediff('2010-01-10 01:00', when_logged))) from customers left join tab_log on customers.id=customer_id where customer_id = ? group by customers.id;
			});


	$sth_old = $dbh_marzipan->prepare(qq{
			select customers.id,name,old_balance,min(if(when_logged<'2010-01-10 01:00',NULL,timediff(when_logged,'2010-01-10 01:00'))) from customers left join tab_log on customers.id=customer_id group by customers.id;
			});
=cut
	$sth_months = $dbh_marzipan->prepare(qq{
			select month(time_ended),year(time_ended) from sales where year(time_ended) > 2012 group by month(time_ended),year(time_ended) order by year(time_ended), month(time_ended)
			});
	$sth_months->execute();
	print '<head>';
	print '<script src="../sorttable.js"></script>'."\n";
	print '</head><body>';
	print "<table border=1>\n";

	while(my @m = $sth_months->fetchrow_array) {
		my $m = @m[0];
		my $y = @m[1];
		next unless $m < 13 and $m > 0;
		next if $m == 7 and $y == 2009;

		my $cutoff = "$y-$m-01 04:00";
		my $month = "Morning of $names{$m} 1st, $y";




	$sth_balance->execute();
	my $balance = 0;

#print '<table class="sortable">';
#print "<thead><tr><th>Customer</th><th>balance</th></tr></thead><tbody>\n";

	while (my @c = $sth_balance->fetchrow_array) {
#print "<tr><td>";
		next if $c[0] == 151;
#print "$c[1] ($c[0]): ";
		my $b = 0;
		$sth_last_new->execute($c[0], $cutoff);
		$sth_next_old->execute($c[0], $cutoff);
		if (my @new = $sth_last_new->fetchrow_array) { # there is a new_balance before cutoff
#print " NEW ";
			$b = $new[0];
		} elsif (@old = $sth_next_old->fetchrow_array) { # is there an old_balanace after the cutoff?
#print " OLD ";
			$b = $old[0];
		} else { # no log -- go with current customer balance
#print " BALANCE ";
			$b = $c[2];
		}

#print "</td><td style='text-align: right;' sorttable_customkey='" . int($b) . "'>", $b, "</td></tr>\n";

		$balance += $b;
	}

#print "</tbody></table></body>";

	print "<tr><td>$month</td><td>$balance</td></tr>\n";

}

print "</table>";
