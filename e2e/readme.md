# E2E-testning

## Installation

Installera [nightwatch](http://nightwatchjs.org/)

    $ npm install -g nightwatch
    
Ladda ner den senaste versionen av selenium-server-standalone från [denna sidan](http://selenium-release.storage.googleapis.com/index.html) och placera JAR-filen i ``e2e/bin/``

Om du vill köra test i Chrome så behöver du Chromedriver som finns att ladda ner [här](https://code.google.com/p/selenium/wiki/ChromeDriver). Lägg den i ``e2e/bin/``

## Konfiguera

Portnummer kan anpassas i ``nightwatch.json``

## Köra tester

Gå till e2e-mappen
    
    $ cd e2e
    
Kör test

    $ nightwatch --test tests/<testfile>.js

Kör test med specifika environments, i exemplet körs defalt=firefox och chrome (enligt nightwatch.json)

    $ nightwatch --test tests/<testfile>.js -e default,chrome
