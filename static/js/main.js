(function(requirejs) {
    'use strict';

    requirejs.config({
        baseUrl: '/static/js/',
        shim: {
            'bootstrap': ['jquery'],
            'bootstrap.datepicker': ['bootstrap'],
            'bootstrap.tokenfield': ['bootstrap'],
            'bootstrap.validator': ['bootstrap'],
            'bootstrap.validator.sv': ['bootstrap.validator'],
            'jquery.tablesorter': ['jquery'],
            'typeahead': ['jquery']
        },
        paths: {
            'bootstrap': ['plugins/bootstrap/3.1.1/js/bootstrap'],
            'bootstrap.datepicker': ['plugins/bootstrap-datepicker/1.3.0/bootstrap-datepicker'],
            'bootstrap.tokenfield': ['plugins/bootstrap-tokenfield/0.12.0/bootstrap-tokenfield'],
            'bootstrap.validator': ['plugins/bootstrap-validator/0.5.2/js/bootstrapValidator'],
            'bootstrap.validator.sv': ['plugins/bootstrap-validator/0.5.2/js/language/sv_SE'],
            'jquery': ['plugins/jquery/1.11.1/jquery'],
            'jquery.tablesorter': ['plugins/jquery/tablesorter/2.17.8/jquery.tablesorter.min'],
            'typeahead': ['plugins/typeaheadjs/0.10.5/typeahead.bundle'],
            'underscore': ['plugins/underscorejs/1.7.0/underscore-min'],

            /* App */
            'cell': 'app/cell/cell',
            'cell.num': 'app/cell/num',
            'cell.sum': 'app/cell/sum'
        },

        deps: ['app/main']
    });

    requirejs.onError = function(e) {
        console.log(e);
    };
})(requirejs);