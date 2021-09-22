import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '9%%8-rz9+nu+&%0=nf#64g!j2m^=m^r=)(687tvjqq9jm^(ok5'
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'rest_framework',
    'django_events_sourcing',
    'tests.test_app',
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


SERVICE_NAME = 'test_service'
AMQP_URI = 'amqp://guest:guest@localhost:5672/'

MODELS_CRUD_EVENT = [
    {'model': 'test_app.Model1',
     'serializer': 'tests.test_app.serializers.Model1Serializer'},
    {'model': 'test_app.StatusModel', 'status_field': 'status'},
    {'model': 'test_app.StatusModel2', 'status_field': 'state'},
]
