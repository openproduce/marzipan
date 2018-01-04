#!/usr/bin/env perl

use DBI;
use DBD::mysql;

my $dbh_marzipan = DBI->connect("dbi:mysql:register_tape:localhost:3306", 'root', '')
    or die "couldn't connect to database";
my %q = map { split /=/, $_ } split /\&/, $ENV{'QUERY_STRING'};

if ($q{'p'} eq 'check') {
    &view_check($q{'no'}, $q{'f'});
} else {
    print "Content-type: text/html\n\n";
    print <<EOF;
<!doctype html>
<html>
<head>
<title>Booze dash board</title>
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
    &browse_checks("Booze", "c.name like 'wine' or c.name like 'beer' or c.name like 'spirits'");
    &browse_checks("Beer sales only", "c.name like 'beer'");
    &browse_checks("Wine sales only", "c.name like 'wine'");
    &browse_checks("Spirits sales only", "c.name like 'spirits'");

    $sth3 = $dbh_marzipan->prepare("select s.time_ended, c.name, si.total, i.name from sale_items as si, sales as s, inventory.items as i, inventory.categories as c, inventory.category_items as ci where si.sale_id = s.id and si.item_id = i.id and i.id = ci.item_id and ci.cat_id = c.id and s.is_void=0 and (c.name like 'beer' or c.name like 'wine' or c.name like 'spirits') and s.time_ended >= (DATE(NOW()) - INTERVAL 7 DAY) order by s.time_ended desc");
    $sth3->execute;

    print "<p> </p><h1>Recent Sales</h1><table>\n";
    while (my @a = $sth3->fetchrow_array()) {
      print "<tr>\n";
      foreach (@a) {
        print "<td>$_</td>\n";
      }
      print "</tr>\n";
    }
    print "</table>\n";

}

$dbh->disconnect();

