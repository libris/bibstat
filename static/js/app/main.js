define(['article', 'charts', 'dispatches', 'index', 'libraries', 'loading', 'login', 'reports', 'spinner', 'surveys', 'table', 'variables'],
    function(article, charts, dispatches, index, libraries, loading, login, reports, spinner, surveys, table, variables) {
        article.init();
        charts.init();
        dispatches.init();
        index.init();
        libraries.init();
        login.init();
        reports.init();
        spinner.init();
        surveys.init();
        table.init();
        variables.init();
        loading.done();
    });