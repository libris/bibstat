# E2E-testning

End-to-end-webbtester för att testa enkätformuläret. Testerna går igenom och kollar att vissa element och inputs finns på plats samt att validering, summering och hjälptexter fungerar. Obs att valideringstesterna kräver att korrekta enheter för de olika variablerna är inställda (t ex för e-postfält och telefonnummerfält).

## Installation

Installera [nightwatch](http://nightwatchjs.org/)

    $ npm install -g nightwatch

Installera Selenium

    $ brew install selenium-server-standalone
    
(alternativt ladda ner den senaste versionen av selenium-server-standalone från [denna sidan](http://selenium-release.storage.googleapis.com/index.html) och placera JAR-filen i ``e2e/bin/``)

Om du vill köra test i Chrome så behöver du Chromedriver. Installera den mha homebrew:
 
    $ brew install chromedriver

(alternativt finns den att ladda ner [här](https://code.google.com/p/selenium/wiki/ChromeDriver). Lägg den i ``e2e/bin/``)

## Konfiguera

Kopiera konfigureringsfilen:

    $ cd e2e
    $ cp nightwatch.json.example nightwatch.json

I ``nightwatch.json``:

- Kolla selenium "server_path" (ex "/usr/local/Cellar/selenium-server-standalone/2.48.2/libexec/selenium-server-standalone-2.48.2.jar" eller "bin/selenium-server-standalone-2.47.1.jar")
- Kolla "webdriver.chrome.driver"  ("/usr/local/bin/chromedriver" eller "bin/chromedriver")
- Anpassa portar
- Välj om Selenium ska startas via Nightwatch eller separat 

## Köra tester

Gå till e2e-mappen
    
    $ cd e2e
    
Kör test

    $ nightwatch --test tests/<testfile>.js

Kör test med specifika environments, i exemplet körs defalt=firefox och chrome (enligt nightwatch.json)

    $ nightwatch --test tests/<testfile>.js -e default,chrome

## Stänga ner selenium

När ett test kraschar under körning (t ex vid syntaxfel i testkoden) och man försöker köra igen, så kan man få felet att ens port redan är upptagen. Du kan då stänga ner Selenium genom att kalla på följande adress i din browser:

http://localhost:4444/selenium-server/driver/?cmd=shutDownSeleniumServer
