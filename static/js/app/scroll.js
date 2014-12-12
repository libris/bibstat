define(['jquery'], function($) {
   return {
       'to': function(selector, callback) {
           $("html, body").animate({scrollTop: $(selector).offset().top - 10}, 400, "swing", callback);
       }
    }
});