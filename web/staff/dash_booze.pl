#!/usr/bin/env perl

use FindBin;  
use lib $FindBin::Bin;   

use DBI;
use DBD::mysql;

use DBCreds;
$DB_USER="marzipan";
our $DB_PASSWORD;


my $dbh_marzipan = DBI->connect("dbi:mysql:register_tape:localhost:3306", $DB_USER, $DBCreds::DB_PASSWORD)
    or die "couldn't connect to database";
my $dbh_inventory = DBI->connect("dbi:mysql:inventory:localhost:3306", $DB_USER, $DBCreds::DB_PASSWORD)
    or die "couldn't connect to database";

#$sth3 = $dbh_marzipan->prepare("select s.time_ended, c.name, si.total, i.name from sale_items as si, sales as s, inventory.items as i, inventory.categories as c, inventory.category_items as ci where si.sale_id = s.id and si.item_id = i.id and i.id = ci.item_id and ci.cat_id = c.id and s.is_void=0 and (c.name like 'beer' or c.name like 'wine' or c.name like 'spirits') and s.time_ended >= (DATE(NOW()) - INTERVAL 7 DAY) order by s.time_ended desc");
#				(c.name like 'beer' or c.name like 'wine' or c.name like 'spirits')");
# c.name, cis.time_ended, c.name, si.total, i.name from sale_items as si, sales as s, inventory.items as i, inventory.categories as c, inventory.category_items as ci where si.sale_id = s.id and si.item_id = i.id and i.id = ci.item_id and ci.cat_id = c.id");

#$total_hours = $sth3->rows();

#$sth3->execute or die "couldn't do database";



print "Content-type: text/html\n\n";
print <<EOF;
    <!doctype html>
    <html>
    <head>
    <title>Booze Dash</title>
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


