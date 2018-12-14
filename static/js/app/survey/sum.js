define(['jquery', 'bootbox', 'survey.cell'], function($, bootbox, cell) {
    var sumOf = function (elements) {
        var sum = null;

        $.each(elements, function (index, element) {
            var number = cell.number(element);
            var strval = cell.value(element);
            if (strval == '') {
                return;
            }
            if (isNaN(number)) {
                return;
            }
            if(sum == null){
                sum = 0;
            }
            sum += number;
        });

        if (sum == null) {
            return null;
        }

        // Max 3 decimals
        if(sum % 1 != 0) sum = sum.toFixed(3);
        return sum;
    };

    var setupSum = function(setup) { //setup contains key = sumfield-id and array of all subfields to be included in sum

        //Every subfield triggers update of sum onchange
        var childCallback = function(parent, child, children) {
            cell.onChange(child, function() {
                if(!$(parent).prop("disabled")) {
                    var sum = sumOf(children);
                    if (sum == null){
                        $(parent).val('-');
                    } else {
                        $(parent).val(String(sum).replace(".", ","));
                    }
                    cell.updateThousandsSeparators(parent);
                    $(parent).change();
                }
            });
        };
        for(var parent in setup) {
            $.each(setup[parent], function (i, child) {
                childCallback(parent, child, setup[parent]);
                $(child).attr('data-is-child', true);
                $(child).attr('parent', ($(child).attr('parent') ? $(child).attr('parent') : '') + parent + ',');
            });
        };

        $(parent).blur(function () {
            var sumFieldValue = cell.number(this);
            if (isNaN(sumFieldValue)) {
                return;
            }

            // Array of subfield elements
            childels = $.map(setup[parent], function (child) {
                return $(child);
            });

            // Check if all subfields contain '-' or other NaN
            var allChildrenIrrelevant = true;
            $.each(childels, function (index, childElement) {
                if (!isNaN(cell.number(childElement))) {
                    // Child contains number
                    allChildrenIrrelevant = false;
                }
            });
            if (allChildrenIrrelevant) {
                return;
            }

            // Compare calculated sum of subfields with value in sum field
            calculatedSum = sumOf(childels);
            if (sumFieldValue == calculatedSum) {
                // Everything is OK
                return;
            }

            // Warn user that calculated sum of subfields does not match sum
            // field value
            bootbox.confirm('Du har angivit värden i delfälten som inte kan summeras till värdet i totalfältet. Om du istället vill ange värde i summeringsfältet kommer delfälten att raderas. Klicka OK för att radera värden i delfälten eller Avbryt för att korrigera summeringfältet.', function (result) {
                if (result) {
                    // User clicks OK
                    // Clear subfields and put focus on sum field
                    $.each(childels, function (index, child) {
                        child.val("");
                    });
                    $(parent).focus()
                } else {
                    // User clicks Cancel
                    // Trigger change on one of the subfields to change
                    // the sum
                    childels[0].change()
                }
            });
        });
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