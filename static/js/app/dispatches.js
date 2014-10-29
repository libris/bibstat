define(['jquery'], function ($) {
    var form = function () { return $('.form-dispatches'); };
    var submitTo = function(url) { form().get(0).setAttribute('action', Urls[url]()); form().submit(); };
    var init = function () {
        form().find('.btn-delete').click(function () { submitTo('dispatches_delete'); });
        form().find('.btn-send').click(function () { submitTo('dispatches_send'); });
    };

    return {
        'init': init
    }
});