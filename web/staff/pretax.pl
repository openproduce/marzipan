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

use CGI qw(:standard);

print "Content-type: text/html\n\n";

print<<EOF;
<html>
<FORM action="pretax.pl" method="GET">
Price: <input type="text" name="amt">
<input type="submit" value="Submit">
</FORM>
EOF

$amt = param('amt');

print "Pre-tax prices for retail price <b>\$$amt</b>:<br/><br/>";

printf "Food / medicine: \$%.2f<br/>" , ($amt / 1.0225);
printf "Non-food: \$%.2f<br/>" , ($amt / 1.0925);
printf "Soda: \$%.2f<br/>" , ($amt / 1.1325);
printf "Beer 6-pack: \$%.2f<br/>" , (($amt - .23)/ 1.0925);
printf "Beer 4-pack tallboy cans: \$%.2f<br/>" , (($amt - .19)/ 1.0925);
printf "Beer 4-pack 12oz bottles: \$%.2f<br/>" , (($amt - .12)/ 1.0925);
printf "Beer 12-pack: \$%.2f<br/>" , (($amt - .46)/ 1.0925);
printf "Beer 750ml: \$%.2f<br/>" , (($amt - .07)/ 1.0925);
printf "Wine 750ml less than 14% abv: \$%.2f<br/>" , (($amt - .12)/ 1.0925);
printf "Wine 750ml more than 14% abv: \$%.2f<br/>" , (($amt - .27)/ 1.0925);
printf "Wine 1L less than 14% abv: \$%.2f<br/>" , (($amt - .16)/ 1.0925);

print "<br/>Retail prices for pre-tax price <b>\$$amt</b>:<br/><br/>";

printf "Food / medicine: \$%.2f<br/>" , ($amt * 1.0225);
printf "Non-food: \$%.2f<br/>" , ($amt * 1.0925);
printf "Soda: \$%.2f<br/>" , ($amt * 1.1325);
printf "Beer 6-pack: \$%.2f<br/>" , (($amt)* 1.0925 + .23);
printf "Beer 4-pack tallboy cans: \$%.2f<br/>" , (($amt)* 1.0925 + .19);
printf "Beer 4-pack 12oz bottles: \$%.2f<br/>" , (($amt)* 1.0925 + .12);
printf "Beer 12-pack: \$%.2f<br/>" , (($amt)* 1.0925 + .46);
printf "Beer 750ml: \$%.2f<br/>" , (($amt)* 1.0925 + .07);
printf "Wine 750ml less than 14% abv: \$%.2f<br/>" , (($amt)* 1.0925 + .12);
printf "Wine 750ml more than 14% abv: \$%.2f<br/>" , (($amt)* 1.0925 + .27);
printf "Wine 1L less than 14% abv: \$%.2f<br/>" , (($amt)* 1.0925 + .16);

print "\n</html>";
