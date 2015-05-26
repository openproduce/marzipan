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
