define(['jquery', 'cell.sum', 'cell.num', 'bootstrap.validator.sv', 'jquery.tablesorter', 'bootstrap', 'bootstrap.datepicker', 'bootstrap.tokenfield',
    'typeahead', 'underscore'], function($, sum, num) {

    window.ellipsis = function(text, max_chars) {
        max_chars = max_chars || 50;
        if(text && text.length > max_chars) {
            return text.substr(0, max_chars) + " ...";
        }
        return text;
    };

    $(document).ready(function() {

        /* Open login modal on redirect */
        if($(".show-login-modal").length == 1) {
            var sPageUrl = window.location.search.substring(1);
            var urlParams = {};

            if(sPageUrl.length > 0) {
                $.each(sPageUrl.split("&"), function(index, p) {
                    var key_value = p.split("=");
                    urlParams[key_value[0]] = key_value[1];
                });
            }

            if("next" in urlParams) {
                var url = $(".show-login-modal").data("form") + "?next=" + urlParams["next"];
                $("#loginModal").load(url, function() {
                    $(this).modal("show");
                    var nextInput = $(this).find("input[name=next]");
                    // nextInput.attr("value", urlParams["next"]);
                });
            }
        }

        /* Login */
        $(".show-login-modal").click(function(e) {
            e.preventDefault();
            var url = $(this).data("form");
            $("#loginModal").load(url, function() {
                $(this).modal("show");
            });
            return false;
        });

        /* Focus username input field when login modal is shown. */
        $("#loginModal").on("shown.bs.modal", function() {
            $("#username").focus();
        });

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
                5: {
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

        /* Create survey, add questions */
        var active_variables = new Bloodhound({
            datumTokenizer: function(item) {
                return Bloodhound.tokenizers.whitespace(item.value);
            },
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            limit: 20,
            remote: {
                url: '/statistics/variables/surveyable?q=%QUERY',
                filter: function(list) {
                    return $.map(list, function(item) {
                        return { label: item.key, value: item.id };
                    });
                }
            }
        });
        active_variables.initialize();
        $('#add_survey_question').tokenfield({
            typeahead: [null, {
                displayKey: 'label',
                source: active_variables.ttAdapter()
            }],
            limit: 1
            //TODO: Disable typeahead autocomplete and cursor if a token already has been set.
        });

        $(".term-description").popover();

        num.init();
        sum.init();

        //$('#survey-form').bootstrapValidator();
    });
});