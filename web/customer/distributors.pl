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

