# E2E-testning

Installera [nightwatch](http://nightwatchjs.org/)

    $ npm install -g nightwatch
    
Ladda ner den senaste versionen av selenium från [denna sidan](http://selenium-release.storage.googleapis.com/index.html) och placera JAR-filen i ``e2e/bin/``

Gå till e2e-mappen
    
    $ cd e2e
    
Kör test

    $ nightwatch --test tests/<testfile>.js
