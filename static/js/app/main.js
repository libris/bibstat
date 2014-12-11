define(['charts', 'dispatches', 'index', 'libraries', 'login', 'reports', 'survey', 'table', 'variables'],
    function(charts, dispatches, index, libraries, login, reports, survey, table, variables) {
        charts.init();
        dispatches.init();
        index.init();
        libraries.init();
        login.init();
        reports.init();
        survey.init();
        table.init();
        variables.init();
    });