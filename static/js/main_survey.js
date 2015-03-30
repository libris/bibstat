/*global require,requirejs,console*/
(function(requirejs) {
    'use strict';

    requirejs.config({
        baseUrl: '/static/js/',
        urlArgs: 'bust=' + (new Date()).getTime(),
        shim: {
            'bootstrap': ['jquery'],
            'formValidation': ['bootstrap'],
            'formValidation.bootstrap': ['formValidation'],
            'formValidation.sv': ['formValidation'],
            'jquery.textrange': ['jquery'],
            'jquery.scrollTo': ['jquery'],
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
            'formValidation': 'plugins/formValidation/js/formValidation',
            'formValidation.bootstrap': 'plugins/formValidation/js/framework/bootstrap',
            'formValidation.sv': 'plugins/formValidation/js/language/sv_SE',
            'jquery': 'plugins/jquery/1.11.1/jquery',
            'jquery.textrange': 'plugins/jquery/textrange/1.3.0/jquery-textrange',
            'jquery.placeholder': 'plugins/jquery/placeholder/jquery.placeholder',
            'jquery.scrollTo': 'plugins/jquery/scrollTo-2.1.0/jquery.scrollTo',
            'bootbox': 'plugins/bootbox'
        }
    });

    requirejs.onError = function(e) {
        console.log(e);
    };

    require(['app/main_survey']);

})(requirejs);