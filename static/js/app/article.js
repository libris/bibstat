define(['jquery'], function() {
    var unsavedChanges = false;

    return {
        'init': function() {
            $('#modal-create-article .btn-confirm').click(function() { $('#article-form').submit(); });
            $('#modal-save-article .btn-confirm').click(function() { $('#article-form').submit(); });
            $('#modal-delete-article .btn-confirm').click(function() { $('#delete-article').submit(); });
            $('#modal-cancel-article .btn-confirm').click(function() { window.location.href = Urls.articles(); });

            $(".form-article-input").on('change', function() {
               unsavedChanges = true;
            });

            $('.btn-cancel-article').click(function() {
                if(unsavedChanges) {
                    $('#modal-cancel-article').modal('show');
                } else {
                    window.location.href = Urls.articles()
                }
            });
        }
    }
});