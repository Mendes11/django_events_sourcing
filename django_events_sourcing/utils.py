from django.apps import apps
from django.conf import settings


def load_model_configurations(sender):
    """
    Iterates through setting MODELS_CRUD_EVENT searching for the sender
    model configurations.
    :param sender: Django Model
    :return dict
    """
    for model_config in settings.MODELS_CRUD_EVENT:
        model = model_config['model']
        app, model = model.rsplit('.', 1)
        model = apps.get_app_config(app).get_model(model)
        if sender == model:
            return model_config
    return None # Not found.
