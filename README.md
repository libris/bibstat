# Biblioteksstatistiken

Sveriges officiella biblioteksstatistik.

## Beroenden

* Python 2.7.x (Django)
* MongoDB 2.6.x

Pakethanteraren [pip](http://pip-installer.org) används för att hantera beroenden i Python.  
Denna finns inkluderad tillsammans med Python 2.7.9 eller senare.

## Installation

Nedan är ett exempel på en minimal installation för Mac OS X.  
Detta kräver att du redan har installerat [Homebrew](http://brew.sh) sedan tidigare.

	# Installera beroenden
	$ brew install git mongodb python
	$ pip install virtualenvwrapper

	# Klona projektet
	$ git clone git@github.com:libris/bibstat
	$ cd bibstat

	# Starta MongoDB
	$ mkdir mongodb
	$ mongod --dbpath $(pwd)/mongodb

	# Skapa en användare för databasen
	$ mongo
	$ use bibstat
	$ db.createUser({user:"bibstat", pwd:"bibstat", roles:["readWrite"]})
	$ exit

	# Skapa en virtuell miljö för Python
	$ source /usr/local/bin/virtualenvwrapper.sh
	$ mkvirtualenv -p /usr/local/bin/python bibstat
	$ workon bibstat

	# Installera paket och konfigurera
	$ pip install -r requirements.txt
	$ cp bibstat/settings_local.py.example bibstat/settings_local.py
	$ python manage.py createsuperuser --username=super --email=a@b.c

	# Starta servern
	$ python manage.py runserver

## Testning

Testerna kan köras genom att använda följande kommando.  
Både enhetstesterna och integrationstesterna kommer köras.

	$ python manage.py test

## Deploy

Det gemensamma verktyget [DevOps](https://github.com/libris/devops) används för att sköta deploy.  
För att kunna göra en deploy krävs anslutning till det lokala nätverket.

Båda miljöerna går att komma åt med SSH på det lokala nätverket.  
Inloggningsuppgifterna till maskinerna går att få genom att fråga IT.  
Notera att `sudo` är trasigt på maskinerna, så `root` måste användas.

**Sökvägar**  
Konfiguration för Django: `/data/appl/config/bibstat_local.py`.  
Konfiguration för Apache: `/etc/httpd/conf.d/bibstat.conf`.  
Felmeddelanden loggas till: `/var/log/httpd/bibstat-error_log`.  
Inkommande requests loggas till: `/var/log/httpd/bibstat-access_log`.

Varje deploy får en egen tids- och datumstämplad mapp i `/data/appl/`.  
Den senaste versionen som används länkas in till `/data/appl/bibstat`.  
Tidigare versioner tas inte bort automatiskt, utan måste tas bort manuellt.

**Backup**  
Båda miljöerna körs i var sin egen virtuell maskin med Red Hat Linux.  
Version: `Red Hat Enterprise Linux Server release 6.6 (Santiago)`.  

Backup sker genom att varje natt ta en kopia på den virtuella maskinen.  
IT kan hjälpa till med driften och återställning om det skulle behövas.  
[Mikko Yletyinen](mailto:mikko.yletyinen@kb.se) har tidigare varit kontaktperson gällande driften.

### Stage

Adress: [bibstat-stg.libris.kb.se](http://bibstat-stg.libris.kb.se)  
Hårdvara: 2 GB Minne, 80 GB Hårddisk  
Deploy: `fab conf.stgbibstat app.bibstat.deploy`  
Inloggning: `super / super` för att kunna administrera.

### Produktion

Adress: [bibstat.libris.kb.se](http://bibstat.libris.kb.se)  
Hårdvara: 16 GB Minne, 80 GB Hårddisk  
Deploy: `fab conf.prodbibstat app.bibstat.deploy`  
Inloggning: Fråga en involverad utvecklare efter uppgifterna.

## Import

**Termer**  
Tidigare års statistiktermer kan importeras på följande sett.  
Filerna finns att hitta i projektkatalogen [`data/variables`](data/variables).

	$ python manage.py import_variables --file=data/variables/folk_termer.xlsx --target_group=folkbib	
	$ python manage.py import_variables --file=data/variables/forsk_termer.xlsx --target_group=specbib
	$ python manage.py import_variables --file=data/variables/skol_termer.xlsx --target_group=skolbib
	$ python manage.py import_variables --file=data/variables/sjukhus_termer.xlsx --target_group=sjukbib

**Enkäter**  
Tidigare års enkäter med de inlämnade värdena kan importeras på följande sett.  
En exekvering av ett kommando importerar ett års värden för en viss bibliotekstyp.  
Filerna finns på både stage- och produktionsmiljön i `/data/appl/old_bibstat_data`.

	$ python manage.py import_survey_responses --file=/data/appl/old_bibstat_data/Folkbibliotek.xlsx --target_group=folkbib --year=2013
	$ python manage.py import_survey_responses --file=/data/appl/old_bibstat_data/Folkbibliotek.xlsx --target_group=folkbib --year=2012
	$ python manage.py import_survey_responses --file=/data/appl/old_bibstat_data/Folkbibliotek.xlsx --target_group=folkbib --year=2011
	$ python manage.py import_survey_responses --file=/data/appl/old_bibstat_data/Folkbibliotek.xlsx --target_group=folkbib --year=2010

## Analytics

[Google Analytics](http://www.google.com/analytics) används för att spåra hur externa användare använder tjänsten.  
Kontot som används delas tillsammans med de andra utvecklade systemen i Libris.

Inloggningsuppgifterna kan fås genom att fråga en involverad utvecklare.