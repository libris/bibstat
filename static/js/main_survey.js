/*global require,requirejs,console*/
(function(requirejs) {
    'use strict';

    requirejs.config({
        baseUrl: '/static/js/',
        urlArgs: 'bust=' + (new Date()).getTime(),
        shim: {
            'bootstrap': ['jquery'],
            'bootstrap.validator': ['bootstrap'],
            'bootstrap.validator.sv': ['bootstrap.validator'],
            'jquery.textrange': ['jquery'],
            'jquery.placeholder': ['jquery']
        },
        paths: {

            /* App */
            'dispatches': 'app/dispatches',
            'loading': 'app/loading',
            'login': 'app/login',
            'scroll': 'app/scroll',
            'spinner': 'app/spinner',
            'survey': 'app/survey',
            'survey.cell': 'app/survey/cell',
            'survey.sum': 'app/survey/sum',
            'surveys.dispatch': 'app/surveys/dispatch',

            /* Plugins */
            'bootstrap': 'plugins/bootstrap/3.2.0/js/bootstrap',
            'bootstrap.validator': 'plugins/bootstrap-validator/0.5.3/js/bootstrapValidator',
            'bootstrap.validator.sv': 'plugins/bootstrap-validator/0.5.3/js/language/sv_SE',
            'jquery': 'plugins/jquery/1.11.1/jquery',
            'jquery.textrange': 'plugins/jquery/textrange/1.3.0/jquery-textrange',
            'jquery.placeholder': 'plugins/jquery/placeholder/jquery.placeholder',
            'bootbox': 'plugins/bootbox'
        }
    });

    requirejs.onError = function(e) {
        console.log(e);
    };

    require(['app/main_survey']);

})(requirejs);