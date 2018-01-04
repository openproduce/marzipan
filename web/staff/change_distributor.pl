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
if ($q{'new_distr'}) {
	my $sth = $dbh->prepare("update items set distributor_id = $q{'new_distr'} where id = $q{'id'}");
	$sth->execute();
} elsif ($q{'itemnum'}) {
	my $sth = $dbh->prepare("update items set item_number = $q{'itemnum'} where id = $q{'id'}");
	$sth->execute();
}
print "Content-type: text/plain\n\n";
print "1";
