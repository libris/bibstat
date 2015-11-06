define(['jquery', 'bootbox', 'survey.cell'], function($, bootbox, cell) {
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

    var setupSum = function(setup) { //setup contains key = sumfield-id and array of all subfields to be included in sum

        //Every subfield triggers update of sum onchange
        var childCallback = function(parent, child, children) {
            cell.onChange(child, function() {
                if(!$(parent).prop("disabled")) {
                    $(parent).val(String(sumOf(children)).replace(".", ",").replace("-", ""));
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

            //Warn if sum of subfields does not match sumfield value
            $(parent).blur(function () {

                //Array of subfield elements
                childels = $.map(setup[parent], function (child) {
                    return $(child);
                });

                //Calculate sum of subfields
                childsum = String(sumOf(childels)).replace(".", ",").replace("-", "");

                //Compare subfield sum with value in sumfield
                if (childsum != "" && String(this.value).replace(".", ",") != childsum) {

                    // Varna användaren om summan skiljer sig från totalfältet
                    bootbox.confirm('Du har angivit värden i delfälten som inte kan summeras till värdet i totalfältet. Om du istället vill ange värde i summeringsfältet kommer delfälten att raderas. Klicka OK för att radera värden i delfälten eller Avbryt för att korrigera summeringfältet.', function (result) {

                        if (result) {

                            // Blank subfields and put focus on sumfield
                            $.each(childels, function(index, child) {
                                child.val("");
                            });

                            $(parent).focus()

                        } else {

                            // Trigger change on one of the subfields to change the sum
                            childels[0].change()
                        }
                    });
                } else {
                    //Sum is correct, ignore
                }
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