define(['jquery'], function($) {
    var value = function(element) {
        return $.trim($(element).val());
    };
    var sum_cells = function(cells, integers) {
        var sum = 0;
        $.each(cells, function(index, cell) {
            var cell_value = Number(value(cell));
            if(integers && cell_value != Math.floor(cell_value))
                cell_value = Number.NaN;

            if(!isNaN(cell_value))
                sum += cell_value
        });

        return sum ? sum : '';
    };
    var validate_cell = function(cell, integers) {
        var parent = $(cell).parent('.form-group');
        var cell_value = value(cell);

        if(integers && cell_value != Math.floor(cell_value))
            cell_value = Number.NaN;

        if(!isNaN(cell_value)) {
            parent.removeClass('has-feedback has-error');
        } else {
            parent.addClass('has-feedback has-error');
        }

        return cell_value;
    };
    var sum_setup = function(setup, options) {
        var parent_callback = function(parent) {
            $(parent).on("change paste keyup", function() {
                validate_cell(this, options.integers);
            });
        };
        var child_callback = function(parent, child, children) {
            $(child).on("change paste keyup", function() {
                $(parent).val(sum_cells(children, options.integers));
                validate_cell(this, options.integers);
            });
        };

        for(var parent in setup) {
            parent_callback(parent);
            $.each(setup[parent], function(i, child) {
                child_callback(parent, child, setup[parent]);
            });
        }
    };
    var with_defaults = function(options) {
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
    var sum = function(setup, options) {
        var cells = function(setup) {
            var cells = { };
            for(var parent in setup) {
                cells[parent] = true;
                for(var child in setup[parent])
                    cells[setup[parent][child]] = true;
            }

            var cells_array = [];
            for(var cell in cells)
                cells_array.push(cell);

            return cells_array;
        };
        var reverse = function(setup) {
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
        var validate = function(setup) {
            var enable = function(element) { $(element).prop('disabled', false); };
            var disable = function(element) { $(element).prop('disabled', true); };
            var disabled = function(element) { return $(element).prop('disabled'); };
            var enabled = function(element) { return !disabled(element); };

            var reversed = reverse(setup);
            for(var parent in setup) { enable(parent); }
            for(var child in reversed) {
                if(value(child)) {
                    for(var parent in reversed[child])
                        disable(reversed[child][parent]);
                }
            }

            for(var parent in setup) {
                if(disabled(parent))
                    continue;

                $.each(setup[parent], function(index, child) {
                    var should_enable = true;
                    $.each(reversed[child], function(index, parent) {
                        if(enabled(parent) && value(parent)) {
                            should_enable = false;
                            disable(child);
                        }
                    });

                    if(should_enable)
                        enable(child);
                });
            }
        };

        sum_setup(setup, with_defaults(options));
        $.each(cells(setup), function(index, cell) {
            $(cell).on('change paste keyup', function() {
                validate(setup);
            });
        });
    };

    return { 'setup': sum }
});