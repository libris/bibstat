define(['jquery'], function($) {
    var hasAttribute = function(element, name) {
        var attribute = $(element).attr(name);
        return typeof attribute !== typeof undefined
            && attribute !== false;
    };

    var cell = {

        disable: function(element) {
            $(element).prop('disabled', true);
            cell.state(element, 'none');
        },

        disabled: function(element) {
            return $(element).prop('disabled');
        },

        enable: function(element) {
            $(element).prop('disabled', false);
        },

        enabled: function(element) {
            return !cell.disabled(element);
        },

        onChange: function(element, callback) {
            $(element).on("change paste keyup", callback);
        },

        value: function(element) {
            return $.trim($(element).val());
        },

        number: function(element, integers) {
            var number = Number(cell.value(element));
            if(integers && number != Math.floor(number))
                number = Number.NaN;

            return number;
        },

        state: function(element, state) {
            var parent = $(element).closest('.form-group');

            switch(state) {
                case 'success':
                    parent.addClass('has-success');
                    parent.removeClass('has-error');
                    break;
                case 'error':
                    parent.addClass('has-error');
                    parent.removeClass('has-success');
                    break;
                case 'none':
                    parent.removeClass('has-error');
                    parent.removeClass('has-success');
                    break;
            }
        },

        integersOnly: function(element) {
            return hasAttribute(element, 'data-integers-only');
        },

        required: function(element) {
            return hasAttribute(element, 'required');
        }
    };

    return cell;
});