from django.test.utils import TestContextDecorator

from django_events_sourcing.register import unregister_models, register_models


class disable_dispatcher(TestContextDecorator):
    """
    Decorator that disables any dispatching that would occur using
    django_events_sourcing.
    It can also be used as a context manager using "with" statement.
    """
    def __init__(self, models_list=None, **kwargs):
        self.models_list = models_list
        super().__init__()

    def enable(self):
        unregister_models(self.models_list)

    def disable(self):
        register_models(self.models_list)
