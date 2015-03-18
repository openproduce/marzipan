#!/usr/bin/env perl
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
