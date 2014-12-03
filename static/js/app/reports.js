define(['jquery'], function($) {
   return {
       'init': function() {
           $('.btn-checked').click(function(e) {
               e.preventDefault();
               $('.checkbox-survey').prop("checked", "checked");
           });
       }
   }
});