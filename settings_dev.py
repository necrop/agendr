#=======================================================
# Settings in this file override default settings
# in the main settings.py file
#=======================================================

DEBUG = True

DATABASE_ROUTERS = []
DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'agendr',
        'USER': 'root',
        'PASSWORD': 'shapo1MYSQL',
        'HOST': '',
        'PORT': '',
    }
}


# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS = (
    "/home/james/j/code/python/django/agendr/templates",
)

MEDIA_ROOT = '/home/james/j/code/python/django/agendr/uploads/'

STATIC_ROOT = ''

FIXTURE_DIRS = (
    "/home/james/j/work/lex/gel2/fixtures",
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
