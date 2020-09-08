# django_events_sourcing
Library that dispatches events based on Django's model Create/Update/Delete
 operations using Nameko Standalone functions.

### Installing

`pip install nameko django-events-sourcing`

### Configuration
Currently it's usage is based on Nameko's Standalone Event Dispatcher so we
 need to configure it:
 
```
# Config to be passed to ClusterRpcProxy
SERVICE_NAME = 'service_name'
NAMEKO_CONFIG = {
    'AMQP_URI': 'amqp://guest:guest@localhost:5672/'
}
```

For usage, add this project to your installed apps:

```
INSTALLED_APPS = [
    ...,
    'django_events_sourcing',
]
```

### Usage
Every model that you want to dispatch an event should be added in the
 settings.py as follows:
 
```
# List of Model and Serializer to be used for the event.
MODELS_CRUD_EVENT = [
    {'model': app.Model1', 
     'serializer': 'app.serializers.Model1Serializer'},
    {'model': 'app.Model2'},
    {'model': 'app.ModelWithStatus', 'status_field': 'status'}
]
```

In the example above, Model1 from app will be serialized using a specific
 serializer while Model2 will be serialized using a ModelSerializer from
  Django RestFramework with all fields included.
  
Now every .save() or .delete() method called for one of this models (except
 for ModelWithStatus explained bellow) will be dispatched as an event with
  the structure:
 ``model_name__created, model_name__updated, model_name__deleted``.
 
If you wish to dispatch different names, you can pass a 'status_field' inside
 the dict with a reference to a field containing a string (usually a
  using a choices attribute). 
  Ex: 
  ```python
class ModelWithStatus(models.Model):
    STATUS_CHOICES = (('started', 'Started'), ('finished', 'Finished'))
    status = models.CharField(max_lenght=200, choices=STATUS_CHOICES)

```
  The dispatcher will use `model_name__[field_value]` for any .save() call
   and `model_name__deleted` when it is deleted.
 
 
 ### Disabling Dispatcher during Tests
 When you run your tests, you usually won't want to dispatch the model events
  registered in your settings.
  
 To disable the dispatcher during your tests, django_events_sourcing provides
  you with a decorator that does that for you. You can disable all or some of
   the registered models using the decorator `disable_dispacher`.
   
   ```python
from django_events_sourcing.testing import disable_dispatcher
from django.test import TestCase

@disable_dispatcher()
class TestSomething(TestCase):
    """This will disable all registered models for all tests inside the class"""

    @disable_dispatcher()
    def test_somethihg(self):
        """It also can be used to decorate only one function."""


@disable_dispatcher(models_list=['app.ModelName'])
class TestSomething(TestCase):
    """This will disable only 'app.ModelName' from being dispatched in all tests
     inside this class."""

    @disable_dispatcher(models_list=['app.ModelName'])
    def test_somethihg(self):
        """It also can be used to decorate only one function."""
        pass
```
