({
	baseUrl: '../static/js/',
	name: 'main',
	mainConfigFile: '../static/js/main.js',
	include: ['plugins/requirejs/require.js'],
	out: "../static/js/main.min.js"
},
{
    baseUrl: '../static/js/',
    name: 'main_survey',
    mainConfigFile: '../static/js/main_survey.js',
    include: ['plugins/requirejs/require.js'],
    out: "../static/js/main_survey.min.js"
})