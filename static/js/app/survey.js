define(['jquery', 'cell.sum', 'bootstrap.validator.sv'], function($, sum) {


    var initDropdown = function() {
        var isActive = function(element) {
            var parent = element.parent('li');
            return parent.hasClass("active");
        };

        var setActive = function(element) {
            var parent = element.parent('li');
            parent.siblings("li").removeClass("active");
            parent.addClass("active");
        };

        var getInput = function(element) {
            return element.closest(".input-group-btn").prev("input");
        };

        var getInputs = function(input) {
            var getAttributeInputs = function(input, attribute) {
                var inputs = [];

                if(input.attr(attribute)) {
                    var elements = input.attr(attribute).split(' ');
                    for(var index in elements)
                        inputs.push($('#' + elements[index]));
                }

                return inputs;
            };

            var getSiblings = function(input) {
                return getAttributeInputs(input, 'data-sum-siblings');
            };

            var getChildren = function(input) {
                return getAttributeInputs(input, 'data-sum-of');
            };

            return [input].concat(getSiblings(input)).concat(getChildren(input));
        };

        var disableInput = function(input, element) {
            $('#survey-form').bootstrapValidator('enableFieldValidators', input.attr('name'), false);
            input.css("padding-right", "0px");
            input.val(element.text());
            input.prop('disabled', true);
        };

        var enableInput = function(input) {
            $('#survey-form').bootstrapValidator('enableFieldValidators', input.attr('name'), true);
            input.css("padding-right", "");
            input.val("");
            input.prop('disabled', false);
        };

        var disableDropdown = function(input) {
            if(input.attr('data-sum-siblings')) {
                var dropdown = input.next(".input-group-btn").children(".btn-dropdown");
                dropdown.prop('disabled', true);
            }
        };

        var enableDropdown = function(input) {
            if(!input.attr('data-sum-of')) {
                var dropdown = input.next(".input-group-btn").children(".btn-dropdown");
                dropdown.prop('disabled', false);

                var enable = dropdown.siblings('.dropdown-menu').find(".menu-enable");
                setActive(enable);
            }
        };

        /* Handle the dropdown menu for cells. */
        $(".cell .input-group-btn .dropdown-menu .menu-disable").click(function(e) {
            e.preventDefault();

            var element = $(this);
            if(isActive(element))
                return;

            setActive(element);

            var input = getInput(element);
            var inputs = getInputs(input);

            for(var index in inputs) {
                disableInput(inputs[index], element);
                disableDropdown(inputs[index]);
            }
        });

        $(".cell .input-group-btn .dropdown-menu .menu-enable").click(function(e) {
            e.preventDefault();

            var element = $(this);
            if(isActive(element))
                return;

            setActive(element);

            var input = getInput(element);
            var inputs = getInputs(input);

            for(var index in inputs) {
                enableInput(inputs[index]);
                enableDropdown(inputs[index]);
            }

            input.focus();
        });
    };

    return {
        init: function() {
            /* Enable bootstrap validator on survey form. */
            $('#survey-form').on('init.field.bv', function(e, data) { // http://bootstrapvalidator.com/examples/showing-required-icon/
                var $parent = data.element.parents('.form-group'),
                    $icon = $parent.find('.form-control-feedback[data-bv-icon-for="' + data.field + '"]'),
                    options = data.bv.getOptions(),
                    validators = data.bv.getOptions(data.field).validators;

                if(validators.notEmpty && options.feedbackIcons && options.feedbackIcons.required)
                    $icon.addClass(options.feedbackIcons.required).show();
            }).bootstrapValidator({
                feedbackIcons: {
                    required: 'fa fa-asterisk',
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh'
                }
            }).on('error.validator.bv', function(e, data) { // http://bootstrapvalidator.com/examples/changing-default-behaviour/#showing-one-message-each-time
                data.element
                    .data('bv.messages')
                    .find('.help-block[data-bv-for="' + data.field + '"]').hide()
                    .filter('[data-bv-validator="' + data.validator + '"]').show();
            }).on('success.form.bv', function(e) {
                var disabled_input_ids = $("input[disabled]").map(function() {
                    return $(this).attr("id");
                }).get().join(" ");

                if(disabled_input_ids) {
                    $("#disabled_inputs").val(disabled_input_ids);
                }

                $("input[disabled]").prop("disabled", false);

                var survey_id = $("#id_key").val();
                var action = Urls.edit_survey(survey_id);
                $("#survey-form").attr("action", action)
            }).on('status.field.bv', function(e, data) { // http://bootstrapvalidator.com/examples/showing-required-icon/
                var $parent = data.element.parents('.form-group'),
                    $icon = $parent.find('.form-control-feedback[data-bv-icon-for="' + data.field + '"]'),
                    options = data.bv.getOptions(),
                    validators = data.bv.getOptions(data.field).validators;

                if(validators.notEmpty && options.feedbackIcons && options.feedbackIcons.required)
                    $icon.removeClass(options.feedbackIcons.required).addClass('fa');
            });

            /* Move feedback icons to the right of the input field. */
            $.each($(".cell .form-control-feedback"), function() {
                var element = $(this), input = element.prev(".input-group").children("input");
                var left = input.outerWidth() - element.width();

                element.css("right", "inherit");
                element.css("left", left + "px");
            });

            initDropdown();

            /* Enable help button popover. */
            $(".btn-help").popover();

            sum.init();
        }
    };
});