define(['jquery', 'scroll'], function($, scroll) {
    return {
        'init': function() {
            $('a.scroll').click(function(e) {
                e.preventDefault();
                scroll.to($(this).attr('href'))
            });

            $('a.scroll-section').click(function(e) {
                e.preventDefault();

                $('.section-toggle').addClass("hidden");
                var section = $($(this).attr('href'));

                section.removeClass("hidden");
                scroll.to(section.find(".section-title"));
            });

            $('.btn.btn-articles-expand').click(function(e) {
                e.preventDefault();
                $('.row.row-article').removeClass('hidden');
                $(this).closest('.row').addClass('hidden');
                scroll.to($('.row-article .subsection-title'))
            });
        }
    };
});