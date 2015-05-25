/*global define,Urls,alert*/
define(['jquery', 'bootbox', 'survey.sum', 'survey.cell', 'surveys.dispatch', 'bootstrap.validator.sv', 'jquery.placeholder'],
  function($, bootbox, sum, cell, dispatch) {
    'use strict';
    var _form = $('#survey-form');
    var _inputs = null;

    var survey = {
      form: function(selector) {
        if (selector) {
          return _form.find(selector);
        } else {
          return _form;
        }
      },
      validator: function() {
        return survey.form().data('bootstrapValidator');
      },
      inputs: function() {
        if (!_inputs) _inputs = survey.form('input:not([type="checkbox"])').not('[type="hidden"]');
        return _inputs;
      },
      changeableInputs: function() {
        return survey.form('input:not([type="checkbox"]),textarea').not('[type="hidden"]').not('.form-excluded');
      },
      disabledInputs: function() {
        return survey.inputs().filter('[disabled]');
      },
      enabledInputs: function() {
        return survey.inputs().not('[disabled]');
      },
      selectedLibraries: function() {
        return survey.form('.select-library:checked').map(function() {
          return $(this).attr('name');
        }).get().join(' ');
      },
      filledInputs: function() {
        return survey.enabledInputs().filter(function() {
          return $(this).val();
        });
      },
      emptyInputs: function() {
        return survey.enabledInputs().filter(function() {
          return !$(this).val();
        });
      },
      correctInputs: function() {
        return survey.enabledInputs().filter(function() {
          return this.value && $(this).closest('.form-group').hasClass('has-success');
        });
      },
      requiredInputs: function() {
        return survey.enabledInputs().filter('[data-bv-notempty]');
      },
      sumOfInputs: function() {
        return survey.enabledInputs().filter('[data-sum-of]');
      }
    };

    var initDropdown = function() {
      var isActive = function(element) {
        var parent = element.parent('li');
        return parent.hasClass('active');
      };
      var setActive = function(element) {
        var parent = element.parent('li');
        parent.siblings('li').removeClass('active');
        parent.addClass('active');
      };
      var getInput = function(element) {
        return element.closest('.input-group-btn').prev('input');
      };
      var disableInput = function(input, element) {
        survey.validator().updateStatus(input.attr('name'), 'NOT_VALIDATED');
        input.css('padding-right', '0px');
        input.val(element.text());
        input.prop('disabled', true);
        input.addClass('value-unknown');
      };
      var enableInput = function(input) {
        input.css('padding-right', '');

        // Empty input if text and NOT A NUMBER
        if (!((input.val() - 0) == input.val() && ('' + input.val()).trim().length > 0)) {
          input.val('0');
        }

        input.prop('disabled', false);
        input.removeClass('value-unknown');
      };
      var setActiveSiblings = function(input) {

        var dropdown = input.next('.input-group-btn').children('.btn-dropdown');

        var disableInput = dropdown.siblings('.dropdown-menu').find('.menu-disable-input');
        setActive(disableInput);

      };
      var enableDropdown = function(input) {
        var dropdown = input.next('.input-group-btn').children('.btn-dropdown');
        dropdown.prop('disabled', false);

        var enable = dropdown.siblings('.dropdown-menu').find('.menu-enable');
        setActive(enable);
      };
      var disable = function(inputs, element) {
        for (var index in inputs) {
          disableInput(inputs[index], element);
          setActiveSiblings(inputs[index]);
        }

        if (!isActive(element))
          showChangesNotSaved();

        setActive(element);

        updateProgress();
      };

      var resetFields = function(elements) {
        for (var i = 0; i < elements.length; i++) {
          if (!elements[i].prop('disabled')) {
            elements[i].val('');
            survey.validator().updateStatus(elements[i].attr('name'), 'NOT_VALIDATED');
          }
        }
      };

      survey.form('.input-group-btn .dropdown-menu .menu-disable-input').click(function(e) {
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
              $(this).closest('.panel-body').find('input').each(function() {
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
          bootbox.confirm('Åtgärden kommer påverka alla fält i denna grupp och eventuella inmatade värden kan gå förlorade. Är du säkert på att du vill fortsätta?', function(result) {
            if (result) {
              disable(children, element);
              resetFields(resets);
            }
          });
        } else {
          disable(children, element);
        }

      });

      survey.form('.input-group-btn .dropdown-menu .menu-enable').click(function(e) {
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
              $(this).closest('.panel-body').find('input').each(function() {
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
    var updateProgress = function() {
      var total = survey.enabledInputs().length;
      var correct = survey.correctInputs().length;
      var percent = (correct / total) * 100;

      var requiredPercent = Math.ceil((survey.requiredInputs().length / total) * 100);
      var boostedPercent = Math.ceil(1.15 * percent);

      var setText = function(text) {
        survey.form('.answers-text').text(text);
      };
      var setPercent = function(percent) {
        survey.form('.answers-progress .progress-bar-success').css('width', percent + '%');
      };
      var setPercentAndText = function(percent) {
        setText('Du har hittills fyllt i ' + percent + '% av hela enkäten');
        setPercent(percent);
      };

      if (correct === 0) {
        setText('Inga fält är ifyllda');
        setPercent(0);
      } else if (boostedPercent <= requiredPercent) {
        setPercentAndText(Math.min(boostedPercent, requiredPercent));
      } else {
        percent = (correct == total) ? 100 : Math.ceil(percent);
        setPercentAndText(Math.max(percent, requiredPercent));
      }
    };
    var initProgress = function() {
      $.each(survey.inputs(), function() {
        cell.onChange($(this), function() {
          updateProgress();
        });
      });
      updateProgress();
    };
    var readOnlyInit = function() {

      /* Enable help button popover. */
      $('.btn-help').popover({
        container: 'body',
        title: function() {
          return 'Förklaring' + '<button class="close" style="line-height: inherit;">&times</button>';
        },
        html: true,
        trigger: 'focus'
      }).click(function(e) {
        e.preventDefault();
      }).on('shown.bs.popover', function() {
        var button = $(this);
        $('.popover button.close').click(function() {
          button.popover('hide');
        });
      });

      var initAdmin = function() {
        $('#form-admin .dropdown-menu > li > a').click(function(e) {
          e.preventDefault();
          var element = $(this);

          $('#id_selected_status').val(element.data('key'));
          element.closest('.dropdown').children('.dropdown-toggle').html(element.text() + ' <span class="caret"></span>');

          var item = element.closest('li');
          item.siblings('li').removeClass('active');
          item.addClass('active');
        });
      };

      var initPassword = function() {
        $('#form-password').bootstrapValidator();
      };

      initAdmin();
      initPassword();
    };
    var showChangesNotSaved = function() {
      $('#unsaved-changes-label').text('Det finns ifyllda svar som inte sparats');
    };
    return {
      init: function() {

        readOnlyInit();
        if ($('#read_only').val()) {
          return;
        }

        survey.form().bootstrapValidator({
          excluded: ['.disable-validation', ':disabled', ':hidden', ':not(:visible)'],
          trigger: 'blur',
          feedbackIcons: null

        }).on('error.validator.bv', function(e, data) { // http://bootstrapvalidator.com/examples/changing-default-behaviour/#showing-one-message-each-time
          data.element
            .data('bv.messages')
            .find('.help-block[data-bv-for="' + data.field + '"]').hide()
            .filter('[data-bv-validator="' + data.validator + '"]').show();
        }).on('success.form.bv', function() {
          var submit_action = $('#submit_action').val();
          if (!submit_action)
            return;

          $('#altered_fields').val(survey.changeableInputs().filter(function() {
            return $(this).val() != $(this).attr('data-original-value');
          }).map(function() {
            return $(this).attr('id');
          }).get().join(' '));

          var unknownInputs = $('.value-unknown');

          var unknownInputIds = unknownInputs.map(function() {
            return $(this).attr('id');
          }).get().join(' ');
          $('#unknown_inputs').val(unknownInputIds);

          var disabledInputIds = survey.disabledInputs().map(function() {
            return $(this).attr('id');
          }).get().join(' ');
          $('#disabled_inputs').val(disabledInputIds);

          $('#selected_libraries').val(survey.selectedLibraries());

          survey.form().attr('action', Urls.survey(survey.form('#id_key').val()));

          $.ajax({
            url: '/surveys/' + $('#id_key').val(),
            type: 'POST',
            data: $('#survey-form').serialize(),
            success: function(result) {
              $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
              $('#save-survey-btn').html('Spara');

                // If there are errors -> update validators and revalidate

                if (result.errors.length > 0) {

                  var sumElements = survey.form('[data-sum-of]');

                  sumElements.each(function(index, sumElement){
                    console.log(sumElement);
                    for (var i in result.errors) {
                      var fieldName = $(sumElement).attr('name')
                      if (result.errors[i].fieldName == fieldName) {
                        survey.validator().updateStatus(fieldName,'INVALID','numeric');
                        survey.validator().updateMessage(fieldName, 'numeric', result.errors[i].errorMessage);
                      } else {
                        survey.validator().resetField(sumElement, true);
                      }
                      console.log("Revalidating form on return...");
                      survey.validator().validate()
                    }
                  });


                // Else -> save or submit

                } else {

                  if (submit_action == 'save') {

                    // Hide message after 5 sec (5000ms)
                    $('#unsaved-changes-label').html('<strong>Formuläret är nu sparat.</strong>');
                    setTimeout(function() {
                      $('#unsaved-changes-label').html('');
                    }, 5000);

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

                    alert('Formuläret är skickat!');
                  }

                }

            },
            // handle a non-successful response
            error: function() {
              alert('Ett fel uppstod! Var vänlig försök igen.');
              $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
              $('#save-survey-btn').html('Spara');
            }
          });
        }).on('error.form.bv', function() {
          var invalidField = survey.validator().getInvalidFields().first();
          $('html, body').animate({
            scrollTop: invalidField.offset().top - 10
          }, 300);
        });

        var submitTo = function(action, submit) {
          submit = submit || false;
          var element = $('.publish-survey-responses-form').get(0);
          element.setAttribute('action', Urls[action]());
          if (submit) {
            element.submit();
          }
          return element;
        };

        $('#surveys_active').click(function(e) {
          e.preventDefault();
          if ($('#surveys_state').val() != 'active') {
            $('#surveys_state').val('active');
            $('#surveys_filter_form').submit();
          }
        });
        $('#surveys_inactive').click(function(e) {
          e.preventDefault();
          if ($('#surveys_state').val() != 'inactive') {
            $('#surveys_state').val('inactive');
            $('#surveys_filter_form').submit();
          }
        });
        $('#export-surveys-modal .btn-confirm').click(function(e) {
          e.preventDefault();
          $('#export-surveys-modal').modal('hide');
          submitTo('surveys_export', true);
        });
        $('.btn-change-status').click(function(e) {
          e.preventDefault();
          submitTo('surveys_statuses', true);
        });
        $('.btn-activate-surveys').click(function(e) {
          e.preventDefault();
          submitTo('surveys_activate', true);
        });
        $('.btn-inactivate-surveys').click(function(e) {
          e.preventDefault();
          submitTo('surveys_inactivate', true);
        });
        $('.btn-dispatch').click(function(e) {
          e.preventDefault();

          var checked = $('.select-one:checked').first();
          var library = checked.data('library');
          var address = checked.data('url-base') + checked.data('address');
          var city = checked.data('city');

          submitTo('dispatches');
          dispatch.init(library, address, city, function(unsavedChanges) {
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


        $('.col-sm-2 .form-control').focus(function() {
          if ($(window).width() <= 992) {
            var inputGroup = $(this).parent('.input-group');

            inputGroup
              .css('width', (inputGroup.outerWidth() * 1.5))
              .addClass('expanded');
          }
        }).blur(function() {
          var inputGroup = $(this).parent('.input-group');

          inputGroup
            .css('width', '')
            .removeClass('expanded');
        });


        survey.form('#save-survey-btn').click(function(e) {
          e.preventDefault();

          $('#submit_action').val('save');

          var saveButton = $(this);
          var saveButtonHtml = saveButton.html();
          var otherButtons = $('#submit-survey-btn,#print-survey-btn');

          saveButton.html('<i class="fa fa-spinner fa-spin"></i> Kontrollerar...').addClass('disabled');
          otherButtons.addClass('disabled');

          setTimeout(function() {
            var empty = survey.emptyInputs();
            empty.addClass('disable-validation');

            console.log("Validating form before saving...");
            var validator = survey.validator();
            validator.validate();

            if (!validator.isValid()) {
              saveButton.html(saveButtonHtml).removeClass('disabled');
              otherButtons.removeClass('disabled');
            } else {
              $('#unsaved-changes-label').text('');
              saveButton.html('<i class="fa fa-spinner fa-spin"></i> Sparar...');
            }

            empty.removeClass('disable-validation');
          }, 100);
        });

        survey.form('#submit-survey-btn').click(function(e) {
          e.preventDefault();

          $('#submit_action').val('');

          var submitButton = $(this);
          var submitButtonHtml = submitButton.html();
          var otherButtons = $('#save-survey-btn,#print-survey-btn');

          submitButton.html('<i class="fa fa-spinner fa-spin"></i> Kontrollerar...').addClass('disabled');
          otherButtons.addClass('disabled');

          setTimeout(function() {
            var validator = survey.validator();
            validator.validate();
            if (validator.isValid()) {
              $('#submit-confirm-modal').modal('show');
            }

            submitButton.html(submitButtonHtml).removeClass('disabled');
            otherButtons.removeClass('disabled');
          }, 100);
        });

        survey.form('#faq-survey-btn').click(function(e) {
          e.preventDefault();

          var button = $(this);

          if (button.attr('data-scroll-to')) {
            $('html, body').animate({
              scrollTop: button.attr('data-scroll-to')
            }, 1000);
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
            }, 1000);
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

        $('#confirm-submit-survey-btn').click(function(e) {
          e.preventDefault();

          $('#submit_action').val('submit');

          setTimeout(function() {
            survey.validator().validate();
          }, 100);
        });


        cell.onChange(survey.changeableInputs(), function() {
          showChangesNotSaved();
        });

        /* FAQ Panel */
        var setIcon = function(id, state) {
          var icon = $('a[href="#' + id + '"]').siblings('.fa');

          if (state == 'collapse') {
            icon.removeClass('fa-angle-down');
            icon.addClass('fa-angle-right');
          } else if (state == 'show') {
            icon.removeClass('fa-angle-right');
            icon.addClass('fa-angle-down');
          }
        };


        $('#panel-help .collapse').on('show.bs.collapse', function() {
          setIcon($(this).attr('id'), 'show');
        }).on('hide.bs.collapse', function() {
          setIcon($(this).attr('id'), 'collapse');
        });

        $('.modified-after-publish').on('click', function(e) {
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
        $(function() {
          $(document).on('keydown', survey.form().selector + ' input', function(e) {
            if (e.which == 13) {
              e.preventDefault();
              return false;
            }
          });
          survey.form('input').keyup(function() {
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