
module.exports = {
  
  
  'Open survey' : function (browser) {
    var emailField = 'Epost01',
        teleField = 'Tele01',
        integerField = 'Bokbuss01',
        outsideField = '.navbar-text'; // Used to blur input fields
    
    browser
      .url('http://localhost:8000/surveys/54b7ca100b52ff12b56c8279?p=umyzlsJmi2')
      .waitForElementVisible('body', 1000)
      
      .verify.containsText('.navbar-text', 'Välkommen')
      
      .click("#" + emailField)
      .setValue("#" + emailField, '')
      .click(outsideField)
      .verify.visible('small[data-bv-for='+emailField+'][data-bv-validator=notEmpty]', 'VALIDATION - notEmpty: Should show msg on fail')
      
      .click("#" + emailField)
      .setValue("#" + emailField, 'Test')
      .click(outsideField)
      .verify.hidden('small[data-bv-for='+emailField+'][data-bv-validator=notEmpty]', 'VALIDATION - notEmpty: Should hide msg on pass')
      .verify.visible('small[data-bv-for='+emailField+'][data-bv-validator=regexp]', 'VALIDATION - regexp (email): Should show msg on fail')
      // .verify.visible('small[data-bv-for=Epost01][data-bv-validator=emailAddress]', 'emailAddress validation msg should show on fail')
      .clearValue("#" + emailField)
      
      .click("#" + emailField)
      .setValue("#" + emailField, 'test@test.test')
      .click(outsideField)
      .verify.hidden('small[data-bv-for='+emailField+'][data-bv-validator=regexp]', 'VALIDATION - regexp (email): Should hide msg on pass')
      // .verify.hidden('small[data-bv-for=Epost01][data-bv-validator=emailAddress]', 'emailAddress validation msg should hide on pass')
      
      .click("#" + teleField)
      .setValue("#" + teleField, '3')
      .click(outsideField)
      .verify.visible('small[data-bv-for='+teleField+'][data-bv-validator=regexp]', 'VALIDATION - regexp (phone): Should show msg on fail')
      .clearValue("#" + teleField)
      .click("#" + teleField)
      .setValue("#" + teleField, '010-709 30 00')
      .click(outsideField)
      .verify.hidden('small[data-bv-for='+teleField+'][data-bv-validator=regexp]', 'VALIDATION - regexp (phone): Should hide msg on pass')
      
      .click("#" + integerField)
      .setValue("#" + integerField, '99999999999999')
      .click(outsideField)
      .verify.visible('small[data-bv-for='+integerField+'][data-bv-validator=lessThan]', 'VALIDATION - lessThan: Should show msg on fail')
      .clearValue("#" + integerField)
      .click("#" + integerField)
      .setValue("#" + integerField, '3')
      .click(outsideField)
      .verify.hidden('small[data-bv-for='+integerField+'][data-bv-validator=lessThan]', 'VALIDATION - lessThan: Should hide msg on pass')
      
      .end();
  },
};
