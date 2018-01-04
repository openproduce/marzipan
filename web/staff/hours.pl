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
    print <<EOF;
<!doctype html>
<html>
<head>
<title>Dash board</title>
<style type="text/css">
    .check { width: 400px; height: 200px; }
    body {font-size: 14px; font-family: verdana;}
	td,th {border-bottom: 1px solid #999; padding-right: 1em;}
	.right {text-align: right}
	.bar {background-color: #9e9;}
	.total td {border-top: 7px solid #fff; border-bottom: none; background-color: #f99;}
	.tiny {font-size: 9px; line-height: 9px; padding-left: 1px; padding-right: 1px;}
	/*.gray {background-color: #ddd;}*/

</style>
</head>
<body>
EOF
my $dbh_marzipan = DBI->connect("dbi:mysql:marzipan:localhost:3306", 'marzipan', '')
    or die "couldn't connect to database";

	$sth = $dbh_marzipan->prepare(qq{
			select date(s.time_ended) as d,dayname(s.time_ended), hour(s.time_ended), sum(si.total),count(distinct s.id) from sales as s, sale_items as si
			where si.sale_id = s.id and (s.customer_id != 151 or s.customer_id
				is null) and s.is_void=0 and si.item_id not in (select id from
					items where name like '%tab payment%' or name like '%cash
					back%') 			group by d, hour(s.time_ended);
			}); 
	$sth->execute();

	print "<table border='0' cellspacing='0'>\n";
	print "<tr><th>Date</th><th>Dayname</th><th>Customers</th><th>\$/ring</th><th>Gross</th>\n";
	foreach my $h ((9..23), 0) {
		printf "<th style='padding-left: 1px; padding-right: 1px;' class='%s'>$h</th>", $h % 2 ? 'gray' : '';
	}
	print "</tr>\n";
	my $gross_total;
	my $last_added;
	my $count = 0;
    while (@row = $sth->fetchrow_array()) {
		my $day = $row[0];
		my $day_name = $row[1];
		if (($day ne $last_day and $row[2] ne '0') and $count > 0) { #it's a brand new day
			FINISH:
			print "<tr>";
			print "<td>$last_day</td>";
			print "<td>$last_day_name</td>";
			printf "<td><div class='bar' style='width: %dpx;'>$daily_customers</div></td>", $daily_customers/2;
			printf "<td><div class='bar' style='width: %dpx;'>%.2f</td>", $daily_dpr * 10, $daily_dpr;
			printf "<td><div class='bar' style='width: %dpx;'>$daily_gross<div style='width: 1px; margin-top: -1em; margin-left: 110px; border-top: 1em solid black'></div></div></td>", $daily_gross/10;


			foreach my $h ((9..23), 0) {
				printf "<td class='tiny%s' style='background-color: rgb(200,%d,200);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
					   $h % 2 ? ' gray' : '', 255 - $hour_gross{$h}*1.3, $hour_customers{$h}, $hour_dpr{$h}, $hour_gross{$h};
			}
			print "<td class='tiny' style='border: none;'>&larr;custs<br/>&larr;\$/ring<br/>&larr;gross</td>" if $day_count == 0;




			$total_gross += $daily_gross unless $day_count == 0 or ($finished and $day_count == 8);
			$total_customers += $daily_customers unless $day_count == 0 or ($finished and $day_count == 8);
			$total_dpr += $daily_dpr unless $day_count == 0 or ($finished and $day_count == 8);

			$daily_gross = 0;
			$daily_customers = 0;
			$daily_dpr = 0;
			%hour_gross = ();
			%hour_customers = ();
			%hour_dpr = ();
			print "</tr>\n";
			$day_count++;
		}


		$dayname = @row[1];

		$daily_gross += $row[3];
		$daily_customers += $row[4];
		$daily_dpr = ($daily_customers ? $daily_gross / $daily_customers : 0);

		$hour_gross{$row[2]} = $row[3];
		$hour_customers{$row[2]} = $row[4];
		$hour_dpr{$row[2]} = ($row[4] ? $row[3]/$row[4] : 0);

		$total_hour_gross{$row[2]} += $hour_gross{$row[2]} unless $day_count == 0 or ($finished and $day_count == 8);
		$total_hour_customers{$row[2]} += $hour_customers{$row[2]} unless $day_count == 0 or ($finished and $day_count == 8);
		$total_hour_dpr{$row[2]} += $hour_dpr{$row[2]} unless $day_count == 0 or ($finished and $day_count == 8);

		$last_day = $day unless $row[2] eq '0';
		$last_day_name = $day_name unless $row[2] eq '0';
		$count++;

	}
	unless (1 or $finished) { # one more time
		$finished = 1;
		goto FINISH;
	}
    print "</body></html>\n";
