define(['jquery', 'survey', 'login', 'jquery.tablesorter', 'bootstrap', 'bootstrap.datepicker', 'bootstrap.tokenfield',
    'typeahead', 'underscore'], function($, survey, login) {

    window.ellipsis = function(text, max_chars) {
        max_chars = max_chars || 50;
        if(text && text.length > max_chars) {
            return text.substr(0, max_chars) + " ...";
        }
        return text;
    };

    $(document).ready(function() {
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
        $(".table.survey_responses .select-all").change(function() {
            var checkboxes = $(".select-one");
            if($(this).is(":checked")) {
                checkboxes.prop("checked", "checked");
            } else {
                checkboxes.removeAttr("checked");
            }

        });

        /* Handle export and publish of survey responses. */
        $(".table.survey_responses .select-one, .table.survey_responses .select-all").change(function() {
            var checked = $(".select-one:checked, .select-all:checked").length > 0;
            var buttons = $(".btn-publish-survey-responses, .btn-export-survey-responses");

            if(checked) buttons.removeClass("disabled");
            else buttons.addClass("disabled");
        });

        $(".btn-publish-survey-responses").click(function() {
            var action = Urls.publish_survey_responses();
            $(".publish-survey-responses-form").get(0).
                setAttribute('action', action);
        });

        $(".btn-export-survey-responses").click(function() {
            var action = Urls.export_survey_responses();
            $(".publish-survey-responses-form").get(0).
                setAttribute('action', action);
        });

        /* Edit variable */
        $(".edit-variable").click(function(ev) {
            ev.preventDefault(); // prevent navigation
            var url = $(this).data("form"); // get form
            $("#variableModal").load(url, function() { // load the url into the modal
                $(this).modal('show'); // display the modal on url load
            });
            return false; // prevent the click propagation
        });

        /* Create variable */
        $(".create-variable").click(function(ev) {
            ev.preventDefault(); // prevent navigation
            var url = $(this).data("form"); // get form
            $("#variableModal").load(url, function() { // load the url into the modal
                $(this).modal('show'); // display the modal on url load
            });
            return false; // prevent the click propagation
        });

        survey.init();
        login.init();

        console.log('Scripts initialized.')
    });
});