# django_events_sourcing
Library that dispatches events based on Django's model Create/Update/Delete
 operations using Nameko Standalone functions.

### Configuration
Currently it's usage is based on Nameko's Standalone Event Dispatcher so we
 need to configure it:
 
```
# Config to be passed to ClusterRpcProxy
SERVICE_NAME = 'service_name'
NAMEKO_CONFIG = {
    'AMQP_URI': config('AMQP_URI',
                       default='amqp://guest:guest@localhost:5672/')
}
```

For usage, add this project to your installed apps:

```
INSTALLED_APPS = [
...,
django_events_sourcing,
]
```

### Usage
Every model that you want to dispatch an event should be added in the
 settings.py as follows:
 
```
# List of Model and Serializer to be used for the event.
MODELS_CRUD_EVENT = [
    ('app.Model1', 'app.serializers.Model1Serializer'),
    ('app.Model2', ),
]
```

In the example above, Model1 from app will be serialized using a specific
 serializer while Model2 will be serialized using a ModelSerializer from
  Django RestFramework with all fields included.
  
Now every .save() or .delete() method called for one of this models will be
 dispatched as an event with the structure:
 ``model_name__created, model_name__updated, model_name__deleted``.
 
