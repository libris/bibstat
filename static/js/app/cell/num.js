define(['jquery', 'cell'], function($, cell) {
    var num = {
        'init': function(elements, options) {
            cell.onChange(elements, function() {
                num.validate(this, options);
            });
        },

        validate: function(element, options) {
            var number = cell.number(element);
            if(options.integers && number != Math.floor(number))
                number = Number.NaN;

            var valid = !isNaN(number);
            cell.state(element, valid);
        }
    };

    return num;
});