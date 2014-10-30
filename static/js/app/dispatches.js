define(['jquery'], function ($) {
    var form = function () { return $('.form-dispatches'); };
    var panel = function() { return $('.panel-dispatches'); };
    var submitTo = function(url) { form().get(0).setAttribute('action', Urls[url]()); form().submit(); };
    var init = function () {
        panel().find('.btn-delete').click(function () { submitTo('dispatches_delete'); });
        panel().find('.btn-send').click(function () { submitTo('dispatches_send'); });
    };

    return {
        'init': init
    }
});