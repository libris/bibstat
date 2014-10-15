define(['jquery', 'cell'], function($, cell) {

    var sumOf = function(elements) {
        var sum = 0;

        $.each(elements, function(index, element) {
            var number = cell.number(element);
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

        var anyChildWithValue = false;
        for(var child in reversed) {
            if(cell.enabled(child) && cell.value(child)) {
                anyChildWithValue = true;
                for(var parent in reversed[child])
                    cell.disable(reversed[child][parent]);
            }
        }

        for(var parent in setup) {
            if(cell.disabled(parent))
                continue;

            $.each(setup[parent], function(index, child) {
                var shouldEnable = !(cell.disabled(child) && cell.value(child));
                $.each(reversed[child], function(index, parent) {
                    if(cell.enabled(parent) && cell.value(parent)) {
                        shouldEnable = false;
                        cell.disable(child);
                    }
                });

                if(shouldEnable) {
                    cell.enable(child);
                    $(child).val('');
                }
            });
        }

        if(anyChildWithValue) {
            for(child in reversed) {
                var dropdown = $(child).next(".input-group-btn").children(".btn-dropdown");
                dropdown.prop('disabled', true);

            }
        }
    };

    var setupSum = function(setup) {
        var childCallback = function(parent, child, children) {
            cell.onChange(child, function() {
                $(parent).val(sumOf(children));
                $(parent).change();
            });
        };

        for(var parent in setup) {
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

    var initSum = function(setup) {
        setupSum(setup);
        $.each(cells(setup), function(index, element) {
            cell.onChange(element, function() {
                validateSetup(setup);
            });
        });
    };

    return {
        'init': function() {
            $.each($('input[data-sum-of]'), function() {
                var parent = $(this);
                var setup = { };

                var children = parent.attr('data-sum-of').split(' ');
                var childrenIds = $.map(children, function(child) {
                    return '#' + child
                });

                var parentId = '#' + parent.attr('id');
                setup[parentId] = childrenIds;

                initSum(setup);
            });
        }
    }
});