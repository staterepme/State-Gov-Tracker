$(document).keypress(function (event) {
    "use strict";
    if (event.which === 13) {
        $('input[type="submit"]').click();
    }
});