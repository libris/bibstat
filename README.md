# Biblioteksstatistiken

## Beroenden

* Python 3.6.x (Django)
* MongoDB 5.0.x

## Installation

Nedan är ett exempel på en minimal installation i Linux.  

	# Installera MongoDB 5.0.x:
    # https://www.mongodb.com/docs/v5.0/installation/
    # Installera MongoDB Database Tools:
    # https://www.mongodb.com/try/download/database-tools
    # (inkluderar mongorestore & co, som ej längre är del av MongoDB-disten sen 4.4)

	# Klona projektet
	git clone git@github.com:libris/bibstat
	cd bibstat

	# Starta MongoDB
	$ mkdir mongodb
	$ mongod --dbpath $(pwd)/mongodb

	# Skapa en användare för databasen
	mongo
	> use bibstat
	> db.createUser({user:"bibstat", pwd:"bibstat", roles:["readWrite"]})
	> exit

	# Skapa en virtuell miljö för Python
    python3 -m venv venv
    # Aktivera virtuell miljö
    source venv/bin/activate
    # Installera Python-beroenden
    pip install -r requirements.txt

	# Konfigurera
	cp bibstat/settings_local.py.example bibstat/settings_local.py
    vi bibstat/settings_local.py # eller nano, eller...
    # Skapa admin-användare
	python manage.py createmongodbsuperuser --username=super --email=a@b.com

	# Starta servern
	python manage.py runserver
    # Alternativt (obs, gunicorn kommer inte serva statiska filer):
    gunicorn bibstat.wsgi

### Importera produktionsdata till lokal utvecklingsmiljö

    # Gör en dump av produktionsdatabasen
    ssh <user>@bibstat.kb.se
    mongodump -d bibstat -u <username> -p <password>
    exit
    
    # där <user> är din AD-användare och
    # <username> och <password> finns i Team Gul Vault

    # Hämta hem dumpen med sftp eller scp, t.ex:
    sftp  <user>@bibstat.kb.se
    get -r dump
    exit

    # Läs in datadumpen
    mongorestore dump

Du kan alternativt ange att bara importera en `collection`, exempelvis enbart termerna med hjälp av
`mongorestore dump/bibstat/libstat_variables.bson`. Användarnamn och lösenord för produktionsdatabasen
finns i `/data/appl/config/bibstat_local.py`.

## Utveckling

Sidans alla resurser (.js- och .css-filer) minifieras med hjälp av requirejs och requirejs.
(Detta kräver Node.js https://nodejs.org/ installerat på datorn. Förslagsvis Node.js 16 LTS.)

Installera requirejs genom:

    npm install -g requirejs

I mappen build finns byggfiler som körs med r.js. När ändringar är gjorda i Javascript och CSS måste dessa köras för att ändringarna ska ha effekt.

För att köra jobbet:

    ./build.sh

Nu är alla filer minifierade och redo för produktion!

I base-filerna i /bibstat/libstat/templates/base/ (admin.html resp. admin-survey.html) kan du välja att använda de
minifierade filerna eller original-filerna. 
Detta gör du genom att ta bort eller lägga till ".min" efter både css-filen och javascript-filen
(t.ex.: i produktion används `/static/css/bundle.min.css` och under utveckling kan `/static/css/bundle.css` användas
för att slippa bygga om mellan uppdateringar).


## Testning

Testerna kan köras genom att använda följande kommando.
Både enhetstesterna och integrationstesterna kommer köras.

	python manage.py test

## Deploy

Se https://github.com/libris/devops (skyddat repo).

**Sökvägar**  
Konfiguration för Django: `/data/appl/config/bibstat_local.py`.  
Konfiguration för Apache: `/etc/httpd/conf.d/bibstat.conf`.  
Felmeddelanden loggas till: `/var/log/httpd/bibstat-error_log`.  
Inkommande requests loggas till: `/var/log/httpd/bibstat-access_log`.

Varje deploy får en egen tids- och datumstämplad mapp i `/data/appl/`.  
Den senaste versionen som används länkas in till `/data/appl/bibstat`.  
Tidigare versioner tas inte bort automatiskt, utan måste tas bort manuellt.

**Backup**
En separat backup av databasen görs varje dag klockan 18.00 med Cron.  
Dessa sparas på en nätverksvolym, som har monterats under `/backup`.  
Använd `crontab -l` för att visa det cron-jobb som används för detta.

**Setup**  
Det finns en [sammanfattning](docs/servers.md) av hur miljöerna sattes upp.

## Import

**Termer**  
Tidigare års statistiktermer kan importeras på följande sett.  
Filerna finns att hitta i projektkatalogen [`data/variables`](data/variables).

	python manage.py import_variables --file=data/variables/folk_termer.xlsx --target_group=folkbib	
	python manage.py import_variables --file=data/variables/forsk_termer.xlsx --target_group=specbib
	python manage.py import_variables --file=data/variables/skol_termer.xlsx --target_group=skolbib
	python manage.py import_variables --file=data/variables/sjukhus_termer.xlsx --target_group=sjukbib

**Enkäter**  
Tidigare års enkäter med de inlämnade värdena kan importeras på följande sett.  
En exekvering av ett kommando importerar ett års värden för en viss bibliotekstyp.  
Filerna finns på både stage- och produktionsmiljön i `/data/appl/old_bibstat_data`.

	python manage.py import_survey_responses --file=/data/appl/old_bibstat_data/Folkbibliotek.xlsx --target_group=folkbib --year=2013
	python manage.py import_survey_responses --file=/data/appl/old_bibstat_data/Folkbibliotek.xlsx --target_group=folkbib --year=2012
	python manage.py import_survey_responses --file=/data/appl/old_bibstat_data/Folkbibliotek.xlsx --target_group=folkbib --year=2011
	python manage.py import_survey_responses --file=/data/appl/old_bibstat_data/Folkbibliotek.xlsx --target_group=folkbib --year=2010

### Export
Export av enkäter till excelfil kan göras via administrationssidan [/surveys](https://bibstat.kb.se/surveys). Det öppna datat kan också exporteras till excelfil under "Öppna data". Då kommer enbart observationer med för variabler som är publika.

Script för export finns även under [libstat/management/commands]([libstat/management/commands).

För att ta ut enkäter:

	python manage.py export_surveys_to_excel --year=2014

För att ta ut data om biblioteken (ange all=y för att ta ut alla bibliotek, eller all=n för att endast få med bibliotek som saknar sigel):

	python manage.py export_libraries_to_excel --year=2012 --all=n
	
I servermiljöerna måste man aktivera virtuell env genom 
    
    cd /data/appl/bibstat
    source env/bin/activate
    
För att köra script som bakgrundsprocess:
    
    nohup python manage.py export_surveys_to_excel --year=2014 &
	
Filerna hamnar under [data/excel_exports] (data/excel_exports) (under /data/appl/excel_exports på servrarna)

### Uppdatera sigel

Om ett bibliotek bytt sigel kan kommandot `update_sigel` köras för att ändra i Bibstat:

    python manage.py update_sigel --from="GAMMALT_SIGEL" --to="NYTT_SIGEL"

## Analytics

Tjänsten genererar data till Matomo på [http://analytics.kb.se](http://analytics.kb.se).
