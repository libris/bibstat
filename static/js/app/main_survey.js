define(['dispatches', 'loading', 'login', 'spinner', 'survey'],
    function(dispatches, loading, login, spinner, survey) {
        dispatches.init();
        login.init();
        spinner.init();
        survey.init();
        loading.done();
    });