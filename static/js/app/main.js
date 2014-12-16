define(['charts', 'dispatches', 'index', 'libraries', 'login', 'reports', 'spinner', 'survey', 'table', 'variables'],
    function(charts, dispatches, index, libraries, login, reports, spinner, survey, table, variables) {
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
    });