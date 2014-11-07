define(['jquery', 'survey', 'login', 'dispatches', 'libraries', 'jquery.tablesorter', 'bootstrap', 'bootstrap.datepicker', 'bootstrap.tokenfield',
    'typeahead', 'underscore', 'jquery.textrange'], function ($, survey, login, dispatches, libraries) {

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
                [0, 0]
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
                [3, 0]
            ]
        });
    });

    $(".table .select-all").change(function () {
        var checkboxes = $(".select-one");
        if ($(this).is(":checked")) {
            checkboxes.prop("checked", "checked");
        } else {
            checkboxes.removeAttr("checked");
        }
    });

    $(".select-one, .select-all").change(function () {
        var checked = $(".select-one:checked").length > 0;
        var buttons = $(".btn-toggle");

        if (checked) buttons.removeClass("disabled");
        else buttons.addClass("disabled");
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

    $('.show-dispatch').click(function (e) {
        e.preventDefault();

        var element = $(this);
        $('.modal-message .modal-title').html(element.data('title'));
        $('.modal-message .modal-body').html(element.data('message'));
        $('.modal-message').modal('show');
    });

    survey.init();
    login.init();
    dispatches.init();
    libraries.init();

    console.log('Scripts initialized.')
});