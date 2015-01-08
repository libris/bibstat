define(['article', 'charts', 'dispatches', 'index', 'libraries', 'loading', 'login', 'reports', 'spinner', 'survey', 'table', 'variables'],
    function(article, charts, dispatches, index, libraries, loading, login, reports, spinner, survey, table, variables) {
        article.init();
        charts.init();
        dispatches.init();
        index.init();
        libraries.init();
        login.init();
        reports.init();
        spinner.init();
        survey.init();
        table.init();
        variables.init();
        loading.done();
    });