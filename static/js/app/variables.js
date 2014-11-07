define(['jquery'], function($) {
    return {
        'init': function() {
            $(".edit-variable, .create-variable").click(function(e) {
                var url = $(this).data("form");
                $("#variableModal").load(url, function() {
                    $(this).modal('show');
                });

                return false;
            });
        }
    }
});