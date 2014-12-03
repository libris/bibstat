define(['dispatches', 'libraries', 'login', 'reports', 'survey', 'table', 'variables'],
    function(dispatches, libraries, login, reports, survey, table, variables) {
        dispatches.init();
        libraries.init();
        login.init();
        reports.init();
        survey.init();
        table.init();
        variables.init();
    });