define(['jquery', 'cell.sum', 'bootstrap.validator.sv'], function($, sum) {
    return {
        init: function() {

            /* Enable bootstrap validator on survey form. */
            $('#survey-form').bootstrapValidator({
                feedbackIcons: {
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh'
                }
            }).on('error.validator.bv', function (e, data) { // http://bootstrapvalidator.com/examples/changing-default-behaviour/#showing-one-message-each-time
                data.element
                    .data('bv.messages')
                    .find('.help-block[data-bv-for="' + data.field + '"]').hide()
                    .filter('[data-bv-validator="' + data.validator + '"]').show();
            }).on('success.form.bv', function (e) {
                var disabled_input_ids = $("input[disabled]").map(function () {
                    return $(this).attr("id");
                }).get().join(" ");
                if (disabled_input_ids) {
                    $("#disabled_inputs").val(disabled_input_ids);
                }
                $("input[disabled]").prop("disabled", false);
            });

            /* Move feedback icons to the right of the input field. */
            $.each($(".cell .form-control-feedback"), function () {
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
                    input.val(element.text());
                    input.prop('disabled', true);
                }
            });

            /* Enable help button popover. */
            $(".btn-help").popover();

            sum.init();
        }
    };
});