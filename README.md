KB bibstat - Biblioteksstatistiken
==================================

## Förkrav ##

* Python 2.7
* pip och virtualenv
* Mongodb 2.6

### Installera mongodb 2.6 på Red Hat 64 bit ###

Se instruktioner på http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/

1. Skapa en yum konfigurationsfil för mongodb `/etc/yum.repos.d/mongodb.repo` med följande innehåll:

	[mongodb]
	name=MongoDB Repository
	baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/
	gpgcheck=0
	enabled=1

2. Installera senaste mongodb

	$ sudo yum install mongodb-org

3 Konfigurera användare och access för mongodb

För lokala miljöer är det enklast att hoppa över detta steg om man vill kunna köra testerna. 
Annars måste man sätta upp en databasanvändare som har behörighet att skapa och radera databaser.
Glöm inte att ersätta exempellösenorden nedan med riktiga lösenord...

3.1. Skapa admin-användare	

	$ mongo
	$> use admin
	$> db.createUser({user:"admin", pwd:"admin", roles: ["root"]})
	$> db.runCommand({usersInfo:"admin", showPrivileges:true })

3.2. Aktivera autenticering och starta om mongod
	
	$ sudo vi /etc/mongod.conf

Se till att följande rader är avkommenterade:

	bind_ip = 127.0.0.1
	auth = true
	
Starta om mongodb

	$ sudo service mongod restart
	
Testa autenticeringen
	
	$ mongo admin
	$> db.auth("admin", "admin")

3.3. Skapa användare för bibstat (inloggad i mongodb som admin)

	$> use bibstat
	$> db.createUser({user:"bibstat", pwd:"bibstat", roles:["readWrite"]})
	$> db.runCommand({usersInfo:"bibstat", showPrivileges:true })
	
## Skapa lokal Python-miljö ##

Stå i Django-applikationens rotkatalog.

Skapa en virtualenv:

    $ mkvirtualenv bibstat

Installera beroenden:

    $ pip install -r requirements.txt

Skapa lokal settings-fil från exempel. Modifiera sedan settings_local enligt din egen miljö:

    $ cp bibstat/settings_local.py.example bibstat/settings_local.py

Starta server:

	$ python manage.py runserver
	
Skapa superanvändare:
	
	$ python manage.py createsuperuser --username=super --email=noone@example.org 
	passwd: super
    
Läs in statistiktermer (finns incheckade):
	
	$ python manage.py import_variables --file=data/folk_termer.xlsx --target_group=public	
	$ python manage.py import_variables --file=data/forsk_termer.xlsx --target_group=research
	$ python manage.py import_variables --file=data/skol_termer.xlsx --target_group=school
	$ python manage.py import_variables --file=data/sjukhus_termer.xlsx --target_group=hospital

Läs in statistikdata, exempelvis folkbibliotekfil som innehåller åren 2010 t o m 2013 (finns på ...?)
	
	$ python manage.py import_survey_responses --file=/tmp/Folkbiblioteksexport_superfil_20140625_ver2.xlsx --target_group=public --year=2013
	$ python manage.py import_survey_responses --file=/tmp/Folkbiblioteksexport_superfil_20140625_ver2.xlsx --target_group=public --year=2012
	$ python manage.py import_survey_responses --file=/tmp/Folkbiblioteksexport_superfil_20140625_ver2.xlsx --target_group=public --year=2011
	$ python manage.py import_survey_responses --file=/tmp/Folkbiblioteksexport_superfil_20140625_ver2.xlsx --target_group=public --year=2010

### Kör tester ###

	$ python manage.py test libstat


