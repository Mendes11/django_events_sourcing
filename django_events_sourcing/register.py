from collections import defaultdict

import threading
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.test.utils import TestContextDecorator

from django_events_sourcing.dispatcher import dispatch_event

_disabled_models = defaultdict(set)

def _register_model_to_signals(model):
    """
    Registers the model to post_save and post_delete Django signals.

    :param model: Django Model object or import path as str
    """
    post_save.connect(generic_post_save, sender=model)
    post_delete.connect(generic_post_delete, sender=model)


def _unregister_model_from_signals(model):
    """
    Unregisters the model from post_save and post_delete Django signals.

    :param model: Django Model object or import path as str.
    """
    post_save.disconnect(generic_post_save, sender=model)
    post_delete.disconnect(generic_post_delete, sender=model)


def unregister_models(models_list=None):
    """
    Unregisters a list of Models from the dispatching events using
    django_events_sourcing.

    If models_list is not empty, it will unregister only those that are
    passed in the argument.

    :param models_config_list: list
    """
    for model_data in settings.MODELS_CRUD_EVENT:
        if models_list and not model_data['model'] in models_list:
            continue
        _unregister_model_from_signals(model_data['model'])


def register_models(models_list=None):
    """
    Registers Models to be able to dispatch events using django_events_sourcing.

    This list should be created in settings file using the setting name of
    MODELS_CRUD_EVENT.

    If models_list is not empty, it will only register those passed in the
    argument.

    :param models_config_list: list
    """
    for model_data in settings.MODELS_CRUD_EVENT:
        if models_list and not model_data['model'] in models_list:
            continue
        _register_model_to_signals(model_data['model'])


class ModelDisabler(TestContextDecorator):
    """
    Decorator that disables any dispatching that would occur for the
    specified model_list.
    """

    def __init__(self, models_list, **kwargs):
        if not isinstance(models_list, list):
            models_list = [models_list]
        self.models_list = models_list
        super().__init__()

    def enable(self):
        global _disabled_models
        _disabled_models[threading.get_ident()].add(*self.models_list)

    def disable(self):
        global _disabled_models
        _disabled_models[threading.get_ident()].remove(*self.models_list)


def model_obj_is_disabled(model_obj):
    global _disabled_models
    disabled_models = _disabled_models[threading.get_ident()]
    if model_obj in disabled_models:
        return True
    return False


disable_model_obj_dispatcher = ModelDisabler


def generic_post_save(sender, instance, created, **kwargs):
    if model_obj_is_disabled(instance):
        return

    action = 'created' if created else 'updated'
    dispatch_event(instance, action=action)


def generic_post_delete(sender, instance, **kwargs):
    if model_obj_is_disabled(instance):
        return
    dispatch_event(instance, action='deleted')