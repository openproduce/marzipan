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

use strict;
use DBI;
use DBD::mysql;

my $dbh = DBI->connect("dbi:mysql:op_bank:localhost:3306", 'op_bank', '')
    or die "couldn't connect to database";
my %q = map { split /=/, $_ } split /\&/, $ENV{'QUERY_STRING'};

if ($q{'p'} eq 'check') {
    &view_check($q{'no'}, $q{'f'});
} else {
    &browse_checks();
}

$dbh->disconnect();

sub browse_checks {
    print "Content-type: text/html\n\n";
    print <<EOF;
<!doctype html>
<html>
<head>
<title>Browse Checks</title>
<style type="text/css">
    .check { width: 400px; height: 200px; }
</style>
</head>
<body>
EOF
    my $sth = $dbh->prepare("select xact_date, check_number, amount from ledger where check_number is not null order by xact_date");
    $sth->execute();
    while (my @row = $sth->fetchrow_array()) {
        print qq|<img class="check" src="?p=check&no=$row[1]&f=front" alt="check $row[1]" />\n|;
    }
    print "</body></html>\n";
}

sub view_check {
    my ($check_number, $face) = @_;
    my $img = $face eq 'front' ? 'front_image' : 'back_image';
    my $sth = $dbh->prepare("select $img from checks where check_number=?");
    $sth->execute($check_number);

    my $data = ($sth->fetchrow_array())[0];
    print "Content-type: image/jpeg\n\n";
    print $data;
}
