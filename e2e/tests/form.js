
module.exports = {
  
  
  'Open survey' : function (browser) {
    var emailField = 'Epost01',
        teleField = 'Tele01',
        integerField = 'Bokbuss01',
        outsideField = '.navbar-text', // Used to blur input fields
        sumOfFields = [
          'Arsverke01',
          'Arsverke02',
          'Arsverke03',
          'Arsverke04',
          'Arsverke99',
          'Arsverke05'
        ];
    
    browser
      .url('http://localhost:8000/surveys/54b7ca100b52ff12b56c8279?p=umyzlsJmi2')
      .waitForElementVisible('body', 1000)
      
      .verify.containsText('.navbar-text', 'Välkommen')
      
      .click("#" + emailField)
      .setValue("#" + emailField, '')
      .click(outsideField)
      .verify.visible('#fg-'+emailField +' small[data-bv-validator=notEmpty]', 'ERRORMESSAGE \t notEmpty \t Should show msg on fail')
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=notEmpty]', 'data-bv-result', 'INVALID', 'VALIDATION \t notEmpty \t INVALID for ""')
      
      .click("#" + emailField)
      .setValue("#" + emailField, 'Test')
      .click(outsideField)
      .verify.hidden('#fg-'+emailField+' small[data-bv-validator=notEmpty]', 'ERRORMESSAGE \t notEmpty \t Should hide msg on pass')
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=notEmpty]', 'data-bv-result', 'VALID', 'VALIDATION \t notEmpty \t VALID for "Test"')
      .verify.visible('#fg-'+emailField+' small[data-bv-validator=regexp]', 'ERRORMESSAGE \t regexp (email) \t Should show msg on fail')
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=regexp]', 'data-bv-result', 'INVALID', 'VALIDATION \t regexp \t INVALID for "Test"')
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=emailAddress]', 'data-bv-result', 'INVALID', 'VALIDATION \t emailAddress \t INVALID for "Test"')
      .clearValue("#" + emailField)
      
      .click("#" + emailField)
      .setValue("#" + emailField, 'test@test.test')
      .click(outsideField)
      .verify.hidden('#fg-'+emailField+' small[data-bv-validator=regexp]', 'ERRORMESSAGE \t regexp (email) \t Should hide msg on pass')
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=regexp]', 'data-bv-result', 'VALID', 'VALIDATION \t regexp \t VALID for "test@test.test"')
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=emailAddress]', 'data-bv-result', 'VALID', 'VALIDATION \t emailAddress \t VALID for "test@test.test"')
      
      .click("#" + teleField)
      .setValue("#" + teleField, '3')
      .click(outsideField)
      .verify.visible('#fg-'+teleField+' small[data-bv-validator=regexp]', 'VALIDATION \t regexp (phone) \t Should show msg on fail')
      .clearValue("#" + teleField)
      .click("#" + teleField)
      .setValue("#" + teleField, '010-709 30 00')
      .click(outsideField)
      .verify.hidden('#fg-'+teleField+' small[data-bv-validator=regexp]', 'VALIDATION \t regexp (phone) \t Should hide msg on pass')
      
      .click("#" + integerField)
      .setValue("#" + integerField, '99999999999999')
      .click(outsideField)
      .verify.visible('#fg-'+integerField+' small[data-bv-validator=lessThan]', 'VALIDATION \t lessThan \t Should show msg on fail')
      .clearValue("#" + integerField)
      .click("#" + integerField)
      .setValue("#" + integerField, '3')
      .click(outsideField)
      .verify.hidden('#fg-'+integerField+' small[data-bv-validator=lessThan]', 'VALIDATION \t lessThan \t Should hide msg on pass')
      
      // Sum-of
      .click("#" + sumOfFields[0])
      .setValue("#" + sumOfFields[0], 5)
      .setValue("#" + sumOfFields[1], 2)
      .setValue("#" + sumOfFields[2], 7)
      .setValue("#" + sumOfFields[3], 8)
      .click(outsideField)
      .verify.value("#" + sumOfFields[4], "22", "SUM OF: Total value should equal the total of subfields")
      
      // Unknown value
      .setValue("#" + sumOfFields[0], 5) // Used to scroll the item properly into view.
      .click("#fg-"+ sumOfFields[0] +" .btn-dropdown")
      .click("#fg-"+ sumOfFields[0] +" ul .menu-disable-input")
      .waitForElementVisible('.bootbox-confirm .modal-dialog', 2000)
      .verify.elementPresent(".bootbox-confirm .modal-dialog", "SUM OF: Value unknown - Should display warning on switch")
      .click(".modal-dialog button.btn-primary")
      .waitForElementNotVisible('.bootbox-confirm .modal-dialog', 2000)
      .verify.elementPresent("#" + sumOfFields[0] + ":disabled", "SUM OF: Value unknown - Input SHOULD be disabled")
      .verify.elementNotPresent("#" + sumOfFields[0] + ":enabled", "SUM OF: Value unknown - Input should NOT be enabled")
      .verify.elementPresent("#" + sumOfFields[1] + ":disabled", "SUM OF: Value unknown - Input SHOULD be disabled (testing sibling)")
      .verify.elementNotPresent("#" + sumOfFields[1] + ":enabled", "SUM OF: Value unknown - Input should NOT be enabled (testing sibling)")
      .click("#fg-"+ sumOfFields[0] +" .btn-dropdown")
      .click("#fg-"+ sumOfFields[0] +" ul .menu-enable")
      .verify.elementNotPresent("#" + sumOfFields[0] + ":disabled", "SUM OF: Value known - Input should NOT be disabled")
      .verify.elementPresent("#" + sumOfFields[0] + ":enabled", "SUM OF: Value known - Input SHOULD be enabled")
      .click("#fg-"+ sumOfFields[0] +" .btn-dropdown")
      .click("#fg-"+ sumOfFields[0] +" ul .menu-disable-input")
      .waitForElementVisible('.bootbox-confirm .modal-dialog', 2000)
      .click(".modal-dialog button.btn-default")
      .verify.elementNotPresent("#" + sumOfFields[0] + ":disabled", "SUM OF: Change to unknown was cancelled - Input should NOT be disabled")
      .verify.elementPresent("#" + sumOfFields[0] + ":enabled", "SUM OF: Change to unknown was cancelled - Input SHOULD be enabled")
      
      // Help text
      
      
      
      .end();
  },
};
