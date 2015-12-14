# E2E-testning

End-to-end-webbtester för att testa enkätformuläret. Testerna går igenom och kollar att vissa element och inputs finns på plats samt att validering, summering och hjälptexter fungerar. Obs att valideringstesterna kräver att korrekta enheter för de olika variablerna är inställda (t ex för e-postfält och telefonnummerfält).

## Installation

Installera [webdriver.io](http://webdriver.io/)

    $ npm install -g webdriverio

Installera Selenium

    $ brew install selenium-server-standalone
    
(alternativt ladda ner den senaste versionen av selenium-server-standalone från [denna sidan](http://selenium-release.storage.googleapis.com/index.html) och placera JAR-filen i ``e2e/bin/``)

Om du vill köra test i Chrome så behöver du Chromedriver. Installera den mha homebrew:
 
    $ brew install chromedriver

Alternativt finns den att ladda ner [här](https://code.google.com/p/selenium/wiki/ChromeDriver).

Lägg den i ``e2e/bin/``

## Konfiguera

Kopiera konfigureringsfilen:

    $ cd e2e
    $ cp wdio.conf.js.example wdio.conf.js

I ``wdio.conf.js``

* Anpassa portar
* Anpassa vilka browsers du vill testa
  * Om man kör flera parallella browsers behöver Firefox startas sist, då den inte klarar av att hantera vissa händelser om den inte är i fokus.

## Köra tester

Gå till e2e-mappen
    
    $ cd e2e
    
Starta selenium (här anger vi även sökväg till chromedriver)

    $ java -jar bin/selenium-server-standalone-2.47.1.jar -Dwebdriver.chrome.driver=bin/chromedriver
    
Kör tester

    $ wdio wdio.conf.js
