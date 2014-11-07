define(['jquery', 'jquery.textrange'], function ($) {
    var initialized = false;

    var modal = function () { return $('#modal-dispatch'); };
    var messageInput = function () { return $('.dispatch-message'); };
    var message = function () { return messageInput().val(); };
    var title = function () { return $('.dispatch-title').val(); };
    var bold = function (text) { return '<b>' + text + '</b>'; };
    var asToken = function (name) { return "{" + name + "}"; };

    var initOnce = function () {
        if (initialized) return;
        else initialized = true;

        $('.btn-insert').click(function () {
            var insertToken = function (name) {
                var insert = modal().data('insert');
                insert = insert ? insert : messageInput();
                modal().data('insert', false);

                insert.textrange('insert', asToken(name)).change().focus();
            };

            insertToken($(this).text().toLowerCase());
        });

        $('.form-dispatch').bootstrapValidator({
            trigger: 'keyup change paste'
        }).on('success.form.bv', function () {
            var includeInForm = function (id) {
                var input = $('<input>').attr({
                    type: 'hidden',
                    id: id,
                    name: id,
                    value: $('#' + id).val()
                }).appendTo('#form-surveys');
            };

            includeInForm("title");
            includeInForm("message");
            includeInForm("description");
            $('#form-surveys').submit();
            return false;
        });


        // From: https://developer.mozilla.org/en/docs/Web/JavaScript/Guide/Regular_Expressions
        function escapeRegExp(string){
            return string.replace(/([.*+?^${}()|\[\]\/\\])/g, "\\$1");
        }

        $('.dispatch-message, .dispatch-title').on('change paste keyup', function () {
            var render = function (text) {
                var rendered = text.replace(/\n/g, '<br>');
                $.each($('.btn-insert'), function () {
                    var token = new RegExp(escapeRegExp(asToken($(this).text().toLowerCase())), 'g');
                    var value = $(this).data('value');

                    rendered = rendered.replace(token, value);
                });

                return rendered;
            };

            $('.dispatch-example-heading').html(render(bold(title())));
            $('.dispatch-example-body').html(render(message()));
        }).focusout(function () {
            modal().data('insert', $(this));
        });
    };

    var init = function (library, address) {
        $('.dispatch-example-footer').html("Detta är ett exempelutskick för " + library + ".");
        $('.btn-library').data('value', library);
        $('.btn-address-password').data('value', address + "?p=" + 'VRhNVva5AR');
        $('.btn-address').data('value', address);
        $('.btn-password').data('value', 'VRhNVva5AR');

        $('.dispatch-message').change();
        $('#modal-dispatch').modal('show');
    };

    return {
        'init': function (library, address) {
            initOnce();
            init(library, address);
        }
    }
});