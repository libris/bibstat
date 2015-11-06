define(['jquery', 'survey.cell'], function($, cell) {
    var sumOf = function (elements) {
        var sum = null;

        $.each(elements, function (index, element) {
            var number = cell.number(element);
            if (!isNaN(number) && cell.value(element) != "") {
                if(sum == null){
                    sum = 0;
                }
                sum += number
            }
        });
        // Max 3 decimals
        if(sum % 1 != 0) sum = sum.toFixed(3);

        return sum != null ? sum : '';
    };

    var setupSum = function(setup) {
        var childCallback = function(parent, child, children) {
            cell.onChange(child, function() {
                if(!$(parent).prop("disabled")) {
                    $(parent).val(String(sumOf(children)).replace(".", ",").replace("-", ""));
                    $(parent).change();
                }
            });
        };
        for(var parent in setup) {
            $.each(setup[parent], function(i, child) {
                childCallback(parent, child, setup[parent]);
                $(child).attr('data-is-child', true);
                $(child).attr('parent', ($(child).attr('parent') ? $(child).attr('parent') : '') + parent + ',');
            });
        }
    };

    var initSum = function(setup) {
        setupSum(setup);
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