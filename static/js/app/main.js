define(['charts', 'dispatches', 'libraries', 'login', 'reports', 'survey', 'table', 'variables'],
    function(charts, dispatches, libraries, login, reports, survey, table, variables) {
        charts.init();
        dispatches.init();
        libraries.init();
        login.init();
        reports.init();
        survey.init();
        table.init();
        variables.init();
    });