define(['jquery', 'scroll'], function($, scroll) {
    return {
       'init': function() {
           $('.btn-checked').click(function(e) {
               e.preventDefault();
               $('.checkbox-survey').prop("checked", "checked");
           });

           scroll.to('.scroll-start');
       }
   }
});