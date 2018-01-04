#!/usr/bin/perl

use CGI qw/:standard/;

%catalogs = ("Kehe" => '/home/openproduce/catalogs/kehe_catalog.txt',
             "Raja" => '/home/openproduce/catalogs/raja_catalog.txt',
             "European" => '/home/openproduce/catalogs/european_catalog.txt');
print header;
print start_html('OP Distributor Catalog Search');
print start_form('GET');
print textfield('keyword');
print submit;
print end_form;
print hr;

if (param()) {
	my $keyword      = param('keyword');
	foreach $k (keys(%catalogs)) {
		print h1($k), "<br/>\n";
		open(F, "<$catalogs{$k}");
		my $firstline = 0;
		print "<pre>";
		while (<F>) {
			chomp;
			if ($firstline == 1) {
				print $_;
				print "<br/>\n";
				$firstline = 0;
				next;
			}
			my @words = split(/ +/,$keyword);
			my $match = 0;
			my $numwords = 0;
			foreach my $w (@words) {
				$numwords++;
				if ($_ =~ /$w/i) { $match++; }
			}
			if ($match == $numwords) {
				print lc(escapeHTML($_));
				print "\n";
			}
		}
		print "</pre>";
	print hr;
	}
}
print end_html;

