define(['jquery', 'survey', 'login', 'jquery.tablesorter', 'bootstrap', 'bootstrap.datepicker', 'bootstrap.tokenfield',
    'typeahead', 'underscore'], function ($, survey, login) {

    window.ellipsis = function (text, max_chars) {
        max_chars = max_chars || 50;
        if (text && text.length > max_chars) {
            return text.substr(0, max_chars) + " ...";
        }
        return text;
    };

    $(document).ready(function () {
        /* Make Variables table sortable */
        $(".table.variables").addClass("tablesorter").tablesorter({
            sortList: [
                [ 0, 0 ]
            ]
        });

        /* Make Survey Responses table sortable */
        $(".table.survey_responses").addClass("tablesorter").tablesorter({
            headers: {
                // disable sorting of the first and last column
                0: {
                    sorter: false
                },
                6: {
                    sorter: false
                }
            },
            sortList: [
                [ 3, 0 ]
            ]
        });
        $(".table .select-all").change(function () {
            var checkboxes = $(".select-one");
            if ($(this).is(":checked")) {
                checkboxes.prop("checked", "checked");
            } else {
                checkboxes.removeAttr("checked");
            }

        });

        /* Handle export and publish of survey responses. */
        $(".table.survey_responses .select-one, .table.survey_responses .select-all").change(function () {
            var checked = $(".select-one:checked, .select-all:checked").length > 0;
            var buttons = $(".btn-survey");

            if (checked) buttons.removeClass("disabled");
            else buttons.addClass("disabled");
        });

        var setFormAction = function (action) {
            $(".publish-survey-responses-form").get(0).
                setAttribute('action', action);
        };

        var setupOnceComplete = false;
        var setupModal = function (library, year, address) {
            var setupOnce = function () {
                if (setupOnceComplete)
                    return;

                setupOnceComplete = true;
                $('.btn-insert').click(function () {
                    var append = function (token) {
                        var modal = $('#modal-dispatch')

                        var insert = modal.data('insert');
                        if(!insert) insert = $('.dispatch-message');
                        modal.data('insert', '');

                        insert.val(insert.val() + "{" + token + "}");
                        insert.change();
                        insert.focus();
                    };

                    append($(this).text().toLowerCase());
                });

                $('.dispatch-message, .dispatch-title').on('change paste keyup', function () {
                    var render = function (text) {
                        var rendered = text.replace(/\n/g, '<br>');
                        $.each($('.btn-insert'), function () {
                            var token = new RegExp('{' + $(this).text().toLowerCase() + '}', 'g');
                            var value = $(this).data('value');

                            rendered = rendered.replace(token, value);
                        });

                        return rendered;
                    };

                    $('.dispatch-example-heading').html('<b>' + render($('.dispatch-title').val()) + '</b>');
                    $('.dispatch-example-body').html(render($('.dispatch-message').val()));
                }).focusout(function () {
                    $('#modal-dispatch').data('insert', $(this));
                });
            };
            var refresh = function () {
                $('.dispatch-example-footer').html("Detta är ett exempelutskick för " + library + ".");
                $('.btn-library').data('value', library);
                $('.btn-year').data('value', year);
                $('.btn-address').data('value', address);
                $('.btn-password').data('value', 'VRhNVva5AR');

                $('.dispatch-message').change();
                $('#modal-dispatch').modal('show');
            };

            setupOnce();
            refresh();
        };

        $(".btn-publish").click(function () {
            setFormAction(Urls.publish_survey_responses());
        });
        $(".btn-export").click(function () {
            setFormAction(Urls.export_survey_responses());
        });
        $(".btn-dispatch").click(function (e) {
            e.preventDefault();

            var checked = $(".select-one:checked").first();
            var library = checked.data('library');
            var year = checked.data('year');
            var address = checked.data('url-base') + checked.data('address');

            setupModal(library, year, address);
        });

        /* Edit variable */
        $(".edit-variable").click(function (ev) {
            ev.preventDefault(); // prevent navigation
            var url = $(this).data("form"); // get form
            $("#variableModal").load(url, function () { // load the url into the modal
                $(this).modal('show'); // display the modal on url load
            });
            return false; // prevent the click propagation
        });

        /* Create variable */
        $(".create-variable").click(function (ev) {
            ev.preventDefault(); // prevent navigation
            var url = $(this).data("form"); // get form
            $("#variableModal").load(url, function () { // load the url into the modal
                $(this).modal('show'); // display the modal on url load
            });
            return false; // prevent the click propagation
        });

        survey.init();
        login.init();

        console.log('Scripts initialized.')
    });
});