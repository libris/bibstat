define(['jquery', 'cell.sum', 'cell', 'bootstrap.validator.sv'], function($, sum, cell) {
    var survey = {
        form: function(selector) {
            if(selector) return $('#survey-form ' + selector);
            else return $('#survey-form');
        },
        validator: function() { return survey.form().data('bootstrapValidator'); },
        inputs: function() { return survey.form('input').not('[type="hidden"]'); },
        disabledInputs: function() { return survey.inputs().filter("[disabled]"); },
        enabledInputs: function() { return survey.inputs().not('[disabled]'); },
        filledInputs: function() { return survey.enabledInputs().filter(function() { return $(this).val(); }); },
        emptyInputs: function() { return survey.enabledInputs().filter(function() { return !$(this).val(); }); },
        correctInputs: function() {
            return survey.enabledInputs().filter(function() {
                return this.value && $(this).closest('.form-group').hasClass('has-success');
            });
        }
    };
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
            input.css("padding-right", "0px");
            input.val(element.text());
            input.prop('disabled', true);
        };
        var enableInput = function(input) {
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

        survey.form(".cell .input-group-btn .dropdown-menu .menu-disable").click(function(e) {
            e.preventDefault();

            var element = $(this);
            setActive(element);

            var input = getInput(element);
            var inputs = getInputs(input);

            for(var index in inputs) {
                disableInput(inputs[index], element);
                disableDropdown(inputs[index]);
            }

            updateProgress();
        });
        survey.form(".cell .input-group-btn .dropdown-menu .menu-enable").click(function(e) {
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

            updateProgress();
        });
        survey.form(".cell .input-group-btn .dropdown-menu li.active a").click();
    };
    var updateProgress = function() {
        var total = survey.enabledInputs().length;
        var correct = survey.correctInputs().length;
        var percent = (correct / total) * 100;

        survey.form('.answers-text').text('Du har svarat på ' + correct + ' av ' + total + ' frågor totalt.');
        survey.form('.answers-progress .progress-bar-success').css('width', percent + '%');
    };
    var initProgress = function() {
        $.each(survey.inputs(), function() {
            cell.onChange($(this), function() {
                updateProgress();
            });
        });

        var validator = survey.validator();
        $.each(survey.filledInputs(), function() {
            validator.validateField($(this));
        });

        updateProgress();
    };

    return {
        init: function() {
            survey.form().bootstrapValidator({
                excluded: ['.disable-validation', ':disabled', ':hidden', ':not(:visible)'],
                feedbackIcons: {
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh'
                }
            }).on('error.validator.bv', function(e, data) { // http://bootstrapvalidator.com/examples/changing-default-behaviour/#showing-one-message-each-time
                data.element
                    .data('bv.messages')
                    .find('.help-block[data-bv-for="' + data.field + '"]').hide()
                    .filter('[data-bv-validator="' + data.validator + '"]').show();
            }).on('success.form.bv', function() {
                var disabledInputIds = survey.disabledInputs().map(function() { return $(this).attr("id"); }).get().join(" ");
                survey.disabledInputs().prop("disabled", false);
                $("#disabled_inputs").val(disabledInputIds);

                survey.form().attr("action", Urls.edit_survey(survey.form("#id_key").val()));
                survey.validator().defaultSubmit();
            });

            /* Move feedback icons to the right side of the input field. */
            $.each(survey.form(".cell .form-control-feedback"), function() {
                var element = $(this), input = element.prev(".input-group").children("input");
                var left = input.outerWidth() - element.width();

                element.css("right", "inherit");
                element.css("left", left + "px");
                element.css("top", "10px");
            });

            /* Enable help button popover. */
            survey.form(".btn-help").popover({
                container: 'body'
            }).click(function(e) {
                e.preventDefault();
            });

            survey.form("#save-survey-btn").click(function(e) {
                e.preventDefault();
                $("#submit_action").val("save");
                var empty = survey.emptyInputs();
                empty.addClass("disable-validation");
                survey.validator().validate();
                empty.removeClass("disable-validation");
            });

            $("#submit-survey-btn").click(function(e) {
                e.preventDefault();
                $("#submit_action").val("submit");
                $("#survey-form").data('bootstrapValidator').validate();
            });

            sum.init();
            initDropdown();
            initProgress();
        }
    };
});