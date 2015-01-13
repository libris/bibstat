define(['jquery', 'scroll'], function ($, scroll) {
    return {
        'init': function () {
            $('.checkbox-survey').change(function () {
                if ($('.checkbox-survey:not(:checked)').length > 0) {
                    $('.btn-checked').text("Markera alla");
                } else {
                    $('.btn-checked').text("Avmarkera alla");
                }
            });

            $('.btn-checked').click(function (e) {
                e.preventDefault();

                if($('.checkbox-survey:not(:checked)').length > 0) {
                    $('.checkbox-survey').prop("checked", "checked");
                } else {
                    $('.checkbox-survey').prop("checked", false);
                }
                $('.checkbox-survey').first().trigger("change");
            });

            $('#form-libraries-submit').click(function (e) {
                var anyChecked = $('.checkbox-survey:checked').length > 0;
                if (anyChecked) {
                    $('#form-libraries').append('<input type="hidden" name="previous_url" value="' + window.location.href + '">')
                } else {
                    e.preventDefault();
                    $('.row-alert').removeClass("hidden")
                }
            });

            $('.report-explanation').click(function (e) {
                e.preventDefault();
            });

            var scrollStart = $('.scroll-start');
            if (scrollStart.length > 0)
                scroll.to(scrollStart);
        }
    }
});