define(['jquery'], function($) {
    var cell = {
        disabled: function(element) { return $(element).prop('disabled'); },
        disable: function(element) {
            var element = $(element);

            if(element.length > 0) {
                $('#survey-form').data('bootstrapValidator')
                    .resetField(element)
                    .enableFieldValidators(element.attr('name'), false);

                    element.prop('disabled', true);
            }
        },
        enabled: function(element) { return !cell.disabled(element); },
        enable: function(element) {
            var element = $(element);

            if(element.length > 0) {
                element.next(".input-group-btn").children(".btn-dropdown").prop("disabled", false);
                element.prop('disabled', false);

                $('#survey-form').data('bootstrapValidator')
                    .enableFieldValidators(element.attr('name'), true);
            }
        },
        onChange: function(element, callback) { $(element).on("change paste keyup", callback); },
        value: function(element) { return $.trim($(element).val()); },
        number: function(element) { return Number(cell.value(element).replace(",", ".")); }
    };

    return cell;
});