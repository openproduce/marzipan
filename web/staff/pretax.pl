#!/usr/bin/env perl

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
printf "Non-food: \$%.2f<br/>" , ($amt / 1.1025);
printf "Soda: \$%.2f<br/>" , ($amt / 1.1325);
printf "Beer 6-pack 12oz: \$%.2f<br/>" , (($amt - .23)/ 1.1025);
printf "Beer 6-pack tallboy: \$%.2f<br/>" , (($amt - .31)/ 1.1025);
printf "Beer 4-pack 12oz bottles: \$%.2f<br/>" , (($amt - .12)/ 1.1025);
printf "Beer 4-pack tallboy cans: \$%.2f<br/>" , (($amt - .19)/ 1.1025);
printf "Beer 12-pack: \$%.2f<br/>" , (($amt - .46)/ 1.1025);
printf "Beer 750ml: \$%.2f<br/>" , (($amt - .07)/ 1.1025);
printf "Wine 375ml less than or equal to 14% abv: \$%.2f<br/>" , (($amt - .06)/ 1.1025);
printf "Wine 750ml less than or equal to 14% abv: \$%.2f<br/>" , (($amt - .12)/ 1.1025);
printf "Wine 750ml more than 14% abv: \$%.2f<br/>" , (($amt - .27)/ 1.1025);
printf "Wine 300ml more than 14% abv: \$%.2f<br/>" , (($amt - .11)/ 1.1025);
printf "Wine 1L less than 14% abv: \$%.2f<br/>" , (($amt - .16)/ 1.1025);
printf "Spirits 600ml: \$%.2f<br/>" , (($amt - .83)/ 1.1025);
printf "Spirits 750ml: \$%.2f<br/>" , (($amt - 1.04)/ 1.1025);

print "<br/>Retail prices for pre-tax price <b>\$$amt</b>:<br/><br/>";

printf "Food / medicine: \$%.2f<br/>" , ($amt * 1.0225);
printf "Non-food: \$%.2f<br/>" , ($amt * 1.1025);
printf "Soda: \$%.2f<br/>" , ($amt * 1.1325);
printf "Beer 6-pack 12oz: \$%.2f<br/>" , (($amt)* 1.1025 + .23);
printf "Beer 6-pack tallboy: \$%.2f<br/>" , (($amt)* 1.1025 + .31);
printf "Beer 4-pack 12oz bottles: \$%.2f<br/>" , (($amt)* 1.1025 + .12);
printf "Beer 4-pack tallboy cans: \$%.2f<br/>" , (($amt)* 1.1025 + .19);
printf "Beer 12-pack: \$%.2f<br/>" , (($amt)* 1.1025 + .46);
printf "Beer 750ml: \$%.2f<br/>" , (($amt)* 1.1025 + .07);
printf "Wine 375ml less than or equal to 14% abv: \$%.2f<br/>" , (($amt)* 1.1025 + .06);
printf "Wine 750ml less than or equal to 14% abv: \$%.2f<br/>" , (($amt)* 1.1025 + .12);
printf "Wine 750ml more than 14% abv: \$%.2f<br/>" , (($amt)* 1.1025 + .27);
printf "Wine 300ml more than 14% abv: \$%.2f<br/>" , (($amt)* 1.1025 + .11);
printf "Wine 1L less than 14% abv: \$%.2f<br/>" , (($amt)* 1.1025 + .16);
printf "Spirits 600ml: \$%.2f<br/>" , (($amt)* 1.1025 + .83);
printf "Spirits 750ml: \$%.2f<br/>" , (($amt)* 1.1025 + 1.04);

print "\n</html>";
