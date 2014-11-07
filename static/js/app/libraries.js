define(['jquery'], function($) {
    return {
        'init': function() {
            $('#modal-create').on('show.bs.modal', function() {
                var checked = $('.select-one:checked').length;
                var message = checked > 1
                    ? "<p>Vill du skapa enkäter för de " + checked + " markerade biblioteken?</p>"
                    : "<p>Vill du skapa en enkät för det markerade biblioteket?</p>";

                $('#modal-create .modal-body').html(message);
            });
        }
    }
});