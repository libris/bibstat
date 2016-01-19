describe('Bibstat', function() {
  
  jasmine.DEFAULT_TIMEOUT_INTERVAL = 9999999;
  
  beforeAll(function(done) {
    
    browser
      .url('http://localhost:8000/surveys/54b7ca100b52ff12b56c8279?p=umyzlsJmi2')
      .waitForExist('body', 9999999)
      .waitForVisible('.loading', 9999999, true) // Väntar tills loadingboxen försvinner
      .call(done);
  });
  
  afterAll(function(done) {
    browser.end(done);
  });
  
  it('Should tell the user if no fields are entered', function(done) {
    browser
      .getText('.answers-text').then(function(text) {
        expect(text).toBe('Inga fält är ifyllda');
      })
      .call(done);
  });
  
  it('Should report that the user has filled out some fields', function(done) {
    browser
      .setValue('#Arsverke01', 1)
      .setValue('#Arsverke02', 2)
      .setValue('#Arsverke03', 5)
      .setValue('#Arsverke04', 9)
      .getText('.answers-text').then(function(text) {
        expect(text).not.toBe('Inga fält är ifyllda');
      })
      .getText('#unsaved-changes-label').then(function(text) {
        expect(text).toBe('Det finns ifyllda svar som inte sparats');
      })
      .call(done);
  });
  
  describe('notEmpty validation', function() {
    it('Should disallow empty input value', function(done) {
      browser
        .setValue('#Epost01', '')
        .keys('Tab')
        .getAttribute('#fg-Epost01 small[data-bv-validator=notEmpty]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID');
        })
        .setValue('#Epost01', 'Test')
        .keys('Tab')
        .getAttribute('#fg-Epost01 small[data-bv-validator=notEmpty]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('VALID');
        })
        .call(done);
    });    
  });
  
  describe('Email validation', function() {
    it('Should only allow proper e-mail strings', function(done){
      browser
        .setValue('#Epost01', 'Test')
        .keys('Tab')
        .getAttribute('#fg-Epost01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID');
        })
        .setValue('#Epost01', 'test@test')
        .keys('Tab')
        .getAttribute('#fg-Epost01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID');
        })
        .setValue('#Epost01', 'test@test.se')
        .keys('Tab')
        .getAttribute('#fg-Epost01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('VALID');
        })
        .call(done);
    });
  });
  
  describe('Phone number validation', function() {
    it('Should only allow proper telephone number strings', function(done) {
      browser
        .setValue('#Tele01', '3')
        .keys('Tab')
        .getAttribute('#fg-Tele01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID');
        })
        .setValue('#Tele01', '123-abc-test')
        .keys('Tab')
        .getAttribute('#fg-Tele01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID');
        })
        .setValue('#Tele01', '(010)-709 30 00')
        .keys('Tab')
        .getAttribute('#fg-Tele01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID');
        })
        .setValue('#Tele01', '+46700073999')
        .keys('Tab')
        .getAttribute('#fg-Tele01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('VALID');
        })
        .setValue('#Tele01', '010-709 30 00')
        .keys('Tab')
        .getAttribute('#fg-Tele01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('VALID');
        })
        .call(done);
    });
  });
  
  describe('Integer validation', function() {
    it('Should only allow integers', function(done) {
      browser
        .setValue('#Bokbuss01', 'abc')
        .keys('Tab')
        .getAttribute('#fg-Bokbuss01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID')
        })
        .setValue('#Bokbuss01', '123')
        .keys('Tab')
        .getAttribute('#fg-Bokbuss01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('VALID')
        })
        .call(done);
    });
  });

  describe('Decimal validation', function() {
    it('Should not allow too big value or more than three decimals', function(done){
      browser
          .setValue('#Arsverke01', '99999999999999')
          .keys('Tab')
          .getAttribute('#fg-Arsverke01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID')
        })
          .setValue('#Arsverke01', '3,33')
          .keys('Tab')
          .getAttribute('#fg-Arsverke01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
            expect(attr).toBe('VALID')
        })
          .setValue('#Arsverke01', '3,3333')
          .keys('Tab')
          .getAttribute('#fg-Arsverke01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
            expect(attr).toBe('INVALID')
        })
          .setValue('#Arsverke01', '-')
          .keys('Tab')
          .getAttribute('#fg-Arsverke01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
            expect(attr).toBe('VALID')
        })
          setValue('#Arsverke01', '')
        .call(done);
    });
  });
  
  describe('lessThan validation', function() {
    it('Should only allow number below or including 99999999', function(done) {
      browser
        .setValue('#Bokbuss01', '99999999')
        .keys('Tab')
        .getAttribute('#fg-Bokbuss01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('VALID')
        })
        .setValue('#Bokbuss01', '1')
        .keys('Tab')
        .getAttribute('#fg-Bokbuss01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('VALID')
        })
        .setValue('#Bokbuss01', '100000000')
        .keys('Tab')
        .getAttribute('#fg-Bokbuss01 small[data-bv-validator=regexp]', 'data-bv-result').then(function(attr) {
          expect(attr).toBe('INVALID')
        })
        .call(done);
    });
  });
  
  describe('Sum-of fields', function() {
    it('Should sum the parts to a total', function(done) {
      browser
        .setValue('#Arsverke01', 1)
        .setValue('#Arsverke02', 2)
        .setValue('#Arsverke03', 5)
        .setValue('#Arsverke04', 9)
        .keys('Tab')
        .getValue('#Arsverke99').then(function(value) {
          expect(value).toBe('17');
        })
        .call(done);
    });
    it('Should warn if changing to unknown value', function(done) {
      browser
        .setValue('#Arsverke01', 1)
        .waitForVisible('#fg-Arsverke01 .btn-dropdown', 1500)
        .click('#fg-Arsverke01 .btn-dropdown')
        .click('#fg-Arsverke01 .menu-disable-input')
        .waitForVisible('.bootbox-confirm .modal-dialog', 1500)
        .isVisible('.bootbox-confirm .modal-dialog').then(function (isVisible) {
          expect(isVisible).toBe(true);
        })
        .call(done);
    });
    it('Should disable all inputs if dialog is accepted', function(done) {
      browser
        .click('.bootbox-confirm .modal-dialog .btn-primary')
        .isEnabled('#Arsverke01').then(function(isEnabled) {
          expect(isEnabled).toBe(false);
        })
        .isEnabled('#Arsverke02').then(function(isEnabled) {
          expect(isEnabled).toBe(false);
        })
        .isEnabled('#Arsverke03').then(function(isEnabled) {
          expect(isEnabled).toBe(false);
        })
        .isEnabled('#Arsverke04').then(function(isEnabled) {
          expect(isEnabled).toBe(false);
        })
        .call(done);
    });
    it('Should enable all inputs if change to known', function(done) {
      browser
        .click('#fg-Arsverke01 .btn-dropdown')
        .click('#fg-Arsverke01 .menu-enable')
        .isEnabled('#Arsverke01').then(function(isEnabled) {
          expect(isEnabled).toBe(true);
        })
        .isEnabled('#Arsverke02').then(function(isEnabled) {
          expect(isEnabled).toBe(true);
        })
        .isEnabled('#Arsverke03').then(function(isEnabled) {
          expect(isEnabled).toBe(true);
        })
        .isEnabled('#Arsverke04').then(function(isEnabled) {
          expect(isEnabled).toBe(true);
        })
        .call(done);
    });
    it('Should not disable inputs if dialog is rejected', function(done) {
      browser
        .click('#fg-Arsverke01 .btn-dropdown')
        .click('#fg-Arsverke01 .menu-disable-input')
        .waitForVisible('.bootbox-confirm .modal-dialog', 1500)
        .click('.bootbox-confirm .modal-dialog .btn-default')
        .isEnabled('#Arsverke01').then(function(isEnabled) {
          expect(isEnabled).toBe(true);
        })
        .isEnabled('#Arsverke02').then(function(isEnabled) {
          expect(isEnabled).toBe(true);
        })
        .isEnabled('#Arsverke03').then(function(isEnabled) {
          expect(isEnabled).toBe(true);
        })
        .isEnabled('#Arsverke04').then(function(isEnabled) {
          expect(isEnabled).toBe(true);
        })
        .call(done);        
    });
  });
  
  
  
});
