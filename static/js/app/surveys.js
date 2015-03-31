/*global define,Urls*/
define(['jquery', 'surveys.dispatch'],
  function($, dispatch) {
    'use strict';

    return {
      init: function() {

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

        $('.modified-after-publish').on('click', function(e) {
          e.preventDefault();
        });

        $(document).tooltip({
          selector: '.survey-popover',
        });

      }
    };
  });