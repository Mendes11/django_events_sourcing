from importlib import import_module

import re

from django.conf import settings
from rest_framework import serializers

from django_events_sourcing.utils import load_model_configurations
from django_events_sourcing.senders.kombu import dispatch


def slug_model_name(instance):
    return re.sub('(?<!^)(?=[A-Z])', '_', type(instance).__name__).lower()


def get_event_name(instance, model_data, action):
    event_name = model_data.get("event_name_prefix")
    if event_name is None:
        event_name = slug_model_name(instance)
    if action == 'deleted':
        event_name += '__deleted'
    elif not model_data.get('status_field') and action == 'created':
        event_name += '__created'
    elif not model_data.get('status_field'):
        event_name += '__updated'
    else:
        event_name += '__{}'.format(
            getattr(instance, model_data['status_field']))
    return event_name


def serialize_model(instance, model_data):
    serializer_cls = model_data.get('serializer')
    if serializer_cls:
        serializer_module, serializer = serializer_cls.rsplit('.', 1)
        serializer = getattr(import_module(serializer_module), serializer)
    else:
        serializer = type('NoClassSerializer', (serializers.ModelSerializer,),
                          {'Meta': type('Meta', (), {'model': type(instance),
                                                     'fields': '__all__'})})
    serializer = serializer(instance=instance)
    return serializer.data


def dispatch_event(instance, action):
    model_data = load_model_configurations(type(instance))
    if model_data is None:
        return
    event_name = get_event_name(instance, model_data, action)
    serialized_model = serialize_model(instance, model_data)

    try:
        amqp_uri = settings.AMQP_URI
    except AttributeError:
        # Fall back to old method of getting it
        amqp_uri = settings.NAMEKO_CONFIG.get("AMQP_URI")

    dispatch(
        settings.SERVICE_NAME, event_name, serialized_model, amqp_uri
    )
