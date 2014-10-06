define(['jquery'], function($) {
    var cell = {
        disable: function(element) {
            $(element).prop('disabled', true);
        },

        disabled: function(element) {
            return $(element).prop('disabled');
        },

        enable: function(element) {
            $(element).prop('disabled', false);
        },

        enabled: function(element) {
            return !cell.disabled(element);
        },

        onChange: function(element, callback) {
            $(element).on("change paste keyup", callback);
        },

        value: function(element) {
            return $.trim($(element).val());
        },

        number: function(element) {
            return Number(cell.value(element));
        },

        state: function(element, valid) {
            var parent = $(element).parent('.form-group');

            if(valid) parent.removeClass('has-feedback has-error');
            else parent.addClass('has-feedback has-error');
        }
    };

    return cell;
});