import os
import sys

from django.core.handlers.wsgi import WSGIHandler

# Not required for development, but required for Webfaction environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'agendr.settings'
application = WSGIHandler()

# Celery stuff
import djcelery
djcelery.setup_loader()
