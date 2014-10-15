define(['jquery'], function($) {
    var cell = {

        disable: function(element) {
            $(element).next(".input-group-btn").children(".btn-dropdown").prop("disabled", true);
            $(element).prop('disabled', true);
        },

        disabled: function(element) {
            return $(element).prop('disabled');
        },

        enable: function(element) {
            $(element).next(".input-group-btn").children(".btn-dropdown").prop("disabled", false);
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
        }
    };

    return cell;
});