define(['jquery', 'scroll'], function($, scroll) {
    return {
       'init': function() {
           $('.btn-checked').click(function(e) {
               e.preventDefault();
               $('.checkbox-survey').prop("checked", "checked");
           });

           $('#form-libraries-submit').click(function() {
              $('#form-libraries').append('<input type="hidden" name="previous_url" value="' + window.location.href + '">')
           });

           scroll.to('.scroll-start');
       }
   }
});