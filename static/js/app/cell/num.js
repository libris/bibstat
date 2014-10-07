define(['jquery', 'cell'], function($, cell) {
    var initNum = function(elements, options) {
        cell.onChange(elements, function() {
            num.validate(this, options);
        });
    };

    var num = {
        'init': function() {
            $.each($('input[data-type="number"]'), function(index, element) {
                var options = {
                    integers: cell.integersOnly(element)
                };

                initNum(element, options);
            });
        },

        validate: function(element, options) {
            var empty = cell.value(element) ? false : true;
            var number = cell.number(element, options.integers);
            number = !isNaN(number) && number >= 0;

            if(empty) {
                cell.state(element, 'none');
            } else {
                if(number) cell.state(element, 'success');
                else cell.state(element, 'error');
            }
        }
    };

    return num;
});