$(document).ready(function() {
    
    var input = $('input.search-rep');
    var button = $('button.search-rep');

    $(button).attr('disabled','disabled');

    $(input).bind('input propertychange', function() {
        if ($(input).val() != "") {
            $(button).removeAttr('disabled');
        }
    });
});
