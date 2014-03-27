GEL2 README
===========

Django settings and code are in the /gel2/ directory
SQL dumps are in the /sql/ directory


Python and Django
=================
The application runs on Python 2.7 and Django 1.5. It should be forward-compatible
with future versions of Python 2.x and Django 1.x, but is not guaranteed to be
forwards-compatible with Python 3.x.

The following non-standard Python libraries will need to be installed:
 - Matplotlib 1.2 or above, to support frequency charts;
 - Django-Celery 3.0 or above, Django-Kombu 0.9 or above, and Django-Supervisor 0.3
	or above, to support management of asynchronous jobs.


Settings
========
Filepaths and other settings in settings.py and wsgi.py will need to be changed depending
on where you install the app. Sensitive information like database username and password
has been replaced in settings.py with 'xxx'; this will also need to be replaced with
the appropriate username and password for your database.


Database
========
It's assumed that the database used will be MySQL. However, since the dump files are
SQL, it should be possible to use them to populate any other SQL database, e.g.
PostgreSQL. If so, you'll first need to change the database settings in settings.py
to use the appropriate database engine.

The SQL files used to populate the initial state of the database are in the /sql/
directory. Note that the SQL files only *populate* the database tables; they don't
create the database tables in the first place. To do this you'll need to run Django's
syncdb process:
 - cd into the project directory (the directory containing settings.py and manage.py).
 - Do 'python manage.py syncdb'.
 - Check that the right tables have appeared in your MySQL database; there should
	be 10 tables with names beginning 'gel2_'

Now import the SQL files:
 - cd into the /sql/ directry file 
 - unzip each .zip file: each should unzip to a single file with a .sql extension;
 - first import the ancillary.sql file; this populates the tables for resources
	and topics:
		'mysql -u [user-name] -p -D [database-name] < ancillary.sql'
 - then import the remaining files; these populate the main record tables (entry,
	wordclass, type, frequency tables, and links). These can be done in any order, e.g.
		'mysql -u [user-name] -p -D [database-name] < dump-abc.sql'
where '[user-name]' is your user name and '[database-name]' is the name of the database.
You'll be prompted for your password each time.


Running the app
===============
To run on a local machine:
 - cd into the project directory (the directory containing settings.py and manage.py);
 - Do 'python manage.py runserver';
The application should now be running on http://127.0.0.1:8000/;
go to http://127.0.0.1:8000/projects/gel2 to see the GEL2 homepage.

To run on Apache:
 - edit the Apache httpd.conf file to point to the location of the /gel2/wsgi.py file:
	see https://docs.djangoproject.com/en/1.2/howto/deployment/modwsgi/
 - restart Apache (/apache/bin/start or /apache/bin/restart)
The application should now be running at http://[servername]/projects/gel2



James McCracken 27/05/2013
james.mccracken@fastmail.fm
