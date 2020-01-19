from django.conf import settings
from django.db.models.signals import post_save, post_delete

from django_events_sourcing.signals import generic_post_save, \
    generic_post_delete


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
