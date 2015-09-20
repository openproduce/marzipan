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
if ($q{'new_distr'}) {
	my $sth = $dbh->prepare("update items set distributor_id = $q{'new_distr'} where id = $q{'id'}");
	$sth->execute();
} elsif ($q{'itemnum'}) {
	my $sth = $dbh->prepare("update items set item_number = $q{'itemnum'} where id = $q{'id'}");
	$sth->execute();
}
print "Content-type: text/plain\n\n";
print "1";
