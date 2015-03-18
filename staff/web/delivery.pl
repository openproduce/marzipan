#!/usr/bin/perl
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
