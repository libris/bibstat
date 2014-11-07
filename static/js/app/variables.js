define(['jquery'], function($) {
    return {
        'init': function() {
            $(".edit-variable, .create-variable").click(function() {
                var url = $(this).data("form");
                $("#modal-variable").load(url, function() {
                    $(this).modal('show');
                });

                return false;
            });
        }
    }
});