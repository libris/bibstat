
module.exports = {
  
  
  'Open survey' : function (browser) {
    var emailField = '#Epost01',
        teleField = '#Tele01',
        outsideField = '.navbar-text'; // Used to blur input fields
    
    browser
      .url('http://localhost:8000/surveys/54b7ca100b52ff12b56c8279?p=umyzlsJmi2')
      .waitForElementVisible('body', 1000)
      
      .assert.containsText('.navbar-text', 'Välkommen')
      
      .click(emailField)
      .setValue(emailField, '')
      .click(outsideField)
      .assert.visible('small[data-bv-for=Epost01][data-bv-validator=notEmpty]', 'Empty valid msg should show on fail')
      
      .click(emailField)
      .setValue(emailField, 'Test')
      .click(outsideField)
      .assert.hidden('small[data-bv-for=Epost01][data-bv-validator=notEmpty]', 'Empty valid msg should hide on pass')
      .assert.visible('small[data-bv-for=Epost01][data-bv-validator=regexp]', 'Email regexp validation msg should show on fail')
      // .assert.visible('small[data-bv-for=Epost01][data-bv-validator=emailAddress]', 'emailAddress validation msg should show on fail')
      
      .click(emailField)
      .setValue(emailField, 'test@test.test')
      .click(outsideField)
      .assert.hidden('small[data-bv-for=Epost01][data-bv-validator=regexp]', 'Email regexp validation msg should hide on pass')
      // .assert.hidden('small[data-bv-for=Epost01][data-bv-validator=emailAddress]', 'emailAddress validation msg should hide on pass')
      
      .click(teleField)
      .setValue(teleField, '3')
      .click(outsideField)
      .assert.visible('small[data-bv-for=Tele01][data-bv-validator=regexp]', 'Phone regexp validation msg should show on fail')
      .click(teleField)
      .setValue(teleField, '010-709 30 00')
      .click(outsideField)
      .assert.hidden('small[data-bv-for=Tele01][data-bv-validator=regexp]', 'Phone regexp validation msg should hide on pass')
      
      .end();
  },
};
