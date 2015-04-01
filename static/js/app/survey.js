/*global define,Urls,alert*/
define(['jquery', 'bootbox', 'survey.sum', 'survey.cell', 'formValidation.sv', 'formValidation.bootstrap', 'jquery.placeholder', 'jquery.scrollTo'],
  function($, bootbox, sum, cell) {
    'use strict';
    var _form = $('#survey-form'),
      _inputs = null,
      _scrollToDelay = 300;

    var survey = {
      form: function(selector) {
        if (selector) {
          return _form.find(selector);
        } else {
          return _form;
        }
      },
      validator: function() {
        return survey.form().data('formValidation');
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
        return survey.enabledInputs().filter('[required]');
      },
      requiredEmptyInputs: function() {
        return survey.enabledInputs().filter(function() {
          return !$(this).val() && $(this).is('[required]');
        });
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

      survey.form('.input-group-btn .dropdown-menu .menu-disable-input').on('click', function(e) {
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

      survey.form('.input-group-btn .dropdown-menu .menu-enable').on('click', function(e) {
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
    var updateProgress = function(onInit) {
      var correctInputsLength = survey.correctInputs().length;
      if(onInit) {
        correctInputsLength = survey.filledInputs().length;
      }
      var totalInputsLength = survey.enabledInputs().length,
        requiredInputsLength = survey.requiredInputs().length,
        requiredEmptyInputsLength = survey.requiredEmptyInputs().length,
        correctInputsPercentage = Math.ceil((correctInputsLength / totalInputsLength) * 100),
        requiredPercent = Math.ceil((requiredInputsLength / totalInputsLength) * 100),
        setText = function(text) {
          survey.form('.answers-text').html(text);
        },
        setPercent = function(percent) {
          survey.form('.answers-progress .progress-bar-success').css('width', percent + '%');
        },
        setPercentAndText = function(percent) {
          setText('Du har hittills fyllt i <strong>'+ percent +'%</strong> av hela enkäten.<br>Du har <strong>'+ requiredEmptyInputsLength +'</strong> obligatoriska fält kvar att fylla i.');
          setPercent(percent);
        };
      if (correctInputsLength === 0) {
        setText('Du har inte börjat fylla i enkäten ännu.');
        setPercent(0);
      } else {
        setPercentAndText(correctInputsPercentage);
      }
    };
    var initProgress = function() {
      $.each(survey.inputs(), function() {
        cell.onChange($(this), function() {
          updateProgress();
        });
      });
      updateProgress(true);
    };
    var toggleChevron = function(e) {
      $(e.target)
        .siblings('.panel-heading')
        .find('i.fa')
        .toggleClass('fa-rotate-90');
    };
    var focusFirst = function(e) {
      $(e.target)
        .find('input')
        .first()
        .focus();
    };
    var initAccordion = function()  {
      survey.form().on('hide.bs.collapse show.bs.collapse', toggleChevron);
      survey.form().on('shown.bs.collapse', focusFirst);
      $('[role="tabpanel"]').on('shown.bs.collapse', function() {
        $.scrollTo($(this).siblings('.panel-heading').find('h2'), _scrollToDelay, {
          offset: -30
        });
      });
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
      }).on('click', function(e) {
        e.preventDefault();
      }).on('shown.bs.popover', function() {
        var button = $(this);
        $('.popover button.close').on('click', function() {
          button.popover('hide');
        });
      });

      var initAdmin = function() {
        $('#form-admin .dropdown-menu > li > a').on('click', function(e) {
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
        $('#form-password').formValidation();
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
        survey.form()
          .on('init.form.fv', function()  {
            $(document).tooltip({
              selector: '[data-toggle="tooltip"]',
              placement: 'bottom'
            });
            $('input').placeholder();
            sum.init();
            initDropdown();
          })
          .formValidation({
            framework: 'bootstrap',
            excluded: '.disable-validation',
            trigger: 'blur',
            locale: 'sv_SE',
            icon: null,
            fields: {
              integer: {
                selector: '.type-integer',
                validators: {
                  greaterThan: {
                    inclusive: '',
                    value: 0
                  },
                  integer: {}
                }
              },
              email: {
                selector: '.type-email',
                validators: {
                  regexp: {
                    regexp: /.+@.+\..+/,
                    message: 'Vänligen mata in en giltig e-postadress'
                  },
                  emailAddress: {}
                }
              },
              numeric: {
                selector: '.type-numeric',
                validators: {
                  greaterThan: {
                    inclusive: '',
                    value: 0
                  },
                  numeric: {
                    separator: ','
                  },
                  regexp: {
                    regexp: /^\d+(\,\d{1,3})?$/,
                    message: 'Vänligen mata in ett nummer med max 3 decimaler (tex 12,522)'
                  }
                }
              },
              text: {
                selector: '.type-text',
                validators: {
                  stringLength: {
                    min: 0
                  }
                }
              }
            }
          })
          .on('err.validator.fv', function(e, data) { // http://bootstrapvalidator.com/examples/changing-default-behaviour/#showing-one-message-each-time
            data.element
              .data('fv.messages')
              .find('.help-block[data-fv-for="' + data.field + '"]').hide()
              .filter('[data-fv-validator="' + data.validator + '"]').show();
          })
          .on('success.form.fv', function() {
            var submit_action = $('#submit_action').val();
            if (!submit_action) {
              return;
            }

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
              success: function() {
                $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
                $('#save-survey-btn').html('Spara');

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

              },
              // handle a non-successful response
              error: function() {
                alert('Ett fel uppstod! Var vänlig försök igen.');
                $('#print-survey-btn, #save-survey-btn, #submit-survey-btn').removeClass('disabled');
                $('#save-survey-btn').html('Spara');
              }
            });
          })
          .on('err.form.fv', function() {
            var $invalidField = $(survey.validator().getInvalidFields().first());
            $invalidField
              .closest('.panel-wrapper')
              .find('.section-title.collapsed')
              .click();
            $.scrollTo($invalidField, _scrollToDelay, {
              offset: -30,
              complete: function() {
                $invalidField.focus();
              }
            });
          });

        // Open next section when using tab key from last input in current section
        survey.form('.panel-wrapper').each(function() {
          var $this = $(this);
          $this.find('input, textarea').last().on('keydown', function(e) {
            if (e.which == 9) {
              $this.next('.panel-wrapper').find('.section-title').click();
            }
          });
        });

        // Open next section when clicking the 'Nästa' button
        survey.form('.btn-next').on('click', function() {
          var $this = $(this);
          $this.closest('.panel-wrapper').next('.panel-wrapper').find('.section-title').click();
        });

        // Save survey when clicking the 'Spara' button
        survey.form('#save-survey-btn').on('click', function(e) {
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

        // Validate survey and open confirm modal when clicking the 'Skicka' button
        survey.form('#submit-survey-btn').on('click', function(e) {
          e.preventDefault();

          $('#submit_action').val('');

          var $submitButton = $(this),
            $validating = $('.validating'),
            submitButtonHtml = $submitButton.html(),
            otherButtons = $('#save-survey-btn, #print-survey-btn');

          $validating.css({'display': 'table'});
          $submitButton.html('<i class="fa fa-spinner fa-pulse"></i> Kontrollerar...').addClass('disabled');
          otherButtons.addClass('disabled');

          setTimeout(function() {
            var validator = survey.validator();
            validator.validate();
            if (validator.isValid()) {
              $('#submit-confirm-modal').modal('show');
            }

            $validating.css({'display': 'none'});
            $submitButton.html(submitButtonHtml).removeClass('disabled');
            otherButtons.removeClass('disabled');
          }, 100);
        });

        survey.form('#faq-survey-btn').on('click', function(e) {
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

        $('#confirm-submit-survey-btn').on('click', function(e) {
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

        initProgress();
        initAccordion();

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
            if (input.prop('data-fv-numeric')) {
              var value = input.val().replace(/\./g, ',');
              if (input.val() !== value) input.val(value);
            }
          });
        });
      }
    };
  });