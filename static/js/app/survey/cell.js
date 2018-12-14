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
        onChange: function(element, callback) { $(element).on("change", callback); },
        value: function(element) { return $.trim($(element).val()); },
        number: function(element) {
            return Number(cell
                .value(element)
                .replace(/\s/g, "")
                .replace(",", ".")
            );
        },
        updateThousandsSeparators: function(element) {
            var strval = $(element).val().replace(/\s/g, '');
            if (!/^[0-9\,]+$/.test(strval)) {
                // Do not do anything if value is not numerical
                return;
            }
            var parts = strval.split(',', 2);
            var integer = parts[0];
            var isDecimal = parts.length >= 2;

            // Create integer part with separators
            var numOfSeparators = Math.floor(integer.length / 3);
            var newInt = integer.slice(-3);
            for (var i = 1; i <= numOfSeparators; i++) {
                newInt = integer.slice(-(i+1)*3, -i*3) + ' ' + newInt;
            }
            newInt = newInt.trim();

            if (isDecimal) {
                var decimals = isDecimal ? parts[1] : '0';
                $(element).val(newInt + ',' + decimals);
            } else {
                $(element).val(newInt);
            }
        }
    };

    return cell;
});