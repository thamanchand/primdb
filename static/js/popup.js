function openOffersDialog() {
	$('#overlay').fadeIn('fast', function() {
		$('#boxpopup').css('display','block');
        $('#boxpopup').animate({'left':'30%'},500);
    });
}
function openOffersDialog1() {
	$('#overlay').fadeIn('fast', function() {
		$('#boxpopup1').css('display','block');
        $('#boxpopup1').animate({'left':'30%'},500);
    });
}

function openOffersDialog2() {
	$('#overlay').fadeIn('fast', function() {
		$('#boxpopup2').css('display','block');
        $('#boxpopup2').animate({'left':'30%'},500);
    });
}

function openOffersDialog3() {
	$('#overlay').fadeIn('fast', function() {
		$('#boxpopup3').css('display','block');
        $('#boxpopup3').animate({'left':'30%'},500);
    });
}
function openOffersDialog4() {
	$('#overlay').fadeIn('fast', function() {
		$('#boxpopup4').css('display','block');
        $('#boxpopup4').animate({'left':'30%'},500);
    });
}
function closeOffersDialog(prospectElementID) {
	$(function($) {
		$(document).ready(function() {
			$('#' + prospectElementID).css('position','absolute');
			$('#' + prospectElementID).animate({'left':'-100%'}, 500, function() {
				$('#' + prospectElementID).css('position','fixed');
				$('#' + prospectElementID).css('left','100%');
				$('#overlay').fadeOut('fast');
			});
		});
	});
}