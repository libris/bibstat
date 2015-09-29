describe('Bibstat', function() {

  describe('Form', function() {
    
    before(function(client, done) {
      done();
    });
    
    after(function(client, done) {
      client.end(function() {
        done();
      });
    });
    
    afterEach(function(client, done) {
      done();
    });
    
    beforeEach(function(client, done) {
      done();
    });
    
    it('Should tell the user if no fields are entered', function(client) {
      
      client
        .url('http://localhost:8000/surveys/54b7ca100b52ff12b56c8279?p=umyzlsJmi2')
        .waitForElementPresent('body', 10000)
        .waitForElementPresent('.container', 10000)
        .expect.element('.answers-text').text.to.equal('Inga fält är ifyllda')
        
    });
    
    
    it('Should report that the user has filled out some fields', function(client) {
      client.setValue('#Arsverke01', 1, function() {
        client.setValue('#Arsverke02', 2, function() {
          client.setValue('#Arsverke03', 5, function() {
            client.setValue('#Arsverke04', 9, function () {
              client.expect.element('.answers-text').text.to.not.equal('Inga fält är ifyllda');
              client.expect.element('#unsaved-changes-label').text.to.equal('Det finns ifyllda svar som inte sparats');
              client.clearValue('#Arsverke01');
              client.clearValue('#Arsverke02');
              client.clearValue('#Arsverke03');
              client.clearValue('#Arsverke04');
            })
          })
        })
      })  
    });
    
    describe('notEmpty validation', function() {
      it('Should disallow empty input value', function(client) {
        client.setValue('#Epost01', '', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Epost01 small[data-bv-validator=notEmpty]').to.have.attribute('data-bv-result').equals('INVALID');
            client.expect.element('#fg-Epost01').to.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Epost01');
        });
        client.setValue('#Epost01', 'Test', function() {
          client.click('h2.section-title', function() {
              client.expect.element('#fg-Epost01 small[data-bv-validator=notEmpty]').to.have.attribute('data-bv-result').equals('VALID');
          });
          client.clearValue('#Epost01');
        });
      });
    })
    
    describe('Email validation', function() {
      
      it('Should only allow proper e-mail strings', function(client) {
        client.setValue('#Epost01', 'Test', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Epost01 small[data-bv-validator=regexp]').to.have.attribute('data-bv-result').equals('INVALID');
            client.expect.element('#fg-Epost01').to.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Epost01');
        });
        client.setValue('#Epost01', 'Test@test', function() {
          client.click('h2.section-title', function() {
              client.expect.element('#fg-Epost01 small[data-bv-validator=regexp]').to.have.attribute('data-bv-result').equals('INVALID');
              client.expect.element('#fg-Epost01').to.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Epost01');
        });
        client.setValue('#Epost01', 'Test@test.se', function() {
          client.click('h2.section-title', function() {
              client.expect.element('#fg-Epost01 small[data-bv-validator=regexp]').to.have.attribute('data-bv-result').equals('VALID');
              client.expect.element('#fg-Epost01').to.not.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Epost01');
        });
      });
    });
      
      
    describe('Phone number validation', function () {
      it('Should only allow proper telephone number strings', function (client) {
        client.setValue('#Tele01', '123', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Tele01 small[data-bv-validator=regexp]').to.have.attribute('data-bv-result').equals('INVALID');
            client.expect.element('#fg-Tele01').to.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Tele01');
        });
        client.setValue('#Tele01', '123-abc-test', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Tele01 small[data-bv-validator=regexp]').to.have.attribute('data-bv-result').equals('INVALID');
            client.expect.element('#fg-Tele01').to.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Tele01');
        });
        client.setValue('#Tele01', '(010)-709 30 00', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Tele01 small[data-bv-validator=regexp]').to.have.attribute('data-bv-result').equals('INVALID');
            client.expect.element('#fg-Tele01').to.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Tele01');
        });
        client.setValue('#Tele01', '+46700073999', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Tele01 small[data-bv-validator=regexp]').to.have.attribute('data-bv-result').equals('VALID');
            client.expect.element('#fg-Tele01').to.not.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Tele01');
        });
        client.setValue('#Tele01', '010-709 30 00', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Tele01 small[data-bv-validator=regexp]').to.have.attribute('data-bv-result').equals('VALID');
            client.expect.element('#fg-Tele01').to.not.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Tele01');
        });
      });  
    });
    
    describe('Integer validation', function () {
      it('Should only allow integers', function (client) {
        client.setValue('#Bokbuss01', 'abc', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Bokbuss01 small[data-bv-validator=integer]').to.have.attribute('data-bv-result').equals('INVALID');
            client.expect.element('#fg-Bokbuss01').to.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Bokbuss01');
        });
        client.setValue('#Bokbuss01', '123', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Bokbuss01 small[data-bv-validator=integer]').to.have.attribute('data-bv-result').equals('VALID');
            client.expect.element('#fg-Bokbuss01').to.not.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Bokbuss01');
        });
      });
    });
    
    describe('lessThan validation', function () {
      it('Should only allow number below or including 99999999', function (client) {
        client.setValue('#Bokbuss01', '99999999', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Bokbuss01 small[data-bv-validator=lessThan]').to.have.attribute('data-bv-result').equals('VALID');
            client.expect.element('#fg-Bokbuss01').to.not.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Bokbuss01');
        });
          client.setValue('#Bokbuss01', '1', function() {
            client.click('h2.section-title', function() {
              client.expect.element('#fg-Bokbuss01 small[data-bv-validator=lessThan]').to.have.attribute('data-bv-result').equals('VALID');
              client.expect.element('#fg-Bokbuss01').to.not.have.attribute('class').contain('has-error');
            });
            client.clearValue('#Bokbuss01');
          });
        client.setValue('#Bokbuss01', '100000000', function() {
          client.click('h2.section-title', function() {
            client.expect.element('#fg-Bokbuss01 small[data-bv-validator=lessThan]').to.have.attribute('data-bv-result').equals('INVALID');
            client.expect.element('#fg-Bokbuss01').to.have.attribute('class').contain('has-error');
          });
          client.clearValue('#Bokbuss01');
        });
      });
    });
    
    describe('Sum-of fields', function() {
      
      it('Should sum the parts to a total', function(client) {
        client.setValue('#Arsverke01', 1, function() {
          client.setValue('#Arsverke02', 2, function() {
            client.setValue('#Arsverke03', 5, function() {
              client.setValue('#Arsverke04', 9, function () {
                client.click('h2.section-title', function() {
                  client.expect.element('#Arsverke99').to.have.value.that.equals('17');
                })
              })
            })
          })
        })
      });
      
      it('Should warn if changing to unknown value', function(client) {
        client.click('#fg-Arsverke01 .btn-dropdown', function() {
          client.click('#fg-Arsverke01 .menu-disable-input', function () {
            client.expect.element('.bootbox-confirm .modal-dialog').to.be.visible.before(2000);
          })
        })
      });
      
      it('Should disable all inputs if dialog is accepted', function(client) {
        client.click('.bootbox-confirm .modal-dialog .btn-primary', function() {
          client.expect.element('#Arsverke01').to.not.be.enabled;
          client.expect.element('#Arsverke02').to.not.be.enabled;
          client.expect.element('#Arsverke03').to.not.be.enabled;
          client.expect.element('#Arsverke04').to.not.be.enabled;
        })
      });
      
      it('Should enable all inputs if change to known', function(client) {
        client.click('#fg-Arsverke01 .btn-dropdown', function() {
          client.click('#fg-Arsverke01 .menu-enable', function () {
            client.expect.element('#Arsverke01').to.be.enabled;
            client.expect.element('#Arsverke02').to.be.enabled;
            client.expect.element('#Arsverke03').to.be.enabled;
            client.expect.element('#Arsverke04').to.be.enabled;
          })
        })
      });
      
      it('Should not disable inputs if dialog is rejected', function(client) {
        client.click('#fg-Arsverke01 .btn-dropdown', function() {
          client.click('#fg-Arsverke01 .menu-disable-input', function () {
            client.expect.element('.bootbox-confirm .modal-dialog').to.be.visible.before(2000);            
            client.click('.bootbox-confirm .modal-dialog .btn-default', function() {
              client.expect.element('#Arsverke01').to.be.enabled;
              client.expect.element('#Arsverke02').to.be.enabled;
              client.expect.element('#Arsverke03').to.be.enabled;
              client.expect.element('#Arsverke04').to.be.enabled;
            })
          })
        })
      });
      
    });
    
    
  });

});
