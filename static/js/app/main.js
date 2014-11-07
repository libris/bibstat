define(['dispatches', 'libraries', 'login', 'survey', 'table', 'variables'],
    function(dispatches, libraries, login, survey, table, variables) {
        dispatches.init();
        libraries.init();
        login.init();
        survey.init();
        table.init();
        variables.init();
    });