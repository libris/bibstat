define(['jquery'], function ($) {
    var form = function () { return $('.form-dispatches'); };
    var panel = function() { return $('.panel-dispatches'); };
    var submitTo = function(url) { form().get(0).setAttribute('action', Urls[url]()); form().submit(); };

    return {
        'init': function () {
            panel().find('.btn-delete').click(function () { submitTo('dispatches_delete'); });
            panel().find('.btn-send').click(function () { submitTo('dispatches_send'); });

            $('.show-dispatch').click(function (e) {
                e.preventDefault();

                var element = $(this);
                $('.modal-message .modal-title').html(element.data('title'));
                $('.modal-message .modal-body').html(element.data('message'));
                $('.modal-message').modal('show');
            });
        }
    }
});