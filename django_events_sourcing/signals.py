import logging
from importlib import import_module

import re
from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from rest_framework import serializers

from django_events_sourcing.nameko.events import dispatch

logger = logging.getLogger('django')

LOADED_MODELS_DICT = {}
for model_crud_event in settings.MODELS_CRUD_EVENT:
    model = model_crud_event['model']
    serializer = model_crud_event.get('serializer', None)
    dispatch_status_field = model_crud_event.get('status_field', None)

    app, model = model.rsplit('.', 1)
    model = apps.get_app_config(app).get_model(model)
    if serializer:
        serializer_module, serializer = serializer.rsplit('.', 1)
        serializer = getattr(import_module(serializer_module), serializer)
    else:
        serializer = type('NoClassSerializer', (serializers.ModelSerializer,),
                          {'Meta': type('Meta', (), {'model': model,
                                                     'fields': '__all__'})})

    if dispatch_status_field and not hasattr(model, dispatch_status_field):
        raise AttributeError(
            'status_field "{}" not present in "{}" model'.format(
                dispatch_status_field, model))

    LOADED_MODELS_DICT[model] = {'serializer': serializer,
                                 'status_field': dispatch_status_field}


def generic_post_save(sender, instance, created, **kwargs):
    model_data = LOADED_MODELS_DICT.get(sender)
    event_name = re.sub('(?<!^)(?=[A-Z])', '_', sender.__name__).lower()
    if not model_data.get('status_field') and created:
        event_name += '__created'
    elif not model_data.get('status_field'):
        event_name += '__updated'
    else:
        event_name += '__{}'.format(
            getattr(instance, model_data['status_field']))

    serializer_cls = model_data['serializer']
    serializer = serializer_cls(instance=instance)
    dispatch(event_name, serializer.data)


def generic_post_delete(sender, instance, **kwargs):
    model_data = LOADED_MODELS_DICT.get(sender)
    event_name = re.sub('(?<!^)(?=[A-Z])', '_', sender.__name__).lower()
    event_name += '__deleted'
    serializer_cls = model_data['serializer']
    serializer = serializer_cls(instance=instance)
    dispatch(event_name, serializer.data)


for app_model, model_serializer in LOADED_MODELS_DICT.items():
    post_save.connect(generic_post_save, sender=app_model)
    post_delete.connect(generic_post_delete, sender=app_model)
