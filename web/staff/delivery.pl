#!/usr/bin/perl

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

use strict;
use DBI;
use DBD::mysql;
my $dsn = "dbi:mysql:marzipan:localhost:3306";
my $dbh = DBI->connect($dsn, 'marzipan', '');
my %q = ();
while (<>) {
	chomp;
	my @pairs = split /\&/; 
	foreach my $pair (@pairs) {
		my ($name, $value) = split /=/, $pair;
		$value =~ s/[^-\d\.]//g;
		$q{$name} = $value;
	}
}
my $sth = $dbh->prepare("insert into deliveries(time_delivered, item_id, amount) values (now(), $q{'id'}, $q{'amt'})");
$sth->execute();
my $sth2 = $dbh->prepare("select sum(quantity) from sale_items where item_id=$q{'id'}");
$sth2->execute();
my $num_out = ($sth2->fetchrow_array())[0];
my $sth2 = $dbh->prepare("select sum(amount) from deliveries where item_id=$q{'id'}");
$sth2->execute();
my $num_in = ($sth2->fetchrow_array())[0];
print "Content-type: text/plain\n\n";
print $num_in - $num_out;
