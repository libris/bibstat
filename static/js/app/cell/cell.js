define(['jquery'], function($) {
    var cell = {

        disable: function(element) {
            $(element).prop('disabled', true);
            $(element).next(".input-group-btn").children(".btn-dropdown").prop("disabled", true);
            $('#survey-form').bootstrapValidator('enableFieldValidators', $(element).attr('name'), false);
        },

        disabled: function(element) {
            return $(element).prop('disabled');
        },

        enable: function(element) {
            $(element).prop('disabled', false);
            $(element).next(".input-group-btn").children(".btn-dropdown").prop("disabled", false);
            $('#survey-form').bootstrapValidator('enableFieldValidators', $(element).attr('name'), true);
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

        number: function(element, integers) {
            var number = Number(cell.value(element));
            if(integers && number != Math.floor(number))
                number = Number.NaN;

            return number;
        }
    };

    return cell;
});