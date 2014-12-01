define(['jquery'], function ($) {
    var form = function () { return $('.form-dispatches'); };
    var submitTo = function(url) { form().get(0).setAttribute('action', Urls[url]()); form().submit(); };

    return {
        'init': function () {
            $('#modal-delete').find('.btn-confirm').click(function () { submitTo('dispatches_delete'); });
            $('#modal-send').find('.btn-confirm').click(function () { submitTo('dispatches_send'); });

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