define(['jquery', 'survey.sum', 'survey.cell', 'surveys.dispatch', 'bootstrap.validator.sv'], function ($, sum, cell, dispatch) {
    var survey = {
        form: function (selector) {
            if (selector) return $('#survey-form ' + selector);
            else return $('#survey-form');
        },
        validator: function () {
            return survey.form().data('bootstrapValidator');
        },
        inputs: function () {
            return survey.form("input:not([type='checkbox'])").not("[type='hidden']");
        },
        changeableInputs: function() {
            return survey.form("input:not([type='checkbox']),textarea").not("[type='hidden']").not('.form-excluded')
        },
        disabledInputs: function () {
            return survey.inputs().filter("[disabled]");
        },
        enabledInputs: function () {
            return survey.inputs().not('[disabled]');
        },
        selectedLibraries: function() {
            return survey.form(".select-library:checked").map(function() {
                return $(this).attr("name");
            }).get().join(" ");
        },
        filledInputs: function () {
            return survey.enabledInputs().filter(function () {
                return $(this).val();
            });
        },
        emptyInputs: function () {
            return survey.enabledInputs().filter(function () {
                return !$(this).val();
            });
        },
        correctInputs: function () {
            return survey.enabledInputs().filter(function () {
                return this.value && $(this).closest('.form-group').hasClass('has-success');
            });
        },
        requiredInputs: function () {
            return survey.enabledInputs().filter("[data-bv-notempty]");
        }
    };

    var initDropdown = function () {
        var isActive = function (element) {
            var parent = element.parent('li');
            return parent.hasClass("active");
        };
        var setActive = function (element) {
            var parent = element.parent('li');
            parent.siblings("li").removeClass("active");
            parent.addClass("active");
        };
        var getInput = function (element) {
            return element.closest(".input-group-btn").prev("input");
        };
        var getInputs = function (input) {
            var getAttributeInputs = function (input, attribute) {
                var inputs = [];

                if (input.attr(attribute)) {
                    var elements = input.attr(attribute).split(' ');
                    for (var index in elements)
                        inputs.push($('#' + elements[index]));
                }

                return inputs;
            };
            var getSiblings = function (input) {
                var inputs = [];
                $.each($("input[data-sum-of]"), function() {
                   var children = $(this).attr('data-sum-of').split(' ');
                   var inputIndex = children.indexOf(input.attr("name"));
                   if(inputIndex != -1) {
                       for(var i = 0; i < children.length; i++) {
                           if(i == inputIndex) continue;
                           inputs.push($("#" + children[i]));
                       }
                   }
                });

                return inputs;
            };
            var getChildren = function (input) {
                return getAttributeInputs(input, 'data-sum-of');
            };

            return [input].concat(getSiblings(input)).concat(getChildren(input));
        };
        var disableInput = function (input, element) {
            survey.validator().updateStatus(input.attr("name"), "NOT_VALIDATED");
            input.css("padding-right", "0px");
            input.val(element.text());
            input.prop('disabled', true);
            input.addClass('value-unknown');
        };
        var enableInput = function (input) {
            input.css("padding-right", "");
            input.val("");
            input.prop('disabled', false);
            input.removeClass('value-unknown');
        };
        var disableDropdown = function (input) {
            if (input.attr('data-is-child')) {
                var dropdown = input.next(".input-group-btn").children(".btn-dropdown");
                dropdown.prop('disabled', true);
            }
        };
        var enableDropdown = function (input) {
            if (!input.attr('data-sum-of')) {
                var dropdown = input.next(".input-group-btn").children(".btn-dropdown");
                dropdown.prop('disabled', false);

                var enable = dropdown.siblings('.dropdown-menu').find(".menu-enable");
                setActive(enable);
            }
        };

        survey.form(".cell .input-group-btn .dropdown-menu .menu-disable").click(function (e) {
            e.preventDefault();

            var element = $(this);
            if (!isActive(element))
                showChangesNotSaved();

            setActive(element);

            var input = getInput(element);
            var inputs = getInputs(input);

            for (var index in inputs) {
                disableInput(inputs[index], element);
                disableDropdown(inputs[index]);
            }

            updateProgress();
        });
        survey.form(".cell .input-group-btn .dropdown-menu .menu-enable").click(function (e) {
            e.preventDefault();

            var element = $(this);
            if (isActive(element))
                return;

            setActive(element);

            var input = getInput(element);
            var inputs = getInputs(input);

            for (var index in inputs) {
                enableInput(inputs[index]);
                enableDropdown(inputs[index]);
            }

            updateProgress();
            showChangesNotSaved();
        });
        survey.form(".cell .input-group-btn .dropdown-menu.value-unknown li.active a").click();
    };
    var updateProgress = function () {
        var total = survey.enabledInputs().length;
        var correct = survey.correctInputs().length;
        var percent = (correct / total) * 100;

        var requiredPercent = Math.ceil((survey.requiredInputs().length / total) * 100);
        var boostedPercent = Math.ceil(1.15 * percent);

        var setText = function(text) { survey.form('.answers-text').text(text); };
        var setPercent = function(percent) {survey.form('.answers-progress .progress-bar-success').css('width', percent + "%"); };
        var setPercentAndText = function(percent) {
            setText("Du har hittills fyllt i " + percent + "% av hela enkäten");
            setPercent(percent);
        };

        if(correct == 0) {
            setText("Du har inte börjat fylla i enkäten än...");
            setPercent(0);
        } else if(boostedPercent <= requiredPercent) {
            setPercentAndText(Math.min(boostedPercent, requiredPercent));
        } else {
            setPercentAndText(Math.max(Math.ceil(percent), requiredPercent));
        }
    };
    var initProgress = function () {
        $.each(survey.inputs(), function () {
            cell.onChange($(this), function () {
                updateProgress();
            });
        });

        var validator = survey.validator();
        $.each(survey.filledInputs(), function () {
            validator.validateField($(this));
        });

        updateProgress();
    };
    var readOnlyInit = function () {

        /* Enable help button popover. */
        $(".btn-help").popover({
            container: 'body'
        }).click(function (e) {
            e.preventDefault();
        });

        var initAdmin = function () {
            $("#form-admin .dropdown-menu > li > a").click(function (e) {
                e.preventDefault();
                var element = $(this);

                $("#id_selected_status").val(element.data('key'));
                element.closest(".dropdown").children(".dropdown-toggle").html(element.text() + ' <span class="caret"></span>');

                var item = element.closest("li");
                item.siblings("li").removeClass("active");
                item.addClass("active");
            });
        };

        var initPassword = function () {
            $("#form-password").bootstrapValidator();
        };

        initAdmin();
        initPassword();
    };
    var showChangesNotSaved = function () {
        $("#unsaved-changes-label").text("Det finns ifyllda svar som inte sparats");
    };
    return {
        init: function () {
            readOnlyInit();
            if ($("#read_only").val()) {
                return;
            }

            survey.form().bootstrapValidator({
                excluded: ['.disable-validation', ':disabled', ':hidden', ':not(:visible)'],
                trigger: 'keyup change paste',
                feedbackIcons: {
                    valid: 'fa fa-check',
                    invalid: 'fa fa-ban',
                    validating: 'fa fa-refresh'
                }
            }).on('error.validator.bv', function (e, data) { // http://bootstrapvalidator.com/examples/changing-default-behaviour/#showing-one-message-each-time
                data.element
                    .data('bv.messages')
                    .find('.help-block[data-bv-for="' + data.field + '"]').hide()
                    .filter('[data-bv-validator="' + data.validator + '"]').show();
            }).on('success.form.bv', function () {
                if (!$("#submit_action").val())
                    return;

                var unknownInputs = $(".value-unknown");

                var unknownInputIds = unknownInputs.map(function () {
                    return $(this).attr("id");
                }).get().join(" ");
                $("#unknown_inputs").val(unknownInputIds);
                unknownInputs.val("");

                var disabledInputIds = survey.disabledInputs().map(function () {
                    return $(this).attr("id");
                }).get().join(" ");
                $("#disabled_inputs").val(disabledInputIds);

                survey.disabledInputs().prop("disabled", false);


                $("#selected_libraries").val(survey.selectedLibraries());
                console.log($("#selected_libraries").val());
                
                survey.form().attr("action", Urls.survey(survey.form("#id_key").val()));
                survey.validator().defaultSubmit();
            }).on('error.form.bv', function () {
                $('html, body').animate({
                    scrollTop: survey.validator().getInvalidFields().first().offset().top - 100
                }, 300);
            });

            var submitTo = function (action, submit) {
                submit = submit || false
                var element = $(".publish-survey-responses-form").get(0);
                element.setAttribute('action', Urls[action]());
                if(submit) {
                    element.submit();
                }
                return element;
            };

            $("#surveys_active").click(function (e) {
                e.preventDefault();
                if($("#surveys_state").val() != "active") {
                    $("#surveys_state").val("active");
                    $("#surveys_filter_form").submit();
                }
            });
            $("#surveys_inactive").click(function (e) {
                e.preventDefault();
                if($("#surveys_state").val() != "inactive") {
                    $("#surveys_state").val("inactive");
                    $("#surveys_filter_form").submit();
                }
            });
            $("#export-surveys-modal .btn-confirm").click(function (e) {
                e.preventDefault();
                $("#export-surveys-modal").modal('hide');
                submitTo('surveys_export', true);
            });
            $(".btn-change-status").click(function (e) { e.preventDefault(); submitTo('surveys_statuses', true); });
            $(".btn-activate-surveys").click(function (e) { e.preventDefault(); submitTo('surveys_activate', true); });
            $(".btn-inactivate-surveys").click(function (e) { e.preventDefault(); submitTo('surveys_inactivate', true); });
            $(".btn-dispatch").click(function (e) {
                e.preventDefault();

                var checked = $(".select-one:checked").first();
                var library = checked.data('library');
                var address = checked.data('url-base') + checked.data('address');
                var city = checked.data('city');

                submitTo('dispatches');
                dispatch.init(library, address, city, function(unsavedChanges) {
                    var button = $('.btn-dispatch');

                    if(unsavedChanges) {
                        button.text("Skapa utskick*");
                        button.attr("data-original-title", "Det finns ett påbörjat utskick.");
                    } else {
                        button.text("Skapa utskick");
                        button.attr("data-original-title", "");
                    }
                });
            });

            /* Move feedback icons to the right side of the input field. */
            $.each(survey.form(".cell .form-control-feedback"), function () {
                var element = $(this), input = element.prev(".input-group").children("input");
                var left = input.outerWidth() - element.width();

                element.css("right", "inherit");
                element.css("left", left + "px");
                element.css("top", "10px");
            });

            survey.form("#save-survey-btn").click(function (e) {
                e.preventDefault();

                $("#submit_action").val("save");
                var empty = survey.emptyInputs();
                empty.addClass("disable-validation");
                survey.validator().validate();
                empty.removeClass("disable-validation");
            });

            survey.form("#submit-survey-btn").click(function (e) {
                e.preventDefault();

                var validator = survey.validator();
                validator.validate();
                if (validator.isValid()) {
                    $("#submit-confirm-modal").modal("show");
                }
            });

            $("#confirm-submit-survey-btn").click(function (e) {
                e.preventDefault();
                $("#submit_action").val("submit");
                survey.validator().validate();
            });

            cell.onChange(survey.changeableInputs(), function () {
                showChangesNotSaved();
            });

            /* FAQ Panel */
            var setIcon = function(id, state) {
                var icon = $("a[href='#" + id +"']").siblings('.fa');

                if(state == 'collapse') {
                    icon.removeClass("fa-angle-down");
                    icon.addClass("fa-angle-right");
                } else if(state == 'show') {
                    icon.removeClass("fa-angle-right");
                    icon.addClass("fa-angle-down");
                }
            };

            $('#panel-help .collapse').on('show.bs.collapse', function() {
                setIcon($(this).attr('id'), 'show');
            }).on('hide.bs.collapse', function() {
                setIcon($(this).attr('id'), 'collapse');
            });
            
            $('.survey-popover').tooltip();

            $('.modified-after-publish').on("click", function(e) {
                e.preventDefault();
            });

            sum.init();
            initDropdown();
            initProgress();
        }
    };
});