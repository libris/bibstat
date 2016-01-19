# E2E-testning

End-to-end-webbtester för att testa enkätformuläret. Testerna går igenom och kollar att vissa element och inputs finns på plats samt att validering, summering och hjälptexter fungerar. Obs att valideringstesterna kräver att korrekta enheter för de olika variablerna är inställda (t ex för e-postfält och telefonnummerfält).

## Installation

Installera [webdriver.io](http://webdriver.io/) och jasmine

    $ npm install -g webdriverio
    $ npm install -g jasmine
   
Ladda ner den senaste versionen av selenium-server-standalone från [denna sidan](http://selenium-release.storage.googleapis.com/index.html)

Placera JAR-filen i ``e2e/bin/``

alternativt installera gnm $ brew install selenium-server-standalone (obs, ej testat)

Om du vill köra test i Chrome så behöver du Chromedriver. Den finns den att ladda ner [här](https://code.google.com/p/selenium/wiki/ChromeDriver).

Lägg den i ``e2e/bin/``

alternativt installera gnm $ brew install chromedriver (obs, ej testat)

Testade versioner (på Mac):

- webdriverio: 3.3.0
- jasmine: 2.4.1
- selenium-server-standalone: 2.47.1
- chromedriver: 2.20
- Google Chrome: 47.0

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
