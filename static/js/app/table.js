define(['jquery', 'jquery.tablesorter'], function($) {
    return {
        'init': function() {
            window.ellipsis = function (text, max_chars) {
                max_chars = max_chars || 50;
                if (text && text.length > max_chars) {
                    return text.substr(0, max_chars) + " ...";
                }
                return text;
            };

            $(document).ready(function () {
                $(".table.variables").addClass("tablesorter").tablesorter({ sortList: [[0, 0]] });
                $(".table.survey_responses").addClass("tablesorter").tablesorter({
                    headers: {
                        0: { sorter: false },
                        7: { sorter: false}
                    },
                    sortList: [[3, 0]]
                });
                $(".table.libraries").addClass("tablesorter").tablesorter({
                    headers: {
                        0: { sorter: false }
                    }
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
                var checked = $(".select-one:checked").length;
                var total = $(".select-one").length;
                var buttons = $(".btn-toggle");

                if (checked > 0) buttons.removeClass("disabled");
                else buttons.addClass("disabled");

                if(checked == total) $(".select-all").prop("checked", "checked");
                else $(".select-all").removeAttr("checked");

                if(checked == 0) {
                    $('.selected-single').addClass('hidden');
                    $('.selected-multiple').addClass('hidden');
                    $('.selected-default').removeClass('hidden');
                } else if(checked == 1) {
                    $('.selected-default').addClass('hidden');
                    $('.selected-multiple').addClass('hidden');
                    $('.selected-single').removeClass('hidden');
                } else if(checked > 1) {
                    $('.selected-default').addClass('hidden');
                    $('.selected-single').addClass('hidden');
                    $('.selected-multiple').removeClass('hidden');
                }

                $('.selected-count').text(checked)
            });
        }
    }
});