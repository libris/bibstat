define(['loading', 'login', 'spinner', 'survey'],
    function(loading, login, spinner, survey) {
        login.init();
        spinner.init();
        survey.init();
        loading.done();
    });