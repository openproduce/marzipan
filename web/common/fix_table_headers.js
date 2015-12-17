/**
 * This file is part of Marzipan, an open source point-of-sale system.
 * Copyright (C) 2015 Open Produce LLC
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

var init_pos;
function fixCH() {
    if ($('.col-header').css('position') != 'fixed') {
        var o = $('.col-header').offset();
        $('.col-header').css('left', o.left+'px');
        $('.col-header').css('top', o.top+'px');
        $('.col-header').css('position', 'fixed');
    }
}

function followCH() {
    if (isOldMSIE()) { return; }

    if ($('.col-header').css('position') == 'fixed') {
        if ($(document).scrollTop() >= init_pos) {
            $('.col-header').css('top', '3px');
        } else {
            $('.col-header').css('top', (init_pos-$(document).scrollTop() - 30)+'px');
        }
    }
}
function isOldMSIE() {
    return ($.browser.msie && $.browser.version < 7);
}

$(document).ready(function() 
{
  if (!isOldMSIE() && $(window).width() >= 1000) {
      init_pos = $('.col-header').offset().top;
      fixCH();
      followCH();
  }

});

$(window).scroll(followCH);
