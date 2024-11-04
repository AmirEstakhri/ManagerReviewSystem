(function ($) {
    "use strict";
    
    portfolioItemContentLoadOnClick();
    setPrettyPhoto();
    sendMail();
    inputFieldsTextAnimation();
    counterCocoBasic();
    accordionCocoBasic();

    //Header
    $("header .menu-toggler").click(function () {
        $(this).toggleClass("toggler-activate");
        $("header nav").toggleClass("nav-activate");
    });
    $("header nav ul li a:not('.new-page-link')").click(function (e) {
        e.preventDefault();
        if ($(window).width() < 1300) {
            $("header nav").removeClass("nav-activate");
            $("header .menu-toggler").removeClass("toggler-activate");
        }
        $("html,body").animate({
            scrollTop: $('#' + $(this).data('scroll')).offset().top - 76
        }, 500, 0);
    });

    $(window).on('load', function () {
        isotopeSetUp();
        imageSliderSettings();
        $('.preloader').fadeOut(600);
    });

    // Function on scrolling
    $(window).scroll(function () {
        // Activating header links on reaching the section
        $("section").each(function () {
            if ($(window).scrollTop() > $(this).offset().top - 77) {
                var sectionID = $(this).attr('id');
                $("nav ul li a[data-scroll='" + sectionID + "']")
                        .addClass('active').parent()
                        .siblings().find('a').removeClass('active');
            }
        });

        progressBar();
    });


//------------------------------------------------------------------------
//Helper Methods -->
//------------------------------------------------------------------------

    function progressBar() {
        // Progress bars 
        $(".skills .skills-content .progress-box .prog-bar").each(function () {
            $(this).appear(function () {
                var loader = $(this).children(".bar").find("span.bar-percent");
                loader.css({
                    width: loader.attr("data-progress")
                });
            });
        });
    }

    function counterCocoBasic() {
        // Counter
        $(".counter-area").appear(function () {
            var countdown1 = setInterval(function () {
                var counter1 = parseInt($(".counter-number-1").html());
                if (counter1 < $(".counter-number-1").attr("data-count")) {
                    $(".counter-number-1").html(counter1 + 1);
                } else {
                    clearInterval(countdown1);
                }
            }, 100);
            var countdown2 = setInterval(function () {
                var counter2 = parseInt($(".counter-number-2").html());
                if (counter2 < $(".counter-number-2").attr("data-count")) {
                    $(".counter-number-2").html(counter2 + 1);
                } else {
                    clearInterval(countdown2);
                }
            }, 10);
            var countdown3 = setInterval(function () {
                var counter3 = parseFloat($(".counter-number-3").html());
                if (counter3 < $(".counter-number-3").attr("data-count")) {
                    $(".counter-number-3").html((counter3 + .1).toFixed(1));
                } else {
                    clearInterval(countdown3.toFixed(2));
                }
            }, 50);
            var countdown4 = setInterval(function () {
                var counter4 = parseInt($(".counter-number-4").html());
                if (counter4 < $(".counter-number-4").attr("data-count")) {
                    $(".counter-number-4").html(counter4 + 1);
                } else {
                    clearInterval(countdown4);
                }
            }, 5);
        });
    }

    function accordionCocoBasic() {
        // Expereince Accordion
        $(".experience-content .faq-accordion .exp-box .title").click(function () {
            $(this).find("i").toggleClass("rotating-icon");
            $(this).next(".slide-text").slideToggle();
        });
    }

    function portfolioItemContentLoadOnClick() {
        $('.ajax-portfolio').on('click', function (e) {
            e.preventDefault();
            var portfolioItemID = $(this).data('id');
            $(this).addClass('loading-portfolio-item-content');
            if ($("#pcw-" + portfolioItemID).length) //Check if is allready loaded
            {
                $('html, body').animate({scrollTop: $('#portfolio-wrapper').offset().top - 150}, 400);
                setTimeout(function () {
                    $('#portfolio-grid').addClass('hide');
                    setTimeout(function () {
                        $("#pcw-" + portfolioItemID).addClass('show');
                        $('.portfolio-load-content-holder').addClass('show');
                        $('.ajax-portfolio').removeClass('loading-portfolio-item-content');
                        $('#portfolio-grid').hide();
                    }, 300);
                }, 500);
            } else {
                loadPortfolioItemContent(portfolioItemID);
            }
        });
    }

    function loadPortfolioItemContent(portfolioItemID) {
        $.ajax({
            url: $('.ajax-portfolio[data-id="' + portfolioItemID + '"]').attr('href'),
            type: 'GET',
            success: function (html) {
                var getPortfolioItemHtml = $(html).find(".portfolio-item-wrapper").html();
                $('.portfolio-load-content-holder').append('<div id="pcw-' + portfolioItemID + '" class="portfolio-content-wrapper">' + getPortfolioItemHtml + '</div>');
                if (!$("#pcw-" + portfolioItemID + " .close-icon").length) {
                    $("#pcw-" + portfolioItemID).prepend('<div class="close-icon"></div>');
                }
                $('html, body').animate({scrollTop: $('#portfolio-wrapper').offset().top - 150}, 400);
                setTimeout(function () {
                    $("#pcw-" + portfolioItemID).imagesLoaded(function () {
                        imageSliderSettings();
                        $(".site-content").fitVids(); //Fit Video
                        $('#portfolio-grid').addClass('hide');
                        setTimeout(function () {
                            $("#pcw-" + portfolioItemID).addClass('show');
                            $('.portfolio-load-content-holder').addClass('show');
                            $('.ajax-portfolio').removeClass('loading-portfolio-item-content');
                            $('#portfolio-grid').hide();
                        }, 300);
                        $('.close-icon').on('click', function (e) {
                            var portfolioReturnItemID = $(this).closest('.portfolio-content-wrapper').attr("id").split("-")[1];
                            $('.portfolio-load-content-holder').addClass("viceversa");
                            $('#portfolio-grid').css('display', 'block');
                            setTimeout(function () {
                                $('#pcw-' + portfolioReturnItemID).removeClass('show');
                                $('.portfolio-load-content-holder').removeClass('viceversa show');
                                $('#portfolio-grid').removeClass('hide');
                            }, 300);
                            setTimeout(function () {
                                $('html, body').animate({scrollTop: $('#p-item-' + portfolioReturnItemID).offset().top - 150}, 400);
                            }, 500);
                        });
                    });
                }, 500);
            }
        });
        return false;
    }

    function imageSliderSettings() {
        $(".image-slider").each(function () {
            var speed_value = $(this).data('speed');
            var auto_value = $(this).data('auto');
            var hover_pause = $(this).data('hover');
            if (auto_value === true) {
                $(this).owlCarousel({
                    loop: true,
                    autoHeight: true,
                    smartSpeed: 1000,
                    autoplay: auto_value,
                    autoplayHoverPause: hover_pause,
                    autoplayTimeout: speed_value,
                    responsiveClass: true,
                    items: 1
                });
                $(this).on('mouseleave', function () {
                    $(this).trigger('stop.owl.autoplay');
                    $(this).trigger('play.owl.autoplay', [auto_value]);
                });
            } else {
                $(this).owlCarousel({
                    loop: true,
                    autoHeight: true,
                    smartSpeed: 1000,
                    autoplay: false,
                    responsiveClass: true,
                    items: 1
                });
            }
        });
    }

    function isotopeSetUp() {
        var grid = $('.grid').imagesLoaded(function () {
            grid.isotope({
                percentPosition: true,
                itemSelector: '.grid-item',
                masonry: {
                    columnWidth: '.grid-sizer'
                }
            });
        });
    }

    function setPrettyPhoto() {
        $('a[data-rel]').each(function () {
            $(this).attr('rel', $(this).data('rel'));
        });
        $(".grid-item:visible a[rel^='prettyPhoto'], a[rel='prettyPhoto[home]']").prettyPhoto({
            slideshow: false, /* false OR interval time in ms */
            overlay_gallery: false, /* If set to true, a gallery will overlay the fullscreen image on mouse over */
            default_width: 1280,
            default_height: 720,
            deeplinking: false,
            social_tools: false,
            iframe_markup: '<iframe src ="{path}" width="{width}" height="{height}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
        });
    }

    function inputFieldsTextAnimation() {
        $(".contact-form textarea, .contact-form input").on("focus", function () {
            $(this).next(".input-default-text").addClass('has-content');
        });

        $(".contact-form textarea, .contact-form input").on("focusout", function () {
            if (!$(this).val()) {
                $(this).next(".input-default-text").removeClass('has-content');
            }
        });
    }

    function isValidEmailAddress(emailAddress) {
        var pattern = /^([a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+(\.[a-z\d!#$%&'*+\-\/=?^_`{|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)*|"((([ \t]*\r\n)?[ \t]+)?([\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*(([ \t]*\r\n)?[ \t]+)?")@(([a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\d\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.)+([a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][a-z\d\-._~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]*[a-z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])\.?$/i;
        return pattern.test(emailAddress);
    }

    function sendMail() {
        $('.contact-form [type="submit"]').on('click', function () {
            var emailVal = $('#contact-email').val();
            if (isValidEmailAddress(emailVal)) {
                var params = {
                    'action': 'SendMessage',
                    'name': $('#name').val(),
                    'email': $('#contact-email').val(),
                    'subject': $('#subject').val(),
                    'message': $('#message').val()
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
                                $("#name").val("").siblings().first().removeClass("has-content");
                                $("#contact-email").val("").siblings().first().removeClass("has-content");
                                $("#subject").val("").siblings().first().removeClass("has-content");
                                $("#message").val("").siblings().first().removeClass("has-content");
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