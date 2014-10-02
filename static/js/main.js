(function(requirejs) {
    'use strict';

    requirejs.config({
<<<<<<< HEAD
        baseUrl: '/static/js/',
        shim: {
            'bootstrap': ['jquery'],
            'bootstrap.datepicker': ['bootstrap'],
            'bootstrap.tokenfield': ['bootstrap'],
            'jquery.tablesorter': ['jquery'],
            'typeahead': ['jquery']
        },
        paths: {
            'bootstrap': ['plugins/bootstrap/3.1.1/js/bootstrap'],
            'bootstrap.datepicker': ['plugins/bootstrap-datepicker/1.3.0/bootstrap-datepicker'],
            'bootstrap.tokenfield': ['plugins/bootstrap-tokenfield/0.12.0/bootstrap-tokenfield'],
            'jquery': ['plugins/jquery/1.11.1/jquery'],
            'jquery.tablesorter': ['plugins/jquery/tablesorter/2.17.8/jquery.tablesorter.min'],
            'typeahead': ['plugins/typeaheadjs/0.10.5/typeahead.bundle'],
            'underscore': ['plugins/underscorejs/1.7.0/underscore-min'],

            /* App */
            'cell.sum': 'app/cell/sum'
        },

        deps: ['app/main']
=======
        shim: {
            'jquery.tablesorter': ['jquery'],
            'bootstrap': ['jquery'],
            'bootstrap.datepicker': ['bootstrap'],
            'bootstrap.tokenfield': ['bootstrap'],
            'typeahead': ['jquery']
        },

        paths: {
            'jquery': ['/static/js/plugins/jquery/1.11.1/jquery'],
            'jquery.tablesorter': ['/static/js/plugins/jquery/tablesorter/2.17.8/jquery.tablesorter.min'],
            'bootstrap': ['/static/js/plugins/bootstrap/3.1.1/js/bootstrap'],
            'bootstrap.datepicker': ['/static/js/plugins/bootstrap-datepicker/1.3.0/bootstrap-datepicker'],
            'bootstrap.tokenfield': ['/static/js/plugins/bootstrap-tokenfield/0.12.0/bootstrap-tokenfield'],
            'typeahead': ['/static/js/plugins/typeaheadjs/0.10.5/typeahead.bundle'],
            'underscore': ['/static/js/plugins/underscorejs/1.7.0/underscore-min'],

            // App
            'sum': '/static/js/app/sum'
        },

        deps: ['/static/js/app/main.js']
>>>>>>> Move remaining code in js/libstat.js to js/app/main.js
    });

    requirejs.onError = function(e) {
        console.log(e);
    };
})(requirejs);