import logging
from importlib import import_module

import amqp
import re
from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from nameko.standalone.events import event_dispatcher
from rest_framework import serializers

logger = logging.getLogger('django')

LOADED_MODELS_DICT = {}
for model_crud_event in settings.MODELS_CRUD_EVENT:
    model = model_crud_event[0]
    if len(model_crud_event) == 2:
        serializer = model_crud_event[1]
    else:
        serializer = None
    app, model = model.rsplit('.', 1)
    model = apps.get_app_config(app).get_model(model)
    if serializer:
        serializer_module, serializer = serializer.rsplit('.', 1)
        serializer = getattr(import_module(serializer_module), serializer)
    else:
        serializer = type('NoClassSerializer', (serializers.ModelSerializer,),
                          {'Meta': type('Meta', (), {'model': model,
                                                     'fields': '__all__'})})
    LOADED_MODELS_DICT[model] = serializer


def generic_post_save(sender, instance, created, **kwargs):
    event_name = re.sub('(?<!^)(?=[A-Z])', '_', sender.__name__).lower()
    if created:
        event_name += '__created'
    else:
        event_name += '__updated'
    serializer_cls = LOADED_MODELS_DICT.get(sender)
    serializer = serializer_cls(instance=instance)
    try:
        event_dispatcher(settings.NAMEKO_CONFIG)(settings.SERVICE_NAME,
                                                 event_name, serializer.data)
    except amqp.exceptions.NotFound:
        # TODO It is interesting to force the creation of the exchange in
        #  rabbit even if no one is listening
        pass


def generic_post_delete(sender, instance, **kwargs):
    event_name = re.sub('(?<!^)(?=[A-Z])', '_', sender.__name__).lower()
    event_name += '__deleted'
    serializer_cls = LOADED_MODELS_DICT.get(sender)
    serializer = serializer_cls(instance=instance)
    try:
        event_dispatcher(settings.NAMEKO_CONFIG)(settings.SERVICE_NAME,
                                                 event_name, serializer.data)
    except amqp.exceptions.NotFound:
        # TODO It is interesting to force the creation of the exchange in
        #  rabbit even if no one is listening
        pass


for app_model, model_serializer in LOADED_MODELS_DICT.items():
    post_save.connect(generic_post_save, sender=app_model)
    post_delete.connect(generic_post_delete, sender=app_model)
