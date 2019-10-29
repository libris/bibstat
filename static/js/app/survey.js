/*global define,Urls,alert*/
define(['jquery', 'bootbox', 'survey.sum', 'survey.cell', 'surveys.dispatch', 'bootstrap.validator.sv', 'jquery.placeholder'],
    function ($, bootbox, sum, cell, dispatch) {
        'use strict';
        var _form = $('#survey-form');
        var _inputs = null;

        var isDirty = false;

        var survey = {
            form: function (selector) {
                if (selector) {
                    return _form.find(selector);
                } else {
                    return _form;
                }
            },
            validator: function () {
                return survey.form().data('bootstrapValidator');
            },
            inputs: function () {
                if (!_inputs) _inputs = survey.form('input:not([type="checkbox"])').not('[type="hidden"]');
                return _inputs;
            },
            changeableInputs: function () {
                return survey.form('input:not([type="checkbox"]),textarea').not('[type="hidden"]').not('.form-excluded');
            },
            disabledInputs: function () {
                return survey.inputs().filter('[disabled]');
            },
            enabledInputs: function () {
                return survey.inputs().not('[disabled]');
            },
            sumFields: function () {
                return survey.enabledInputs().filter('[data-sum-of]');
            },
            selectedLibraries: function () {
                return survey.form('.select-library:checked').map(function () {
                    return $(this).attr('name');
                }).get().join(' ');
            },
            filledInputs: function () {
                return survey.enabledInputs().filter(function () {
                    return $(this).val();
                });
            },
            filledRequiredInputs: function () {
                return survey.requiredEnabledInputs().filter(function () {
                    return $(this).val();
                });
            },
            emptyInputs: function () {
                return survey.enabledInputs().filter(function () {
                    return !$(this).val();
                });
            },
            notEmptySumFields: function () {
                return survey.sumFields().filter(function () {
                    return $(this).val();
                });
            },
            requiredInputs: function () {
                return survey.enabledInputs().filter('[data-bv-notempty]');
            },
            requiredEnabledInputs: function() {
              return survey.enabledInputs().filter('[data-bv-notempty]').not('[disabled]');
            },
            sumOfInputs: function () {
                return survey.enabledInputs().filter('[data-sum-of]');
            }
        };

        var initDropdown = function () {
            var isActive = function (element) {
                var parent = element.parent('li');
                return parent.hasClass('active');
            };
            var setActive = function (element) {
                var parent = element.parent('li');
                parent.siblings('li').removeClass('active');
                parent.addClass('active');
            };
            var getInput = function (element) {
                return element.closest('.input-group-btn').prev('input');
            };
            var disableInput = function (input, element) {
                survey.validator().updateStatus(input.attr('name'), 'NOT_VALIDATED');
                input.css('padding-right', '0px');
                input.val(element.text());
                input.prop('disabled', true);
                input.addClass('value-unknown');
            };
            var enableInput = function (input) {
                input.css('padding-right', '');

                // Empty input if text and NOT A NUMBER
                if (!((input.val() - 0) == input.val() && ('' + input.val()).trim().length > 0)) {
                    input.val('0');
                }

                input.prop('disabled', false);
                input.removeClass('value-unknown');
            };
            var setActiveSiblings = function (input) {

                var dropdown = input.next('.input-group-btn').children('.btn-dropdown');

                var disableInput = dropdown.siblings('.dropdown-menu').find('.menu-disable-input');
                setActive(disableInput);

            };
            var enableDropdown = function (input) {
                var dropdown = input.next('.input-group-btn').children('.btn-dropdown');
                dropdown.prop('disabled', false);

                var enable = dropdown.siblings('.dropdown-menu').find('.menu-enable');
                setActive(enable);
            };
            var disable = function (inputs, element) {
                for (var index in inputs) {
                    disableInput(inputs[index], element);
                    setActiveSiblings(inputs[index]);
                }

                if (!isActive(element))
                    showChangesNotSaved();

                setActive(element);

                updateProgress();
            };

            var resetFields = function (elements) {
                for (var i = 0; i < elements.length; i++) {
                    if (!elements[i].prop('disabled')) {
                        elements[i].val('');
                        survey.validator().updateStatus(elements[i].attr('name'), 'NOT_VALIDATED');
                    }
                }
            };

            survey.form('.input-group-btn .dropdown-menu .menu-disable-input').click(function (e) {
                e.preventDefault();

                var element = $(this);
                var input = getInput(element);
                var children = [];
                var resets = [];

                var hasParent = (input.attr('parent')) ? input.attr('parent').slice(0, -1) : null;

                if (hasParent !== null) {
                    if (hasParent.split(',').length == 2) {
                        // MATRIX
                        if (input.attr('data-sum-of') === undefined) {
                            // Loop all inputs in a div.panel-body!
                            $(this).closest('.panel-body').find('input').each(function () {
                                var el = $(this);
                                if (el.attr('data-sum-of') === undefined && el.attr('data-is-child') !== undefined) {
                                    children.push(el);
                                } else {
                                    // Reset parent input (right and in the bottom)
                                    resets.push(el);
                                }
                            });
                        }
                    } else {
                        // Disable entire column
                        // Except sum/parent input
                        var parent = $(input.attr('parent').slice(0, -1));
                        var c = parent.attr('data-sum-of').split(' ');

                        for (var i = 0; i < c.length; i++) {
                            children.push($('#' + c[i]));
                        }
                    }
                } else {
                    children.push(input);
                }

                // Disable the children!
                if (children.length > 1) {
                    bootbox.confirm('Åtgärden kommer påverka alla fält i denna grupp och eventuella inmatade värden kan gå förlorade. Är du säkert på att du vill fortsätta?', function (result) {
                        if (result) {
                            disable(children, element);
                            resetFields(resets);
                        }
                    });
                } else {
                    disable(children, element);
                }

            });

            survey.form('.input-group-btn .dropdown-menu .menu-enable').click(function (e) {
                e.preventDefault();

                var element = $(this);
                if (isActive(element)) {
                    return;
                }

                setActive(element);

                var input = getInput(element);
                var hasParent = (input.attr('parent')) ? input.attr('parent').slice(0, -1) : null;

                if (hasParent !== null) {
                    if (hasParent.split(',').length == 2) {
                        // MATRIX
                        if (input.attr('data-sum-of') === undefined) {
                            // Loop all inputs in a div.panel-body!
                            $(this).closest('.panel-body').find('input').each(function () {
                                var el = $(this);
                                if (el.attr('data-sum-of') === undefined && el.attr('data-is-child') !== undefined) {
                                    enableInput(el);
                                    enableDropdown(el);
                                }
                            });
                        }
                    } else {
                        // Disable entire column
                        // Except sum/parent input
                        var parent = $(input.attr('parent').slice(0, -1));
                        var c = parent.attr('data-sum-of').split(' ');

                        for (var i = 0; i < c.length; i++) {
                            var el = $('#' + c[i]);
                            enableInput(el);
                            enableDropdown(el);
                        }
                    }
                } else {
                    enableInput(input);
                }

                updateProgress();
                showChangesNotSaved();
            });
        };
        var updateProgress = function () {
            var total = survey.enabledInputs().length;
            var filled = survey.filledInputs().length;
            var filledPercent = Math.ceil((filled / total) * 100);
            var required = survey.requiredEnabledInputs().length;
            var filledRequired = survey.filledRequiredInputs().length;
            var filledRequiredPercent = Math.ceil((filledRequired / required) * 100);

            var setText = function (text) {
                survey.form('.answers-text').text(text);
            };
            var setPercent = function (percent) {
                survey.form('.answers-progress .progress-bar-success').css('width', percent + '%');
            };
            var setPercentAndText = function (percent) {
                setText('Du har hittills fyllt i ' + percent + '% av hela enkäten');
                setPercent(percent);
            };

            if (filled === 0) {
                setText('Inga fält är ifyllda');
                setPercent(0);
            } else {
                filledPercent = (filled == total) ? 100 : filledPercent;
                setPercentAndText(Math.max(filledPercent, filledRequiredPercent)); // Use filledRequiredPercent if it's higher than filledPercent
            }
        };
        var initProgress = function () {
            $.each(survey.inputs(), function () {
                cell.onChange($(this), function () {
                    updateProgress();
                });
            });
            updateProgress();
        };
        var readOnlyInit = function () {

            /* Enable help button popover. */
            $('.btn-help').popover({
                container: 'body',
                html: true,
                trigger: 'click'
            }).click(function (e) {
                e.preventDefault();
            });

            var initAdmin = function () {
                $('#form-admin .dropdown-menu > li > a').click(function (e) {
                    e.preventDefault();
                    var element = $(this);

                    $('#id_selected_status').val(element.data('key'));
                    element.closest('.dropdown').children('.dropdown-toggle').html(element.text() + ' <span class="caret"></span>');

                    var item = element.closest('li');
                    item.siblings('li').removeClass('active');
                    item.addClass('active');
                });
            };

            var initPassword = function () {
                $('#form-password').bootstrapValidator();
            };

            initAdmin();
            initPassword();
        };
        var showChangesNotSaved = function () {
            isDirty = true;
            $('#unsaved-changes-label').text('Det finns ifyllda svar som inte sparats');
        };

        var getTrimmedValue = function (element) {
          return $.trim(element.val()).replace(",", ".").replace("-", "");
        };

        var checkPartSum = function (partValueEl, valueEl) {
            var partValueElVal = getTrimmedValue($(partValueEl));
            var valueElVal = getTrimmedValue($(valueEl));
          if ($.isNumeric(partValueElVal) && $.isNumeric(valueElVal)) {
              return parseFloat(partValueElVal) <= parseFloat(valueElVal);
          }
          return true;
        };

        return {
            init: function () {

                readOnlyInit();
                if ($('#read_only').val()) {
                    return;
                }

                //Warn user if they leave page before saving changes

                $(window).on('beforeunload', function(event) {

                    // Unlock survey before leaving page
                    //$.get('/surveys/unlock/' + $('#id_key').val(), function() {});

                    if (!isDirty) {
                        return undefined;

                    } else {
                        var confirmMessage = "Det finns osparade ändringar i enkäten.";
                        (event || $(window).event).returnValue = confirmMessage; //Gecko + IE
                        return confirmMessage; //Gecko + Webkit, Safari, Chrome etc.
                    }
                });


                //Validate fields with Bootstrap validator

                survey.form().bootstrapValidator({
                    excluded: ['.disable-validation', ':disabled', ':hidden', ':not(:visible)'],
                    trigger: 'blur',
                    feedbackIcons: null

                }).on('error.validator.bv', function (e, data) { // http://bootstrapvalidator.com/examples/changing-default-behaviour/#showing-one-message-each-time

                    var submit_action = $('#submit_action').val();
                    var showValMessage = $('#valMessageShown').val();

                    if (submit_action && showValMessage == 'true') {
                        $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
                        $('#save-survey-btn').html('Spara');
                        $('#submit-survey-btn').html('Skicka');

                        var messageShown = null;
                        if (submit_action == 'save') {
                            messageShown = "Något eller några värden behöver korrigeras innan du kan spara enkäten. Du måste se till att det inte dykt upp ett rödmarkerat felmeddelande under någon av inmatningsrutorna. Om du inte har möjlighet att ange ett värde kan du klicka på pilen bredvid inmatningsfältet för att välja 'värdet är okänt' i rullisten, alternativt kan du ange '-' om värdet inte är relevant.";
                        }
                        if (submit_action == 'presubmit') {
                            messageShown = "Något eller några värden behöver korrigeras innan du kan skicka in enkäten. Alla obligatoriska fält behöver vara ifyllda och du måste se till att det inte dykt upp ett rödmarkerat felmeddelande under någon av inmatningsrutorna. Om du inte har möjlighet att ange ett värde kan du klicka på pilen bredvid inmatningsfältet för att välja 'värdet är okänt' i rullisten, alternativt kan du ange '-' om värdet inte är relevant.";
                        }

                        bootbox.alert(messageShown, function() {
                        });

                    }

                    $('#valMessageShown').val('false');

                    data.element
                        .data('bv.messages')
                        .find('.help-block[data-bv-for="' + data.field + '"]').hide()
                        .filter('[data-bv-validator="' + data.validator + '"]').show();
                }).on('success.form.bv', function () {

                    var submit_action = $('#submit_action').val();
                    if (!submit_action)
                        return;

                    $('#valMessageShown').val('false');

                    var continuePosting = true; //continue posting if sum checks are passed

                    var showBootBox = false;
                    var messageToShow = null;
                    var elementToFocusOn = null;
                    var elementToScrollTo = null;

                    //Check question 23 part sums
                    var q23partSums = ['#Publ201','#Publ202','#Publ203','#Publ204','#Publ205','#Publ206','#Publ207','#Publ208','#Publ209','#Publ210','#Publ211','#Publ212','#Publ213','#Publ214','#Publ215','#Publ216','#Publ217','#Publ218','#Publ219','#Publ220','#Publ299']
                    var q23Sums = ['#Publ101','#Publ102','#Publ103','#Publ104','#Publ105','#Publ106','#Publ107','#Publ108','#Publ109','#Publ110','#Publ111','#Publ112','#Publ113','#Publ114','#Publ115','#Publ116','#Publ117','#Publ118','#Publ119','#Publ120','#Publ199']

                    var allOk = true;
                    for (var i=0; i < 21; i++) {
                        if (!checkPartSum(q23partSums[i], q23Sums[i])) {
                            allOk = false;
                        }
                    }
                    if (!allOk) {
                        continuePosting = false;
                        showBootBox = true;
                        messageToShow = 'Något eller några av värdena under aktiviteter för barn och unga i den andra kolumnen på fråga 23 är större än det totala antalet aktiviteter som angetts. Du behöver korrigera värdena.';
                        elementToFocusOn = '#Publ201';
                        elementToScrollTo = '#Publ101';
                    }

                    //Check question 14 to make sure sums match
                    var inilan199Value = getTrimmedValue($('#Inilan199'));
                    var omlan299Value = getTrimmedValue($('#Omlan299'));
                    var utlan399Value = getTrimmedValue($('#Utlan399'));
                    var inilanEntered = ($.isNumeric(inilan199Value));
                    var omlanEntered = ($.isNumeric(omlan299Value));
                    var utlanEntered = ($.isNumeric(utlan399Value));

                    if (inilanEntered && omlanEntered && utlanEntered) {
                        if (Number(inilan199Value) + Number(omlan299Value) == Number(utlan399Value)) {
                            // Sum is correct
                        } else {
                            continuePosting = false;
                            showBootBox = true;
                            messageToShow = 'Summan för totalt antal utlån på fråga 14 stämmer inte överens med det totala antalet initiala utlån och omlån. Du måste antingen ändra värdena i kolumnen under Totalt antal utlån eller korrigera summorna för totalt antal initiala utlån samt omlån.';
                            elementToFocusOn = '#Inilan199';
                            elementToScrollTo = '#Inilan101';
                       }

                    }

                    //Check question 14 course literature
                    var q14CourseLitPartSums = ['#Inilan102','#Omlan202','#Utlan302']
                    var q14CourseLitSums = ['#Inilan101','#Omlan201','#Utlan301']

                    allOk = true;
                    for (var i=0; i < 4; i++) {
                        if (!checkPartSum(q14CourseLitPartSums[i], q14CourseLitSums[i])) {
                            allOk = false;
                        }
                    }
                    if (!allOk) {
                        continuePosting = false;
                        showBootBox = true;
                        messageToShow = 'Något eller några av värdena för antal kursböcker, studielitteratur, läromedel samt skolböcker på fråga 14, andra raden, är större än det totala antalet böcker med skriven text som angetts. Du behöver korrigera värdena.';
                        elementToFocusOn = '#Inilan102';
                        elementToScrollTo = '#Inilan101';

                    }

                    //Check question 12 to make sure sums match
                    var titlar199Value = getTrimmedValue($('#Titlar199'));
                    var titlar299Value = getTrimmedValue($('#Titlar299'));
                    var titlar399Value = getTrimmedValue($('#Titlar399'));
                    var titlar499Value = getTrimmedValue($('#Titlar499'));
                    var titlar199Entered = ($.isNumeric(titlar199Value));
                    var titlar299Entered = ($.isNumeric(titlar299Value));
                    var titlar399Entered = ($.isNumeric(titlar399Value));
                    var titlar499Entered = ($.isNumeric(titlar499Value));

                    if (titlar199Entered && titlar299Entered && titlar399Entered && titlar499Entered) {
                        if (Number(titlar199Value) + Number(titlar299Value) + Number(titlar399Value) == Number(titlar499Value)) {
                            // Sum is correct;
                        } else {
                            continuePosting = false;
                            showBootBox = true;
                            messageToShow = 'Summan för totalt antal titlar på fråga 12 stämmer inte överens med det totala antalet titlar på svenska, nationella minoritetsspråk och utländska språk. Du måste antingen ändra värdena i kolumnen under Totalt antal titlar eller korrigera summorna för totalt antal titlar på svenska, minoritetsspråk samt utländska språk.';
                            elementToFocusOn = '#Titlar199';
                            elementToScrollTo = '#Titlar101';
                        }

                    }

                    //Check question 10 part sums
                    var q10partSums = ['#Bestand201','#Bestand202','#Bestand203','#Bestand204','#Bestand205','#Bestand206','#Bestand207','#Bestand208','#Bestand209','#Bestand210','#Bestand211','#Bestand212','#Bestand213','#Bestand299']
                    var q10Sums = ['#Bestand101','#Bestand102','#Bestand103','#Bestand104','#Bestand105','#Bestand106','#Bestand107','#Bestand108','#Bestand109','#Bestand110','#Bestand111','#Bestand112','#Bestand113','#Bestand199']

                    allOk = true;
                    for (var i=0; i < 14; i++) {
                        if (!checkPartSum(q10partSums[i], q10Sums[i])) {
                            allOk = false;
                        }
                    }
                    if (!allOk) {
                        continuePosting = false;
                        showBootBox = true;
                        messageToShow = 'Något eller några av värdena under fysiskt nyförvärv i den andra kolumnen på fråga 10 är större än det totala fysiska beståndet som angetts. Du behöver korrigera värdena.';
                        elementToFocusOn = '#Bestand201';
                        elementToScrollTo = '#Bestand101';

                    }

                    //Check question 10 course literature
                    var q10CourseLitPartSums = ['#Bestand102','#Bestand202','#Bestand302']
                    var q10CourseLitSums = ['#Bestand101','#Bestand201','#Bestand301']

                    allOk = true;
                    for (var i=0; i < 4; i++) {
                        if (!checkPartSum(q10CourseLitPartSums[i], q10CourseLitSums[i])) {
                            allOk = false;
                        }
                    }
                    if (!allOk) {
                        continuePosting = false;
                        showBootBox = true;
                        messageToShow = 'Något eller några av värdena för antal kursböcker, studielitteratur, läromedel samt skolböcker på fråga 10, andra raden, är större än det antal böcker med skriven text som angetts. Du behöver korrigera värdena.';
                        elementToFocusOn = '#Bestand102';
                        elementToScrollTo = '#Bestand101';

                    }

                    //Warn user by showing message box
                    if (showBootBox) {

                        $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
                        $('#save-survey-btn').html('Spara');
                        $('#submit-survey-btn').html('Skicka');

                        bootbox.alert(messageToShow, function() {

                                $(elementToFocusOn).focus();
                                setTimeout(function () {
                                    $('html, body').animate({
                                        scrollTop: $(elementToScrollTo).offset().top - 30
                                    }, 100);
                                }, 100);
                            }); //End bootbox alert
                    }

                    if (continuePosting) {
                        // On successful form-format-validation and sum checks, if submit_action -> ajax post form

                        if (submit_action == "save") {
                            $('#save-survey-btn').html('<i class="fa fa-spinner fa-spin"></i> Sparar...');
                        } else if (submit_action == "presubmit") {
                            $('#submit-survey-button').html('<i class="fa fa-spinner fa-spin"></i> Sparar...');
                        } else if (submit_action == "submit") {
                            $('#submit-survey-button').html('<i class="fa fa-spinner fa-spin"></i> Skickar...');
                        }

                        $('#altered_fields').val(survey.changeableInputs().filter(function () {
                            return $(this).val() != $(this).attr('data-original-value');
                        }).map(function () {
                            return $(this).attr('id');
                        }).get().join(' '));

                        var unknownInputs = $('.value-unknown');

                        var unknownInputIds = unknownInputs.map(function () {
                            return $(this).attr('id');
                        }).get().join(' ');
                        $('#unknown_inputs').val(unknownInputIds);

                        var disabledInputIds = survey.disabledInputs().map(function () {
                            return $(this).attr('id');
                        }).get().join(' ');
                        $('#disabled_inputs').val(disabledInputIds);

                        $('#selected_libraries').val(survey.selectedLibraries());

                        survey.form().attr('action', Urls.survey(survey.form('#id_key').val()));

                        $.ajax({
                            url: '/surveys/' + $('#id_key').val(),
                            type: 'POST',
                            data: $('#survey-form').serialize().replace(/Obligatorisk/g, ''), //KP
                            success: function (result) {
                                $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
                                $('#save-survey-btn').html('Spara');
                                $('#submit-survey-btn').html('Skicka');


                                if (submit_action == 'save') {

                                    isDirty = false;

                                    // Hide message after 5 sec (5000ms)
                                    $('#unsaved-changes-label').html('<strong>Formuläret är nu sparat.</strong>');
                                    setTimeout(function () {
                                        $('#unsaved-changes-label').html('');
                                    }, 5000);

                                } else if (submit_action == 'presubmit') {

                                    $('#submit-confirm-modal').modal('show');

                                } else if (submit_action == 'submit') {
                                    // Hide bootstrap modal
                                    $('#submit-confirm-modal').modal('hide');
                                    // Hide bootstrap navbar (footer)
                                    $('.navbar-fixed-bottom').hide();
                                    // Disable all inputs
                                    survey.inputs().attr('readonly', true);
                                    // Disable all dropdown-togglers
                                    $('input[type="checkbox"]').attr('disabled', true);
                                    // Disable all dropdown-togglers
                                    $('.btn-dropdown').attr('disabled', true);
                                    // Don't show status message about unsaved changes
                                    $('#unsaved-changes-label').html('');

                                    isDirty = false;

                                    $('.jumbotron-submitted').show();

                                    $('html, body').animate({
                                        scrollTop: ($('.jumbotron-submitted').first().offset().top - 60)
                                    }, 100);
                                }

                            },
                            // handle a non-successful response
                            error: function () {
                                alert('Ett fel uppstod! Var vänlig försök igen.');
                                $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
                                $('#save-survey-btn').html('Spara');
                                $('#submit-survey-btn').html('Skicka');
                            }
                        }); //End ajax

                    }


                }).on('error.form.bv', function () {
                    $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
                    $('#save-survey-btn').html('Spara');
                    $('#submit-survey-btn').html('Skicka');
                    var invalidField = survey.validator().getInvalidFields().first();
                    setTimeout(function () {
                        $('html, body').animate({
                            scrollTop: invalidField.offset().top - 150
                        }, 100);
                    }, 100);
                });

                var submitTo = function (action, submit) {
                    submit = submit || false;
                    var element = $('.publish-survey-responses-form').get(0);
                    element.setAttribute('action', Urls[action]());
                    if (submit) {
                        element.submit();
                    }
                    return element;
                };

                $('#surveys_active').click(function (e) {
                    e.preventDefault();
                    if ($('#surveys_state').val() != 'active') {
                        $('#surveys_state').val('active');
                        $('#surveys_filter_form').submit();
                    }
                });
                $('#surveys_inactive').click(function (e) {
                    e.preventDefault();
                    if ($('#surveys_state').val() != 'inactive') {
                        $('#surveys_state').val('inactive');
                        $('#surveys_filter_form').submit();
                    }
                });
                $('#export-surveys-modal .btn-confirm').click(function (e) {
                    e.preventDefault();
                    $('#export-surveys-modal').modal('hide');
                    submitTo('surveys_export', true);
                });
                $('.btn-change-status').click(function (e) {
                    e.preventDefault();
                    submitTo('surveys_statuses', true);
                });
                $('.btn-activate-surveys').click(function (e) {
                    e.preventDefault();
                    submitTo('surveys_activate', true);
                });
                $('.btn-inactivate-surveys').click(function (e) {
                    e.preventDefault();
                    submitTo('surveys_inactivate', true);
                });
                $('.btn-dispatch').click(function (e) {
                    e.preventDefault();

                    var checked = $('.select-one:checked').first();
                    var library = checked.data('library');
                    var address = checked.data('url-base') + checked.data('address');
                    var city = checked.data('city');

                    submitTo('dispatches');
                    dispatch.init(library, address, city, function (unsavedChanges) {
                        var button = $('.btn-dispatch');

                        if (unsavedChanges) {
                            button.text('Skapa utskick*');
                            button.attr('data-original-title', 'Det finns ett påbörjat utskick.');
                        } else {
                            button.text('Skapa utskick');
                            button.attr('data-original-title', '');
                        }
                    });
                });


                $('.col-sm-2 .form-control').focus(function () {
                    if ($(window).width() <= 992) {
                        var inputGroup = $(this).parent('.input-group');

                        inputGroup
                            .css('width', (inputGroup.outerWidth() * 1.5))
                            .addClass('expanded');
                    }
                }).blur(function () {
                    var inputGroup = $(this).parent('.input-group');

                    inputGroup
                        .css('width', '')
                        .removeClass('expanded');
                });

                // Update thousands separators (spaces)
                var numericalInputs = survey.form('input.numerical');
                numericalInputs.change(function (e) {
                    cell.updateThousandsSeparators(this);
                });
                numericalInputs.trigger('keyup');

                // Make input text red if value far from previous year's value
                numericalInputs.change(function (e) {
                    var value = cell.number(this);
                    var previousValue = Number(
                        $(this).attr('data-previous-value')
                    );
                    if (isNaN(value) || isNaN(previousValue)) {
                        $(this).removeClass('largeDiffFromPrevious');
                        return;
                    }
                    var tolerance = 0.1  // 10% of previous year's value
                    var diffLimit = Math.abs(tolerance * previousValue);
                    if (Math.abs(value - previousValue) > diffLimit) {
                        $(this).addClass('largeDiffFromPrevious');
                    } else {
                        $(this).removeClass('largeDiffFromPrevious');
                    }
                });
                numericalInputs.trigger('change');

                survey.form('#save-survey-btn').click(function (e) {
                    e.preventDefault();

                    $('#submit_action').val('save');

                    if ($('#valMessageShown').length) {
                        $('#valMessageShown').val('true');
                    } else {
                        survey.form().append('<input type="hidden" id="valMessageShown" value="true">');
                    }

                    var saveButton = $(this);
                    var saveButtonHtml = saveButton.html();
                    var otherButtons = $('#submit-survey-btn,#print-survey-btn');

                    saveButton.html('<i class="fa fa-spinner fa-spin"></i> Kontrollerar...').addClass('disabled');
                    otherButtons.addClass('disabled');

                    setTimeout(function () {
                        var empty = survey.emptyInputs();
                        empty.addClass('disable-validation'); // Save doesn't validate empty required fields (only done on submit)

                        var validator = survey.validator();
                        validator.validate();
                        empty.removeClass('disable-validation');
                    }, 100);
                });

                survey.form('#submit-survey-btn').click(function (e) {
                    e.preventDefault();

                    $('#submit_action').val('presubmit');

                    if ($('#valMessageShown').length) {
                        survey.form('#valMessageShown').val('true');
                    } else {
                        survey.form().append('<input type="hidden" id="valMessageShown" value="true">');
                    }

                    var submitButton = $(this);
                    var submitButtonHtml = submitButton.html();
                    var otherButtons = $('#save-survey-btn,#print-survey-btn');

                    submitButton.html('<i class="fa fa-spinner fa-spin"></i> Kontrollerar...').addClass('disabled');
                    otherButtons.addClass('disabled');

                    setTimeout(function () {
                        var validator = survey.validator();
                        validator.validate();
                    }, 100);
                });

                survey.form('#faq-survey-btn').click(function (e) {
                    e.preventDefault();

                    var button = $(this);

                    if (button.attr('data-scroll-to')) {
                        $('html, body').animate({
                            scrollTop: button.attr('data-scroll-to')
                        }, 100);
                        button
                            .html('<i class="fa fa-question fa-inline"></i>Vanliga frågor')
                            .removeAttr('data-scroll-to');
                    } else {
                        var yPos = $(document).scrollTop();
                        button
                            .html('<i class="fa fa-question fa-inline"></i>Ta mig tillbaka')
                            .attr('data-scroll-to', yPos);

                        $('html, body').animate({
                            scrollTop: ($('#panel-help-top').offset().top - 60)
                        }, 100);
                    }
                });

                /* survey.form('#show-more-libraries').click(function (e) {
                 event.preventDefault();
                 var button = $(this);
                 var oldText = button.text();
                 button
                 .text( button.attr('data-display-text') )
                 .attr('data-display-text', oldText)
                 .blur();

                 $('tr.library').toggleClass('expanded');
                 return false;
                 });*/

                $('#confirm-submit-survey-btn').click(function (e) {
                    e.preventDefault();

                    $('#submit_action').val('submit');

                    setTimeout(function () {
                        survey.validator().validate();
                    }, 100);
                });


                cell.onChange(survey.changeableInputs(), function () {
                    this.value = $.trim(this.value);
                    showChangesNotSaved();
                });

                /* FAQ Panel */
                var setIcon = function (id, state) {
                    var icon = $('a[href="#' + id + '"]').siblings('.fa');

                    if (state == 'collapse') {
                        icon.removeClass('fa-angle-down');
                        icon.addClass('fa-angle-right');
                    } else if (state == 'show') {
                        icon.removeClass('fa-angle-right');
                        icon.addClass('fa-angle-down');
                    }
                };


                $('#panel-help .collapse').on('show.bs.collapse', function () {
                    setIcon($(this).attr('id'), 'show');
                }).on('hide.bs.collapse', function () {
                    setIcon($(this).attr('id'), 'collapse');
                });

                $('.modified-after-publish').on('click', function (e) {
                    e.preventDefault();
                });

                $('.tooltip-wrapper').tooltip({
                    position: 'bottom'
                });
                $('.survey-popover').tooltip();
                $('input').placeholder();

                sum.init();
                initDropdown();
                initProgress();

                bootbox.setLocale('sv');

                // Prevent form submission with enter key.
                $(function () {
                    $(document).on('keydown', survey.form().selector + ' input', function (e) {
                        if (e.which == 13) {
                            e.preventDefault();
                            return false;
                        }
                    });
                    survey.form('input').keyup(function () {
                        var input = $(this);
                        if (input.prop('data-bv-numeric')) {
                            var value = input.val().replace(/\./g, ',');
                            if (input.val() !== value) input.val(value);
                        }
                    });
                });
            }
        };
    });