sub browse_checks {

    $title = $_[0];
$sql_restrict = $_[1];

	print "<h1>$title</h1>\n";
    
# print table headers
print "<table border='0' cellspacing='0'>\n";
print "<tr><th>Date</th><th>Dayname</th><th>Customers</th><th>\$/ring</th><th>Gross</th>\n";
foreach my $h ((6..23), 0, 1, 2) {
    printf "<th style='padding-left: 1px; padding-right: 1px;' class='%s'>$h</th>", $h % 2 ? 'gray' : '';
}
print "</tr>\n";

my $count = 0;

$sth3 = $dbh_marzipan->prepare("select date(s.time_ended) as d, 
    dayname(s.time_ended) as dn, 
    hour(s.time_ended) as hour, 
    sum(si.total),count(distinct s.id) from sales as s, sale_items as si, inventory.items as i, inventory.categories as c,inventory.category_items as ci
    where si.sale_id = s.id and si.item_id = i.id and i.id = ci.item_id and ci.cat_id = c.id and s.is_void=0 and ($sql_restrict)		  and (date_sub(CURDATE(), interval 6 day) <= date(s.time_ended) 
    or (date_sub(CURDATE(), interval 7 day) <= date(s.time_ended) 
    and HOUR(s.time_ended) != 0 and HOUR(s.time_ended) !=1 
    and HOUR(s.time_ended) !=2 and HOUR(s.time_ended) !=3))

    and s.time_ended >= (DATE(NOW()) - INTERVAL 7 DAY) 				  group by d, hour, dn");
$sth3->execute;

# run once to get count, i GUESS
$sth3->execute() or die "Unable to execute " . $sth3->errstr;
$total_hours = $sth3->rows();    
$sth3->execute() or die "Unable to execute " . $sth3->errstr;

# use the count so we don't have to use the goto
# we're doing it n+1 times so we can wrap up the current day
for ($i = 0; $i <= $total_hours; $i++) {

    @row = $sth3->fetchrow_array();


$day = $row[0];
$day_name = $row[1];

calculate_totals($row);

# make sure sales from midnite-4am are in the last day's thing
if ((($day ne $last_day) and ($row[2] ne '0') and ($row[2] ne '1') and ($row[2] ne '2') and ($row[2] ne '3') and $count > 0)) {
    #it's a brand new day
    # print out everything we calculated by looping over the day's sales
    

    print "<tr>";
print "<td>$last_day</td>";
print "<td>$last_day_name</td>";
printf "<td><div class='bar' style='width: %dpx;'>$daily_customers</div></td>", $daily_customers/3;
printf "<td><div class='bar' style='width: %dpx;'>%.2f</td>", $daily_dpr * 10, $daily_dpr;
printf "<td><div class='bar' style='width: %dpx;'>$daily_gross<div style='width: 1px; margin-top: -1em; margin-left: 100px; border-top: 1em solid black'></div></div></td>", $daily_gross/15;

# print each hour of the day, colorized
foreach my $h ((6..23), 0, 1, 2) {
    my $t = 180; #threshold
my $f = 0.95; #factor

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

# side legend for table
print "<td class='tiny' style='border: none;'>&larr;custs<br/>&larr;\$/ring<br/>&larr;gross</td>" if $day_count == 0;

# skip this if today, unfinished days will mess up averages
unless ($day_count == 7) {
    # add daily totals to weekly totals
    $total_gross += $daily_gross; 
$total_customers += $daily_customers; 
$total_dpr += $daily_dpr; 

# add daily totals to weekly totals, separated by weekday/weekend
if ($last_day_name eq 'Saturday' or $last_day_name eq 'Sunday') { 
    $weekend_total_gross += $daily_gross; 
$weekend_total_customers += $daily_customers; 
$weekend_total_dpr += $daily_dpr; 
$weekend_days_count += 1;
} else {
    $weekday_total_gross += $daily_gross; 
$weekday_total_customers += $daily_customers; 
$weekday_total_dpr += $daily_dpr; 
$weekday_days_count += 1;
}
}

# reset daily variables for next go-round
$daily_gross = 0;
$daily_customers = 0;
$daily_dpr = 0;
%hour_gross = ();
%hour_customers = ();
%hour_dpr = ();


print "</tr>\n";
$day_count++ unless ($day_count == 7);

} # close day

$last_day = $day unless ($row[2] eq '0' or $row[2] eq '1' or $row[2] eq '2' or $row[2] eq '3' );
$last_day_name = $day_name unless ($row[2] eq '0' or $row[2] eq '1' or $row[2] eq '2' or $row[2] eq '3');
$count++;


} # done with sql loop, now we have numbers for bottom totals

print_bottom_rows();

# all done!
print "</tr>\n";
print "</table>\n";
}



sub calculate_totals {
    $row = $_[0];


# start addin' it up
$day_name = $row[1];
$daily_gross += $row[3];
$daily_customers += $row[4];
$daily_dpr = ($daily_customers ? $daily_gross / $daily_customers : 0);

$hour_gross{$row[2]} = $row[3];
$hour_customers{$row[2]} = $row[4];
$hour_dpr{$row[2]} = ($row[4] ? $row[3]/$row[4] : 0);


if ($day_name eq 'Saturday' or $day_name eq 'Sunday') {
    $weekend_total_hour_gross{$row[2]} += $hour_gross{$row[2]}; 
$weekend_total_hour_customers{$row[2]} += $hour_customers{$row[2]}; 
$weekend_total_hour_dpr{$row[2]} += $hour_dpr{$row[2]}; 
} else {
    $weekday_total_hour_gross{$row[2]} += $hour_gross{$row[2]}; 
$weekday_total_hour_customers{$row[2]} += $hour_customers{$row[2]}; 
$weekday_total_hour_dpr{$row[2]} += $hour_dpr{$row[2]}; 
}


$total_hour_gross{$row[2]} += $hour_gross{$row[2]}; 
$total_hour_customers{$row[2]} += $hour_customers{$row[2]}; 
$total_hour_dpr{$row[2]} += $hour_dpr{$row[2]};


}

sub print_bottom_rows() {
    # bottomnal data (colorized averages for full week)

    printf "<tr class='total'><td colspan=2>Week average ($day_count days)</td></td><td>%d</td><td>%.2f</td><td>%.2f</td>", $total_customers/$day_count, $total_dpr/$day_count, $total_gross/$day_count;
foreach my $h ((6..23), 0, 1, 2) {
    my $t = 180; #threshold
my $f = 0.95; #factor

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
if ($weekday_days_count != 0) {
    printf "<tr class='total'><td colspan=2>Weekday average ($weekday_days_count days)</td></td><td>%d</td><td>%.2f</td><td>%.2f</td>", $weekday_total_customers/$weekday_days_count, $weekday_total_dpr/$weekday_days_count, $weekday_total_gross/$weekday_days_count;
foreach my $h ((6..23), 0, 1, 2) {
    my $t = 180; #threshold
my $f = 0.95; #factor

my $hg = $weekday_total_hour_gross{$h}/$weekday_days_count * $f;
my $a = $hg;
$a = $t if $a > $t;
my $b = $hg - $t;
$b = 0 if $b < 0;
printf "<td class='tiny%s' style='background-color: rgb(%d,%d,%d);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
    $h % 2 ? ' gray' : '',
    143 + $b,
    239 - $a,
    143,
    $weekday_total_hour_customers{$h}/$weekday_days_count, $weekday_total_hour_dpr{$h}/$weekday_days_count, $weekday_total_hour_gross{$h}/$weekday_days_count;
#printf "<td class='tiny%s' style='background-color: rgb(200,%d,200);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
#			   $h % 2 ? ' gray' : '', 255 - $total_hour_gross{$h}/7*1.3, $total_hour_customers{$h}/7, $total_hour_dpr{$h}/7, $total_hour_gross{$h}/7;
}
}
if ($weekend_days_count != 0) {
    printf "<tr class='total'><td colspan=2>Weekend average ($weekend_days_count days)</td></td><td>%d</td><td>%.2f</td><td>%.2f</td>", $weekend_total_customers/$weekend_days_count, $weekend_total_dpr/$weekend_days_count, $weekend_total_gross/$weekend_days_count;
foreach my $h ((6..23), 0, 1, 2) {
    my $t = 180; #threshold
my $f = 0.95; #factor

my $hg = $weekend_total_hour_gross{$h}/$weekend_days_count * $f;
my $a = $hg;
$a = $t if $a > $t;
my $b = $hg - $t;
$b = 0 if $b < 0;
printf "<td class='tiny%s' style='background-color: rgb(%d,%d,%d);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
    $h % 2 ? ' gray' : '',
    143 + $b,
    239 - $a,
    143,
    $weekend_total_hour_customers{$h}/$weekend_days_count, $weekend_total_hour_dpr{$h}/$weekend_days_count, $weekend_total_hour_gross{$h}/$weekend_days_count;
#printf "<td class='tiny%s' style='background-color: rgb(200,%d,200);'>%d<br/>%.1f<br/><b>\$%d</b></td>\n",
#			   $h % 2 ? ' gray' : '', 255 - $total_hour_gross{$h}/7*1.3, $total_hour_customers{$h}/7, $total_hour_dpr{$h}/7, $total_hour_gross{$h}/7;
}
}
}
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




