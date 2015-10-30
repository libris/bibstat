
module.exports = {
  
  
  'Open survey' : function (browser) {
    var emailField = 'Epost01',
        teleField = 'Tele01',
        integerField = 'Bokbuss01',
        decimalField = 'Arsverke01',
        outsideField = '.navbar-text', // Used to blur input fields
        sumOfFields = [
          'Arsverke01',
          'Arsverke02',
          'Arsverke03',
          'Arsverke04',
          'Arsverke99',
          'Arsverke05'
        ];
      
    function formatOutput() {
      var output = '';
      for(var arg = 0; arg < arguments.length; arg++) {
        while(arguments[arg].length < 20)
          arguments[arg] += ' ';
        output += arguments[arg];
        if (arg < arguments.length - 1)
          output += " | ";
      }
      return output;
    }
    
    browser
      .url('http://localhost:8000/surveys/54b7ca100b52ff12b56c8279?p=umyzlsJmi2')
      .waitForElementVisible('body', 5000)
      
      .verify.containsText('.navbar-text', 'Välkommen')
      
      .click("#" + emailField)
      .setValue("#" + emailField, '')
      .click(outsideField)
      .verify.visible('#fg-'+emailField +' small[data-bv-validator=notEmpty]', formatOutput('Validation Msg', 'notEmpty', 'Should show msg on fail'))
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=notEmpty]', 'data-bv-result', 'INVALID', formatOutput('Validation', 'notEmpty', 'INVALID for ""'))
      
      .click("#" + emailField)
      .setValue("#" + emailField, 'Test')
      .click(outsideField)
      .verify.hidden('#fg-'+emailField+' small[data-bv-validator=notEmpty]', formatOutput('Validation Msg', 'notEmpty', 'Should hide msg on pass'))
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=notEmpty]', 'data-bv-result', 'VALID', formatOutput('Validation', 'notEmpty', 'VALID for "Test"'))
      .verify.visible('#fg-'+emailField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (email)', 'Should show msg on fail'))
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=regexp]', 'data-bv-result', 'INVALID', formatOutput('Validation', 'regexp', 'INVALID for "Test"'))
      .clearValue("#" + emailField)
      
      .click("#" + emailField)
      .setValue("#" + emailField, 'test@test.test')
      .click(outsideField)
      .verify.hidden('#fg-'+emailField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (email)', 'Should hide msg on pass'))
      .verify.attributeEquals('#fg-'+emailField +' small[data-bv-validator=regexp]', 'data-bv-result', 'VALID', formatOutput('Validation', 'regexp', 'VALID for "test@test.test"'))

      .click("#" + teleField)
      .setValue("#" + teleField, '3')
      .click(outsideField)
      .verify.visible('#fg-'+teleField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (phone)', 'Should show msg on fail'))
      .clearValue("#" + teleField)
      .click("#" + teleField)
      .setValue("#" + teleField, '010-709 30 00')
      .click(outsideField)
      .verify.hidden('#fg-'+teleField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (phone)', 'Should hide msg on pass'))
      
      .click("#" + integerField)
      .setValue("#" + integerField, '99999999999999')
      .click(outsideField)
      .verify.visible('#fg-'+integerField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (integer)', 'Should show msg on fail'))
      .clearValue("#" + integerField)
      .click("#" + integerField)
      .setValue("#" + integerField, '3')
      .click(outsideField)
      .verify.hidden('#fg-'+integerField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (integer)', 'Should hide msg on pass'))

      .click("#" + decimalField)
      .setValue("#" + decimalField, '99999999999999')
      .click(outsideField)
      .verify.visible('#fg-'+decimalField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (decimal)', 'Should show msg on fail'))
      .clearValue("#" + decimalField)
      .click("#" + decimalField)
      .setValue("#" + decimalField, '3,33')
      .click(outsideField)
      .verify.hidden('#fg-'+decimalField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (decimal)', 'Should hide msg on pass'))
      .clearValue("#" + decimalField)
      .click("#" + decimalField)
      .setValue("#" + decimalField, '3,3333')
      .click(outsideField)
      .verify.visible('#fg-'+decimalField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (decimal)', 'Should show msg on fail'))
      .clearValue("#" + decimalField)
      .setValue("#" + decimalField, '-')
      .click(outsideField)
      .verify.hidden('#fg-'+decimalField+' small[data-bv-validator=regexp]', formatOutput('Validation Msg', 'regexp (decimal)', 'Should hide msg on pass'))
      .clearValue("#" + decimalField)

      // Sum-of
      .click("#" + sumOfFields[0])
      .setValue("#" + sumOfFields[0], 5)
      .setValue("#" + sumOfFields[1], 2)
      .setValue("#" + sumOfFields[2], 7)
      .setValue("#" + sumOfFields[3], 8)
      .click(outsideField)
      .verify.value("#" + sumOfFields[4], "22", formatOutput('Sum of', 'Total value should equal the total of subfields'))
      
      // Unknown value
      .setValue("#" + sumOfFields[0], 5) // Used to scroll the item properly into view.
      .click("#fg-"+ sumOfFields[0] +" .btn-dropdown")
      .click("#fg-"+ sumOfFields[0] +" ul .menu-disable-input")
      .waitForElementVisible('.bootbox-confirm .modal-dialog', 2000)
      .verify.elementPresent(".bootbox-confirm .modal-dialog", formatOutput('Sum of', 'Value unknown', 'Should display warning on switch'))
      .click(".modal-dialog button.btn-primary")
      .waitForElementNotVisible('.bootbox-confirm .modal-dialog', 2000)
      .verify.elementPresent("#" + sumOfFields[0] + ":disabled", formatOutput('Sum of', 'Value unknown', 'Input SHOULD be disabled'))
      .verify.elementNotPresent("#" + sumOfFields[0] + ":enabled", formatOutput('Sum of', 'Value unknown', 'Input should NOT be enabled'))
      .verify.elementPresent("#" + sumOfFields[1] + ":disabled", formatOutput('Sum of', 'Value unknown', 'Input SHOULD be disabled', '(testing sibling field)'))
      .verify.elementNotPresent("#" + sumOfFields[1] + ":enabled", formatOutput('Sum of', 'Value unknown', 'Input should NOT be enabled', '(testing sibling field)'))
      .click("#fg-"+ sumOfFields[0] +" .btn-dropdown")
      .click("#fg-"+ sumOfFields[0] +" ul .menu-enable")
      .verify.elementNotPresent("#" + sumOfFields[0] + ":disabled", formatOutput('Sum of', 'Value known', 'Input should NOT be disabled'))
      .verify.elementPresent("#" + sumOfFields[0] + ":enabled", formatOutput('Sum of', 'Value known', 'Input SHOULD be enabled'))
      .click("#fg-"+ sumOfFields[0] +" .btn-dropdown")
      .click("#fg-"+ sumOfFields[0] +" ul .menu-disable-input")
      .waitForElementVisible('.bootbox-confirm .modal-dialog', 2000)
      .click(".modal-dialog button.btn-default")
      .verify.elementNotPresent("#" + sumOfFields[0] + ":disabled", formatOutput('Sum of', 'Change to unknown cancelled', 'Input should NOT be disabled'))
      .verify.elementPresent("#" + sumOfFields[0] + ":enabled", formatOutput('Sum of', 'Change to unknown cancelled', 'Input SHOULD be enabled'))
      
      // Help text
      .pause(500)
      .click('#fg-' +sumOfFields[0]+' .btn-help')
      .verify.elementPresent('div.popover', formatOutput('Help popover', 'Should be present after help button click'))
      .click(outsideField)
      .pause(500)
      .verify.elementNotPresent('div.popover', formatOutput('Help popover', 'Should NOT be present after click outside popover'))
      
      
      
      .end();
  },
};