sub browse_checks {

$title = $_[0];
$sql_restrict = $_[1];
                          my %total_hour_gross;
                          my %total_hour_customers;
                          my %total_hour_dpr;

                          my %weekend_total_hour_gross;
                          my %weekend_total_hour_customers;
                          my %weekend_total_hour_dpr;

                          my %weekday_total_hour_gross;
                          my %weekday_total_hour_customers;
                          my %weekday_total_hour_dpr;

                            my $weekday_total_gross;
                            my $weekday_total_customers;
                            my $weekday_total_dpr;
                            my $weekday_days_count;

                            my $weekend_total_gross = 0;
                            my $weekend_total_customers = 0;
                            my $weekend_total_dpr = 0;
                            my $weekend_days_count = 0;

			my $daily_gross = 0;
			my $daily_customers = 0;
			my $daily_dpr = 0;
			my %hour_gross = ();
			my %hour_customers = ();
			my %hour_dpr = ();

my $total_gross = 0;
my $total_customers = 0;
my $total_dpr += 0;
my $day_count = 0;


my $finished = 0;

       $sth = $dbh_marzipan->prepare(qq{
			select date(s.time_ended) as d,dayname(s.time_ended), hour(s.time_ended), sum(si.total),count(distinct s.id) from sales as s, sale_items as si, inventory.categories as c, inventory.category_items as ci
			where si.item_id = ci.item_id and ci.cat_id = c.id and ($sql_restrict) and si.sale_id = s.id and (s.customer_id != 151 or s.customer_id
				is null) and s.is_void=0 and si.item_id not in (807, 909) and (date_sub(CURDATE(), interval 7 day) <= date(s.time_ended) or (date_sub(CURDATE(), interval 8 day) <= date(s.time_ended) and HOUR(s.time_ended) != 0 and HOUR(s.time_ended) !=1 and HOUR(s.time_ended) !=2 and HOUR(s.time_ended) !=3))
			group by d, hour(s.time_ended);
			}); 
	$sth->execute();

	print "<h1>$title</h1>\n";
	print "<table border='0' cellspacing='0'>\n";
	print "<tr><th>Date</th><th>Dayname</th><th>Customers</th><th>\$/ring</th><th>Gross</th>\n";
	foreach my $h ((6..23), 0, 1, 2) {
		printf "<th style='padding-left: 1px; padding-right: 1px;' class='%s'>$h</th>", $h % 2 ? 'gray' : '';
	}
	print "</tr>\n";
	my $gross_total = 0;
	my $last_added = 0;
	my $count = 0;
    while (@row = $sth->fetchrow_array()) {
		my $day = $row[0];
		my $day_name = $row[1];
		if (($day ne $last_day) and ($row[2] ne '0') and ($row[2] ne '1') and ($row[2] ne '2') and ($row[2] ne '3') and $count > 0) { #it's a brand new day
			FINISH:
			print "<tr>";
			print "<td>$last_day</td>";
			print "<td>$last_day_name</td>";
			printf "<td><div class='bar' style='width: %dpx;'>$daily_customers</div></td>", $daily_customers * 3;
			printf "<td><div class='bar' style='width: %dpx;'>%.2f</td>", $daily_dpr * 7, $daily_dpr;
			printf "<td><div class='bar' style='width: %dpx;'>$daily_gross<div style='width: 1px; margin-top: -1em; margin-left: 100px; border-top: 1em solid black'></div></div></td>", $daily_gross/ 3;


			foreach my $h ((6..23), 0, 1, 2) {
				my $t = 180; #threshold
				my $f = 2.95; #factor

				my $hg = $hour_gross{$h} * $f;
				my $a = $hg;
				$a = $t if $a > $t;
				my $b = $hg - $t;
				$b = 0 if $b < 0;
				printf "<td class='tiny%s' style='background-color: rgb(%d,%d,%d);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
					   $h % 2 ? ' gray' : '',
					   143 + $b,
					   239 - $a,
					   143,
					   $hour_customers{$h}, $hour_dpr{$h}, $hour_gross{$h};
			}
			print "<td class='tiny' style='border: none;'>&larr;custs<br/>&larr;\$/ring<br/>&larr;gross</td>" if $day_count == 0;




			$total_gross += $daily_gross unless $day_count == 0 or ($finished and $day_count == 8);
			$total_customers += $daily_customers unless $day_count == 0 or ($finished and $day_count == 8);
			$total_dpr += $daily_dpr unless $day_count == 0 or ($finished and $day_count == 8);

                       unless ($day_count == 0 or ($finished and $day_count == 8)) {
                          if ($day_name eq 'Sunday' or $day_name eq 'Saturday') {
                            $weekend_total_gross += $daily_gross; # unless $day_count == 0 or ($finished and $day_count == 8);
                            $weekend_total_customers += $daily_customers; # unless $day_count == 0 or ($finished and $day_count == 8);
                            $weekend_total_dpr += $daily_dpr; # unless $day_count == 0 or ($finished and $day_count == 8);
                            $weekend_days_count += 1;
                          } else {
                            $weekday_total_gross += $daily_gross; # unless $day_count == 0 or ($finished and $day_count == 8);
                            $weekday_total_customers += $daily_customers; # unless $day_count == 0 or ($finished and $day_count == 8);
                            $weekday_total_dpr += $daily_dpr; # unless $day_count == 0 or ($finished and $day_count == 8);
                            $weekday_days_count += 1;
                          }
                        }


			$daily_gross = 0;
			$daily_customers = 0;
			$daily_dpr = 0;
			%hour_gross = ();
			%hour_customers = ();
			%hour_dpr = ();
			print "</tr>\n";
			$day_count++;
		}


		$dayname = $row[1];

		$daily_gross += $row[3];
		$daily_customers += $row[4];
		$daily_dpr = ($daily_customers ? $daily_gross / $daily_customers : 0);

		$hour_gross{$row[2]} = $row[3];
		$hour_customers{$row[2]} = $row[4];
		$hour_dpr{$row[2]} = ($row[4] ? $row[3]/$row[4] : 0);

                       unless ($day_count == 0 or ($finished and $day_count == 8)) {
                        if ($day_name eq 'Saturday' or $day_name eq 'Sunday') {
                          $weekend_total_hour_gross{$row[2]} += $hour_gross{$row[2]}; # unless $day_count == 0 or ($finished and $day_count == 8);
                          $weekend_total_hour_customers{$row[2]} += $hour_customers{$row[2]}; # unless $day_count == 0 or ($finished and $day_count == 8);
                          $weekend_total_hour_dpr{$row[2]} += $hour_dpr{$row[2]}; # unless $day_count == 0 or ($finished and $day_count == 8);
                        } else {
                          $weekday_total_hour_gross{$row[2]} += $hour_gross{$row[2]}; # unless $day_count == 0 or ($finished and $day_count == 8);
                          $weekday_total_hour_customers{$row[2]} += $hour_customers{$row[2]}; # unless $day_count == 0 or ($finished and $day_count == 8);
                          $weekday_total_hour_dpr{$row[2]} += $hour_dpr{$row[2]}; # unless $day_count == 0 or ($finished and $day_count == 8);
                        }
                        }
                          $total_hour_gross{$row[2]} += $hour_gross{$row[2]} unless $day_count == 0 or ($finished and $day_count == 8);
                          $total_hour_customers{$row[2]} += $hour_customers{$row[2]} unless $day_count == 0 or ($finished and $day_count == 8);
                          $total_hour_dpr{$row[2]} += $hour_dpr{$row[2]} unless $day_count == 0 or ($finished and $day_count == 8);

		$last_day = $day unless ($row[2] eq '0' or $row[2] eq '1' or $row[2] eq '2' or $row[2] eq '3' );
		$last_day_name = $day_name unless ($row[2] eq '0' or $row[2] eq '1' or $row[2] eq '2' or $row[2] eq '3');
		$count++;

	}
	unless ($finished) { # one more time
		$finished = 1;
		goto FINISH;
	}
	printf "<tr class='total'><td colspan=2>Week average (7 days)</td></td><td>%d</td><td>%.2f</td><td>%.2f</td>", $total_customers/7, $total_dpr/7, $total_gross/7;
	foreach my $h ((6..23), 0, 1, 2) {
				my $t = 180; #threshold
				my $f = 2.95; #factor

				my $hg = $total_hour_gross{$h}/7 * $f;
				my $a = $hg;
				$a = $t if $a > $t;
				my $b = $hg - $t;
				$b = 0 if $b < 0;
				printf "<td class='tiny%s' style='background-color: rgb(%d,%d,%d);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
					   $h % 2 ? ' gray' : '',
					   143 + $b,
					   239 - $a,
					   143,
					   $total_hour_customers{$h}/7, $total_hour_dpr{$h}/7, $total_hour_gross{$h}/7;
             #printf "<td class='tiny%s' style='background-color: rgb(200,%d,200);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
#			   $h % 2 ? ' gray' : '', 255 - $total_hour_gross{$h}/7*1.3, $total_hour_customers{$h}/7, $total_hour_dpr{$h}/7, $total_hour_gross{$h}/7;
	}
	printf "<tr class='total'><td colspan=2>Weekday average ($weekday_days_count days)</td></td><td>%d</td><td>%.2f</td><td>%.2f</td>", $weekday_total_customers/$weekday_days_count, $weekday_total_dpr/$weekday_days_count, $weekday_total_gross/$weekday_days_count unless $weekday_days_count == 0;
	foreach my $h ((6..23), 0, 1, 2) {
				my $t = 180; #threshold
				my $f = 2.95; #factor

				my $hg = $weekday_total_hour_gross{$h}/$weekday_days_count * $f unless $weekday_days_count == 0;
				my $a = $hg;
				$a = $t if $a > $t;
				my $b = $hg - $t;
				$b = 0 if $b < 0;
				printf "<td class='tiny%s' style='background-color: rgb(%d,%d,%d);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
					   $h % 2 ? ' gray' : '',
					   143 + $b,
					   239 - $a,
					   143,
					   $weekday_total_hour_customers{$h}/$weekday_days_count, $weekday_total_hour_dpr{$h}/$weekday_days_count, $weekday_total_hour_gross{$h}/$weekday_days_count unless $weekday_days_count == 0;
             #printf "<td class='tiny%s' style='background-color: rgb(200,%d,200);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
#			   $h % 2 ? ' gray' : '', 255 - $total_hour_gross{$h}/7*1.3, $total_hour_customers{$h}/7, $total_hour_dpr{$h}/7, $total_hour_gross{$h}/7;
	}
	printf "<tr class='total'><td colspan=2>Fri/Sat average ($weekend_days_count days)</td></td><td>%d</td><td>%.2f</td><td>%.2f</td>", $weekend_total_customers/$weekend_days_count, $weekend_total_dpr/$weekend_days_count, $weekend_total_gross/$weekend_days_count unless $weekend_days_count == 0;
	foreach my $h ((6..23), 0, 1, 2) {
				my $t = 180; #threshold
				my $f = 2.95; #factor

				my $hg = $weekend_total_hour_gross{$h}/$weekend_days_count * $f unless $weekend_days_count == 0;
				my $a = $hg;
				$a = $t if $a > $t;
				my $b = $hg - $t;
				$b = 0 if $b < 0;
				printf "<td class='tiny%s' style='background-color: rgb(%d,%d,%d);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
					   $h % 2 ? ' gray' : '',
					   143 + $b,
					   239 - $a,
					   143,
					   $weekend_total_hour_customers{$h}/$weekend_days_count, $weekend_total_hour_dpr{$h}/$weekend_days_count, $weekend_total_hour_gross{$h}/$weekend_days_count unless $weekend_days_count == 0;
             #printf "<td class='tiny%s' style='background-color: rgb(200,%d,200);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
#			   $h % 2 ? ' gray' : '', 255 - $total_hour_gross{$h}/7*1.3, $total_hour_customers{$h}/7, $total_hour_dpr{$h}/7, $total_hour_gross{$h}/7;
	}
	print "</tr>\n";
	print "</table>\n";


	#$sth = $dbh_marzipan->prepare(qq{
			#select date(s.time_ended) as d,dayname(s.time_ended), hour(s.time_ended), sum(si.total),count(distinct s.id) from sales as s, sale_items as si, inventory.categories as c, inventory.category_items as ci
			#where si.item_id = ci.item_id and ci.cat_id = c.id and (c.name like 'beer') and si.sale_id = s.id and (s.customer_id != 151 or s.customer_id
				#is null) and s.is_void=0 and si.item_id not in (807, 909) and (date_sub(CURDATE(), interval 7 day) <= date(s.time_ended) or (date_sub(CURDATE(), interval 8 day) <= date(s.time_ended) and HOUR(s.time_ended) != 0 and HOUR(s.time_ended) !=1 and HOUR(s.time_ended) !=2 and HOUR(s.time_ended) !=3))
			#group by d, hour(s.time_ended);
			#}); 
	#$sth->execute();
}
