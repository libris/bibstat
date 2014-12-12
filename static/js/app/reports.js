define(['jquery', 'scroll'], function($, scroll) {
    return {
       'init': function() {
           $('.btn-checked').click(function(e) {
               e.preventDefault();
               $('.checkbox-survey').prop("checked", "checked");
           });

           $('#form-libraries-submit').click(function(e) {
               var anyChecked = $('.checkbox-survey:checked').length > 0;
               if(anyChecked) {
                   $('#form-libraries').append('<input type="hidden" name="previous_url" value="' + window.location.href + '">')
               } else {
                   e.preventDefault();
                   $('.row-alert').removeClass("hidden")
               }
           });

           var scrollStart = $('.scroll-start');
           if(scrollStart.length > 0)
               scroll.to(scrollStart);
       }
   }
});