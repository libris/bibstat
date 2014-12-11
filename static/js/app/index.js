define(['jquery'], function($) {
    var scrollTo = function(selector, callback) {
        $("html, body").animate({scrollTop: $(selector).offset().top - 10}, 400, "swing", callback);
    };

    return {
        'init': function() {
            $('a.scroll').click(function(e) {
                e.preventDefault();
                scrollTo($(this).attr('href'))
            });

            $('a.scroll-section').click(function(e) {
                e.preventDefault();

                $('.section-toggle').addClass("hidden");
                var section = $($(this).attr('href'));

                section.removeClass("hidden");
                scrollTo(section.find(".section-title"));
            });

            $('.btn.btn-articles-expand').click(function(e) {
                e.preventDefault();
                $('.row.row-article').removeClass('hidden');
                $(this).closest('.row').addClass('hidden');
                scrollTo($('.row-article .subsection-title'))
            });
        }
    };
});