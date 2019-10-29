# Biblioteksstatistiken

## Beroenden

* Python 2.7.x (Django)
* MongoDB 2.6.x

Pakethanteraren [pip](http://pip-installer.org) används för att hantera beroenden i Python.  
Denna finns inkluderad tillsammans med Python 2.7.9 eller senare.

## Installation

Nedan är ett exempel på en minimal installation för Mac OS X.  

	# Installera beroenden
	https://docs.mongodb.com/v2.6/tutorial/install-mongodb-on-os-x/
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
	$ python manage.py createsuperuser --username=super --email=a@b.com

	# Starta servern
	$ python manage.py runserver

### MongoDB i Docker

Ett alternativ till att installera MongoDB är att köra det i Docker.
https://hub.docker.com/_/mongo?tab=description&page=1&name=2.6

```sh
docker run --name bibstat_mongodb -v /abs/path/to/repo/mongodb:/data/db -d mongo:2.6
```

Konfigurera då `MONGODB_HOST` i `bibstat/settings_local.py` till returvärdet av

```sh
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' bibstat_mongodb
```

### Produktionsdata

Efter en första installation kommer det inte finnas någon data i den lokala miljön.  
Nedan är instruktioner för att göra en dump av produktionsdatabasen och importera den.

    # Gör en dump av produktionsdatabasen genom att ssh:a till bibstat.kb.se 
    # - <user> är dit eget (AD kopplat, kontakts drift om behörighet saknas)
    # - <username> och <password> till bibstat mongodb finns i Team Gul Vault
    #
    $ ssh <user>@bibstat.kb.se
    $ mongodump -d bibstat -u <username> -p <password>
    $ exit

    # Hämta ned dump till lokala maskinen
    $ sftp  <user>@bibstat.kb.se
    $ get -r dump
    $ exit

    # Importera produktionsdata
    $ mongorestore dump

Du kan alternativt ange att bara importera en `collection`, exempelvis enbart termerna med hjälp av `mongorestore dump/bibstat/libstat_variables.bson`. Användarnamn och lösenord för produktionsdatabasen finns i `/data/appl/config/bibstat_local.py`.

## Utveckling

Sidans alla resurser (.js & .css filer) minifieras med hjälp av requirejs och requirejs. (Detta kräver nodejs https://nodejs.org/ installerat på datorn.)

Installera requirejs genom:

    $ npm install -g requirejs

I mappen build finns byggfiler som körs med r.js. När ändringar är gjorda i Javascript och CSS måste dessa köras för att ändringarna ska ha effekt.

För att köra jobbet:

    $ ./build.sh

Nu är alla filer minifierade och redo för produktion!

I base-filerna i /bibstat/libstat/templates/base/ (admin.html resp. admin-survey.html) kan ni välja att använda de minifierade filerna eller orginal-filerna. 
Detta gör ni genom att ta bort / lägga till ".min" efter både css filen och javascript-filen (ex i produktion används "/static/css/bundle.min.css" och under utveckling kan "/static/css/bundle.css" användas för att slippa bygga om mellan uppdateringar).


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
Mikko Yletyinen har tidigare varit kontaktperson gällande driften.

En separat backup av databasen görs varje dag klockan 18.00 med Cron.  
Dessa sparas på en nätverksvolym, som har monterats under `/backup`.  
Använd `crontab -l` för att visa det cron-jobb som används för detta.

**Setup**  
Det finns en [sammanfattning](docs/servers.md) av hur miljöerna sattes upp.

### Stage

Redhat Enterprise Linux Server 6.10  
Adress: [bibstat-stg.kb.se](http://bibstat-stg.kb.se)  
Hårdvara: 8 GB Minne, 80 GB Hårddisk  
Deploy: `fab conf.bibstat_stg app.bibstat.deploy -u <username>`  
Inloggning: Fråga IT-drift om `sudo`-åtkomst eller inloggningsuppgifter.

### Produktion

Redhat Enterprise Linux Server 6.10  
Adress: [bibstat.kb.se](http://bibstat.kb.se)  
Hårdvara: 23 GB Minne, 80 GB Hårddisk  
Deploy: `fab conf.bibstat_prod app.bibstat.deploy -u <username>`  
Inloggning: Fråga IT-drift om `sudo`-åtkomst eller inloggningsuppgifter.

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

### Export
Export av enkäter till excelfil kan göras via administrationssidan [/surveys](http://bibstat.kb.se/surveys). Det öppna datat kan också exporteras till excelfil under "Öppna data". Då kommer enbart observationer med för variabler som är publika.

Script för export finns även under [libstat/management/commands]([libstat/management/commands).

För att ta ut enkäter:

	$ python manage.py export_surveys_to_excel --year=2014

För att ta ut data om biblioteken (ange all=y för att ta ut alla bibliotek, eller all=n för att endast få med bibliotek som saknar sigel):

	$ python manage.py export_libraries_to_excel --year=2012 --all=n
	
I servermiljöerna måste man aktivera virtuell env genom 
    
    $ cd /data/appl/bibstat
    $ source env/bin/activate
    
För att köra script som bakgrundsprocess:
    
    $ nohup python manage.py export_surveys_to_excel --year=2014 &
	
Filerna hamnar under [data/excel_exports] (data/excel_exports) (under /data/appl/excel_exports på servrarna)

## Analytics

[Google Analytics](http://www.google.com/analytics) används för att spåra hur externa användare använder tjänsten.  
Kontot som används delas tillsammans med de andra utvecklade systemen i Libris.

Inloggningsuppgifterna kan fås genom att fråga en involverad utvecklare.

Tjänsten genererar även data till Piwik på [http://analytics.kb.se](http://analytics.kb.se)
