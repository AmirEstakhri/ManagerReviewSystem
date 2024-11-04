(function ($) {
    "use strict";

    subscribe();

    $(window).on('load', function () {
        $('.doc-loader').fadeOut();
    });

    function isValidEmailAddress(emailAddress) {
        var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i;
        return pattern.test(emailAddress);
    }

    function subscribe() {
        $('.coming-form button').on('click', function (e) {
            e.preventDefault();
            var emailVal = $('#email').val();
            if (isValidEmailAddress(emailVal)) {
                var params = {
                    'action': 'SendMessage',
                    'email': $('#email').val(),
                };
                $.ajax({
                    type: "POST",
                    url: "php/sendMail.php",
                    data: params,
                    success: function (response) {
                        if (response) {
                            var responseObj = $.parseJSON(response);
                            if (responseObj.ResponseData)
                            {
                                alert(responseObj.ResponseData);
                                $("#email").val('');
                            }
                        }
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        //xhr.status : 404, 303, 501...
                        var error = null;
                        switch (xhr.status)
                        {
                            case "301":
                                error = "Redirection Error!";
                                break;
                            case "307":
                                error = "Error, temporary server redirection!";
                                break;
                            case "400":
                                error = "Bad request!";
                                break;
                            case "404":
                                error = "Page not found!";
                                break;
                            case "500":
                                error = "Server is currently unavailable!";
                                break;
                            default:
                                error = "Unespected error, please try again later.";
                        }
                        if (error) {
                            alert(error);
                        }
                    }
                });
            } else
            {
                alert('Your email is not in valid format');
            }
        });
    }

})(jQuery);