define(['jquery'], function($) {
   return {
       'init': function() {
           $('.spinner').click(function() {
               var element = $(this);

               var text = element.attr('data-spinner-text');
               var disabled = $(element.attr('data-spinner-disable'));

               disabled.addClass('disabled');
               element.html('<i class="fa fa-spinner fa-spin"></i> ' + text)
                   .addClass("disabled");
           });
       }
   }
});