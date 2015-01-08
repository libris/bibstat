define(['jquery'], function() {
    var unsavedChanges = false;

    return {
        'init': function() {
            $('#modal-create-article .btn-confirm').click(function() { $('#article-form').submit(); });
            $('#modal-save-article .btn-confirm').click(function() { $('#article-form').submit(); });
            $('#modal-delete-article .btn-confirm').click(function() { $('#delete-article').submit(); });
            $('#modal-cancel-article .btn-confirm').click(function() { window.location.href = Urls.articles(); });

            $('.btn-validate-article').click(function() {
                var modal = $($(this).attr('data-modal'));
                var emptyInputs = $('.form-article-input').filter(function() {
                   return $(this).val().trim().length == 0;
                });

                if(emptyInputs.length == 0) {
                    $('.row-alert').addClass('hidden');
                    modal.modal('show');
                } else {
                    $('.row-alert').removeClass('hidden');
                    emptyInputs[0].focus();
                }
            });

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

            // Prevent form submission with enter key.
            $("input.form-article-input").keydown(function(event){
                if(event.keyCode == 13) {
                    event.preventDefault();
                    return false;
                }
            });
        }
    }
});