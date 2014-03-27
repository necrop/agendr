[program:celeryd]
command=python2.7 {{ PROJECT_DIR }}/manage.py celeryd -l info

[program:autoreload]
exclude=true

[program:runserver]
exclude=true

