define(['jquery', 'bootstrap.validator.sv'], function($) {
    return {
        init: function() {

            /* Enable bootstrap validator on survey form. */
            $('#survey-form').bootstrapValidator({
                feedbackIcons: {
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh'
                }
            });

            /* Move feedback icons to the right of the input field. */
            $.each($(".cell .form-control-feedback"), function() {
                var element = $(this), input = element.prev(".input-group").children("input");
                var left = input.outerWidth() - element.width();

                element.css("right", "inherit");
                element.css("left", left + "px");
            });

            /* Handle the dropdown menu for cells. */
            $(".cell .input-group-btn .dropdown-menu a").click(function(e) {
                e.preventDefault();

                var element = $(this), parent = element.parent('li');
                if(parent.hasClass("active"))
                    return;

                parent.siblings("li").removeClass("active");
                parent.addClass("active");

                var input = element.closest(".input-group-btn").prev("input");
                if(element.hasClass("menu-enable")) {
                    $('#survey-form').bootstrapValidator('enableFieldValidators', input.attr('name'), true);
                    input.css("padding-right", "");
                    input.prop('disabled', false);
                    input.val("");
                    input.focus();
                } else {
                    $('#survey-form').bootstrapValidator('enableFieldValidators', input.attr('name'), false);
                    input.css("padding-right", "0px");
                    input.prop('disabled', true);
                    input.val(element.text());
                }
            });

            /* Enable help button popover. */
            $(".btn-help").popover();
        }
    };
});