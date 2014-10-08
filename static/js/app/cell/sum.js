define(['jquery', 'cell', 'cell.num'], function($, cell, num) {

    var sumOf = function(elements, options) {
        var sum = 0;

        $.each(elements, function(index, element) {
            var number = cell.number(element);
            if(options.integers && number != Math.floor(number))
                number = Number.NaN;

            if(!isNaN(number))
                sum += number
        });

        return sum ? sum : '';
    };

    var validateSetup = function(setup) {
        var reversed = reverseSetup(setup);

        for(var parent in setup) {
            cell.enable(parent);
        }

        for(var child in reversed) {
            if(cell.value(child)) {
                for(var parent in reversed[child])
                    cell.disable(reversed[child][parent]);
            }
        }

        for(var parent in setup) {
            if(cell.disabled(parent))
                continue;

            $.each(setup[parent], function(index, child) {
                var shouldEnable = true;
                $.each(reversed[child], function(index, parent) {
                    if(cell.enabled(parent) && cell.value(parent)) {
                        shouldEnable = false;
                        cell.disable(child);
                    }
                });

                if(shouldEnable)
                    cell.enable(child);
            });
        }
    };

    var setupSum = function(setup, options) {
        var parentCallback = function(parent) {
            cell.onChange(parent, function() {
                num.validate(this, options);
            });
        };

        var childCallback = function(parent, child, children) {
            cell.onChange(child, function() {
                $(parent).val(sumOf(children, options));
                num.validate(this, options);
            });
        };

        for(var parent in setup) {
            parentCallback(parent);
            $.each(setup[parent], function(i, child) {
                childCallback(parent, child, setup[parent]);
            });
        }
    };

    var reverseSetup = function(setup) {
        var reversed = { };
        for(var parent in setup) {
            $.each(setup[parent], function(index, child) {
                if(!reversed.hasOwnProperty(child))
                    reversed[child] = [];

                reversed[child].push(parent);
            });
        }

        return reversed;
    };

    var withDefaults = function(options) {
        var defaults = {
            integers: false
        };

        if(!options)
            return defaults;

        for(var option in defaults) {
            if(!options.hasOwnProperty(option))
                options[option] = defaults[option];
        }

        return options;
    };

    var cells = function(setup) {
        var elements = { };
        for(var parent in setup) {
            elements[parent] = true;
            for(var child in setup[parent])
                elements[setup[parent][child]] = true;
        }

        var array = [];
        for(var element in elements)
            array.push(element);

        return array;
    };

    var initSum = function(setup, options) {
        setupSum(setup, withDefaults(options));
        $.each(cells(setup), function(index, element) {
            cell.onChange(element, function() {
                validateSetup(setup);
            });
        });
    };

    return {
        'init': function() {
            $.each($('input[data-type="sum"]'), function(parent) {
                parent = $(this);
                var setup = { };

                var children = parent.attr('data-sum-of').split(' ');
                var childrenIds = $.map(children, function(child) {
                    return '#' + child.toLowerCase();
                });

                var parentId = '#' + parent.attr('id');
                setup[parentId] = childrenIds;

                var options = {
                    integers: cell.integersOnly(parent)
                };

                initSum(setup, options);
            });
        }
    }
});